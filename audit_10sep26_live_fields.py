import os
import sys
import time
import json
import re
import socket
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding="utf-8")

LINKS_FILE = "celsis_100926_links.json"
DB_FILE = "celsis_100926_database.json"
AUDIT_OUTPUT = "celsis_100926_final_audit_report.json"

if not os.path.exists(LINKS_FILE) or not os.path.exists(DB_FILE):
    print("Error: Missing database or links file!")
    sys.exit(1)

with open(DB_FILE, "r", encoding="utf-8") as f:
    db = json.load(f)
db_map = {s["Sample"]: s for s in db}

with open(LINKS_FILE, "r", encoding="utf-8") as f:
    links_list = json.load(f)

print("=" * 75)
print(f"  EagleTrax Live Field Auditor for 10SEP26 ({len(links_list)} samples)")
print("=" * 75)

def is_port_open(port=9222):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

user_home = os.path.expanduser("~")
chrome_profile_dir = os.path.join(user_home, "chrome_automation_profile")

if is_port_open(9222):
    try:
        opts = Options()
        opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=opts)
        print("🔗 Connected to existing Chrome on port 9222!", flush=True)
    except Exception:
        opts = Options()
        opts.add_argument(f"--user-data-dir={chrome_profile_dir}")
        opts.add_argument("--profile-directory=Default")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_argument("--window-size=1366,900")
        driver = webdriver.Chrome(options=opts)
        print("🌐 Launched Chrome with automation profile...", flush=True)
else:
    opts = Options()
    opts.add_argument(f"--user-data-dir={chrome_profile_dir}")
    opts.add_argument("--profile-directory=Default")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_argument("--window-size=1366,900")
    driver = webdriver.Chrome(options=opts)
    print("🌐 Launched Chrome with automation profile...", flush=True)

# Load existing progress if any
audit_results = {}
if os.path.exists(AUDIT_OUTPUT):
    try:
        with open(AUDIT_OUTPUT, "r", encoding="utf-8") as f:
            for item in json.load(f):
                if item.get("audited_live"):
                    audit_results[item["Sample"]] = item
        print(f"Loaded {len(audit_results)} already audited samples from {AUDIT_OUTPUT}.", flush=True)
    except Exception:
        pass

try:
    # First check login on EagleTrax
    driver.get("https://etrax.eagleanalytical.com/Submission")
    time.sleep(2)

    cur_url = driver.current_url.lower()
    if "/account/login" in cur_url or "microsoft" in cur_url or "login.live" in cur_url:
        print("🔑 Login required. Auto-filling username...")
        try:
            u_input = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.ID, "Username"))
            )
            if not u_input.get_attribute("value"):
                u_input.clear()
                u_input.send_keys("qchen")
            cont_btn = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue'] | //button[contains(text(), 'Continue')]"))
            )
            cont_btn.click()
        except Exception:
            pass

        print("👉 Waiting for SSO authentication...")
        start_l = time.time()
        while True:
            time.sleep(2)
            now_url = driver.current_url.lower()
            try:
                kmsi = driver.find_elements(By.ID, "KmsiCheckboxField")
                if kmsi and not kmsi[0].is_selected():
                    kmsi[0].click()
                yes_btn = driver.find_elements(By.XPATH, "//input[@id='idSIButton9' or @value='Yes'] | //button[contains(text(), 'Yes')]")
                if yes_btn and yes_btn[0].is_displayed():
                    yes_btn[0].click()
            except Exception:
                pass

            if "eagleanalytical.com" in now_url and "/account/login" not in now_url and "microsoft" not in now_url and "login.live" not in now_url:
                print(f"✅ Logged in successfully ({int(time.time() - start_l)}s)!")
                break
            if time.time() - start_l > 180:
                print("❌ Login timeout.")
                sys.exit(1)

    try:
        driver.minimize_window()
        print("🪟 Minimized Chrome window to background.", flush=True)
    except Exception:
        pass

    for idx, item in enumerate(links_list, 1):
        sid = item["Sample"]
        url = item.get("url")

        if sid in audit_results and audit_results[sid].get("audited_live"):
            print(f"[{idx:02d}/{len(links_list):02d}] {sid} -> already audited", flush=True)
            continue

        if not url or "http" not in url:
            print(f"[{idx:02d}/{len(links_list):02d}] {sid} -> No URL, skipping", flush=True)
            continue

        print(f"[{idx:02d}/{len(links_list):02d}] Auditing {sid} ...", flush=True)
        try:
            driver.get(url)
            time.sleep(1.2)

            # Extract fields via JS
            js_script = """
            const res = {
                status: '',
                results: {},
                notes: []
            };
            const statusSel = document.getElementById('TestStatusId');
            if (statusSel) {
                res.status = statusSel.selectedOptions[0] ? statusSel.selectedOptions[0].text.trim() : statusSel.value;
            }
            document.querySelectorAll('#SubmissionTestResultList .row').forEach(r => {
                const lblEl = r.querySelector('label, .control-label, .col-xs-4');
                const inp = r.querySelector('input, select, textarea');
                if (lblEl && inp) {
                    const lbl = lblEl.innerText.replace(/[\\*\\:]/g, '').trim();
                    let val = inp.value;
                    if (inp.tagName.toLowerCase() === 'select' && inp.selectedIndex >= 0) {
                        val = inp.options[inp.selectedIndex] ? inp.options[inp.selectedIndex].text.trim() : val;
                    }
                    res.results[inp.id || lbl] = {
                        id: inp.id,
                        label: lbl,
                        value: val
                    };
                }
            });
            const noteContainer = document.getElementById('SubmissionTestNoteList');
            if (noteContainer) {
                noteContainer.querySelectorAll('table tbody tr, .note-item').forEach(nr => {
                    const t = nr.innerText.trim();
                    if (t) res.notes.push(t);
                });
            }
            return res;
            """
            dom = driver.execute_script(js_script)

            status_val = dom.get("status", "")
            fields = dom.get("results", {})
            notes = dom.get("notes", [])

            # Extract specific field values
            rec_val = fields.get("SubmissionTestResults_0__Value", {}).get("value", "")
            method_val = fields.get("SubmissionTestResults_1__Value", {}).get("value", "")
            mod_val = fields.get("SubmissionTestResults_2__Value", {}).get("value", "")
            filt_vol = fields.get("SubmissionTestResults_3__Value", {}).get("value", "")
            added_vol = fields.get("SubmissionTestResults_4__Value", {}).get("value", "")
            atp_val = fields.get("SubmissionTestResults_8__Value", {}).get("value", "")
            tsb_val = fields.get("SubmissionTestResults_9__Value", {}).get("value", "")
            ftm_val = fields.get("SubmissionTestResults_10__Value", {}).get("value", "")
            res_val = fields.get("SubmissionTestResults_15__Value", {}).get("value", "")

            # PDF Source Data
            pdf_data = db_map.get(sid, {})
            pdf_inst = pdf_data.get("Instrument", "")
            pdf_atp = str(pdf_data.get("Daily ATP", ""))
            pdf_tsb = str(pdf_data.get("Max TSB RLU", ""))
            pdf_ftm = str(pdf_data.get("Max FTM RLU", ""))
            pdf_cv = pdf_data.get("Max CV%", "")
            pdf_pages = pdf_data.get("Pages", [])

            # Cross-checks & Discrepancies
            discrepancies = []

            # Check Status (Rule 11)
            if status_val != "Data Review":
                discrepancies.append(f"Status is '{status_val}', not 'Data Review'")

            # Check Rule 9: Volume Placement
            if "Membrane" in method_val:
                if not filt_vol:
                    discrepancies.append(f"MF Rule 9 violation: Filtered Volume is empty")
                if added_vol:
                    discrepancies.append(f"MF Rule 9 violation: Added Volume is NOT empty ('{added_vol}')")
            elif "Direct" in method_val:
                if not added_vol:
                    discrepancies.append(f"DI Rule 9 violation: Added Volume is empty")
                if filt_vol:
                    discrepancies.append(f"DI Rule 9 violation: Filtered Volume is NOT empty ('{filt_vol}')")

            # Check Rule 12: Standard Test Note Volume Extraction & Crosscheck
            canonical_vol = None
            for n in notes:
                m_vol = re.search(r'(?:Method:\s*(?:DI|MF)\.\s*)?(\d+(?:\.\d+)?)\s*m[lL]\s+(?:of\s+sample\s+)?(?:added|filtered)\s+per\s+media', n, re.IGNORECASE)
                if m_vol:
                    canonical_vol = m_vol.group(1)
                    break
            
            if canonical_vol:
                current_entered_vol = filt_vol if "Membrane" in method_val else added_vol
                if not current_entered_vol:
                    discrepancies.append(f"Rule 12 violation: Note specifies {canonical_vol} mL per media, but entered volume is empty")
                else:
                    try:
                        if float(current_entered_vol) != float(canonical_vol):
                            discrepancies.append(f"Rule 12 mismatch: Note specifies {canonical_vol} mL per media, but entered volume is '{current_entered_vol}'")
                    except Exception:
                        pass

            # Check ATP
            if atp_val and pdf_atp and atp_val != pdf_atp:
                discrepancies.append(f"ATP mismatch: LIMS='{atp_val}' vs PDF='{pdf_atp}'")

            # Check TSB
            if tsb_val and pdf_tsb and tsb_val != pdf_tsb:
                discrepancies.append(f"TSB mismatch: LIMS='{tsb_val}' vs PDF='{pdf_tsb}'")

            # Check FTM
            if ftm_val and pdf_ftm and ftm_val != pdf_ftm:
                discrepancies.append(f"FTM mismatch: LIMS='{ftm_val}' vs PDF='{pdf_ftm}'")

            # Audit Result
            audit_result = "PASS" if not discrepancies else f"BLOCK ({'; '.join(discrepancies)})"

            audit_entry = {
                "Sample": sid,
                "Instrument": pdf_inst,
                "EagleTrax URL": url,
                "Submission URL": item.get("submission_url"),
                "Titan ID": item.get("titan_id"),
                "PDF ATP": pdf_atp,
                "PDF TSB": pdf_tsb,
                "PDF FTM": pdf_ftm,
                "PDF Max CV%": pdf_cv,
                "PDF Pages": pdf_pages,
                "LIMS Status": status_val,
                "LIMS Test Record": rec_val,
                "LIMS Method": method_val,
                "LIMS Mod": mod_val,
                "LIMS Filtered Volume": filt_vol,
                "LIMS Added Volume": added_vol,
                "LIMS ATP": atp_val,
                "LIMS TSB": tsb_val,
                "LIMS FTM": ftm_val,
                "LIMS Result": res_val,
                "Discrepancies": discrepancies,
                "Audit Result": audit_result,
                "Notes Count": len(notes),
                "Notes": notes[:2],
                "audited_live": True
            }

            audit_results[sid] = audit_entry
            print(f"  -> {audit_result} | Status: {status_val} | Method: {method_val} | ATP: {atp_val} | TSB: {tsb_val} | FTM: {ftm_val}", flush=True)

            with open(AUDIT_OUTPUT, "w", encoding="utf-8") as f:
                json.dump(list(audit_results.values()), f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"  -> ❌ Error on {sid}: {e}", flush=True)

    print("\n" + "=" * 75)
    print(f"🎉 Live Field Audit Complete! {len(audit_results)} samples audited.")
    pass_cnt = sum(1 for a in audit_results.values() if a.get("Audit Result") == "PASS")
    block_cnt = sum(1 for a in audit_results.values() if "BLOCK" in a.get("Audit Result", ""))
    print(f"  • PASS:  {pass_cnt} / {len(links_list)}")
    print(f"  • BLOCK: {block_cnt} / {len(links_list)}")
    print(f"Report saved to: {AUDIT_OUTPUT}")
    print("=" * 75)

finally:
    try:
        driver.quit()
        print("Driver safely closed.", flush=True)
    except Exception:
        pass
