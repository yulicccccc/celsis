import os
import sys
import time
import json
import re
import socket
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding="utf-8")

INPUT_FILE = "pdf_samples_summary.json"
OUTPUT_FILE = "celsis_approval_timestamps.json"

parser = argparse.ArgumentParser()
parser.add_argument("--limit", type=int, default=0, help="Limit number of samples (0 = all)")
parser.add_argument("--start", type=int, default=0, help="Start index")
args, _ = parser.parse_known_args()
LIMIT = args.limit
START = args.start

print("=" * 75, flush=True)
print("   EagleTrax Celsis Approval Timestamps Harvester (Persistent Chrome)", flush=True)
if LIMIT > 0:
    print(f"   [TEST MODE] Processing up to {LIMIT} samples (from index {START})", flush=True)
print("=" * 75, flush=True)

def is_port_open(port=9222):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

def get_driver():
    user_home = os.path.expanduser("~")
    chrome_profile_dir = os.path.join(user_home, "chrome_automation_profile")

    if is_port_open(9222):
        try:
            attach_opts = Options()
            attach_opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            d = webdriver.Chrome(options=attach_opts)
            print("🔗 [Session Reused] Connected to existing Chrome on port 9222!", flush=True)
            return d
        except Exception as e:
            print(f"Port 9222 attach info: {e}")

    options = Options()
    options.add_argument(f"--user-data-dir={chrome_profile_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--window-size=1366,900")

    print("🌐 Launching persistent Chrome...", flush=True)
    try:
        d = webdriver.Chrome(options=options)
        return d
    except Exception as e:
        print(f"\n⚠️ Chrome launch error: {e}", flush=True)
        print("👉 Please close any existing automated Chrome window and retry.", flush=True)
        sys.exit(1)

def ensure_login(driver):
    driver.get("https://etrax.eagleanalytical.com/Submission")
    time.sleep(2)
    cur_url = driver.current_url.lower()
    if "/account/login" in cur_url or "microsoft" in cur_url or "login.live" in cur_url:
        print("🔑 Login required. Auto-filling username...", flush=True)
        try:
            u_input = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.ID, "Username"))
            )
            if not u_input.get_attribute("value"):
                u_input.clear()
                u_input.send_keys("qchen")
                print("  -> Auto-filled qchen", flush=True)
            cont_btn = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue'] | //button[contains(text(), 'Continue')]"))
            )
            cont_btn.click()
            print("  -> Clicked Continue", flush=True)
        except Exception:
            pass

        print("👉 Waiting for SSO authentication in browser window...", flush=True)
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
                print(f"✅ Logged in successfully ({int(time.time() - start_l)}s)!", flush=True)
                break
            if time.time() - start_l > 300:
                print("❌ Login timeout.", flush=True)
                sys.exit(1)

        driver.get("https://etrax.eagleanalytical.com/Submission")
        time.sleep(2)

def normalize_sid(sid):
    # Fix common OCR typos in ETX dates
    # e.g. ETX-260621-0536 -> ETX-260821-0536
    m = re.match(r"ET[X|K|R]-(\d{6})-(\d{4})", sid, re.I)
    if m:
        d1, d2 = m.group(1), m.group(2)
        if d1.startswith("2606"):
            d1 = "2608" + d1[4:]
        return f"ETX-{d1}-{d2}"
    return sid

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: {INPUT_FILE} not found. Please ensure sample extraction is complete.")
        sys.exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        pdf_samples_map = json.load(f)

    all_targets = []
    for pdf_path, s_list in pdf_samples_map.items():
        base_name = os.path.basename(pdf_path)
        for s in s_list:
            norm_s = normalize_sid(s)
            all_targets.append({"sample": norm_s, "raw_sample": s, "packet": base_name})

    print(f"Loaded {len(all_targets)} sample entries across {len(pdf_samples_map)} packets.")

    harvested = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
                for r in records:
                    harvested[r["Sample"]] = r
            print(f"Loaded {len(harvested)} already harvested samples from {OUTPUT_FILE}.")
        except Exception:
            pass

    remaining = [t for t in all_targets if t["sample"] not in harvested]
    print(f"Remaining samples to harvest: {len(remaining)}")

    if not remaining:
        print("🎉 All samples already harvested!")
        return

    if START > 0:
        remaining = remaining[START:]

    if LIMIT > 0:
        remaining = remaining[:LIMIT]
        print(f"Applying limit: processing {len(remaining)} samples for this run.")

    driver = get_driver()
    ensure_login(driver)

    try:
        driver.minimize_window()
        print("🪟 Chrome minimized to background for quiet operation.", flush=True)
    except Exception:
        pass

    try:
        for idx, item in enumerate(remaining, 1):
            sid = item["sample"]
            packet = item["packet"]
            print(f"\n[{idx:03d}/{len(remaining):03d}] Searching {sid} ({packet}) ...", flush=True)

            try:
                driver.get("https://etrax.eagleanalytical.com/Submission")
                time.sleep(1.2)

                try:
                    clear_btn = driver.find_element(By.ID, "ClearButton")
                    clear_btn.click()
                    time.sleep(0.3)
                except Exception:
                    pass

                srch_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "srchCriteria"))
                )
                srch_input.clear()
                srch_input.send_keys(sid)
                time.sleep(0.2)

                find_btn = driver.find_element(By.ID, "FindButton")
                find_btn.click()
                time.sleep(1.8)

                # Switch to Tests tab
                try:
                    tests_tab = WebDriverWait(driver, 6).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@href='#SubmissionTests' or contains(text(), 'Tests')]"))
                    )
                    tests_tab.click()
                    time.sleep(1.2)
                except Exception:
                    pass

                # Locate Celsis link via /SubmissionTest/Details/
                all_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/SubmissionTest/Details/')]")
                details_url = None
                test_title = None

                for l in all_links:
                    txt = l.text.strip()
                    if "celsis" in txt.lower():
                        details_url = l.get_attribute("href")
                        test_title = txt
                        break

                # Fallback: if single link or first link
                if not details_url and all_links:
                    for l in all_links:
                        href = l.get_attribute("href")
                        txt = l.text.strip()
                        if "sterility" in txt.lower() or "celsis" in href.lower():
                            details_url = href
                            test_title = txt
                            break

                if not details_url:
                    print(f"  ❌ Could not find Celsis test URL for {sid}")
                    entry = {
                        "Sample": sid,
                        "Packet": packet,
                        "found": False,
                        "error": "URL not found"
                    }
                    harvested[sid] = entry
                    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                        json.dump(list(harvested.values()), f, indent=2, ensure_ascii=False)
                    continue

                print(f"  🔗 Found: {test_title} -> {details_url}")
                driver.get(details_url)
                time.sleep(2.2)

                current_status = ""
                try:
                    status_elem = driver.find_element(By.ID, "TestStatusId")
                    current_status = Select(status_elem).first_selected_option.text.strip()
                except Exception:
                    pass

                event_history = []
                try:
                    table_rows = driver.find_elements(By.XPATH, "//table[contains(., 'Date Performed') or contains(., 'Event')]//tbody//tr")
                    for tr in table_rows:
                        cols = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, "td")]
                        if len(cols) >= 3:
                            event_history.append({
                                "event": cols[0],
                                "date_performed": cols[1],
                                "performed_by": cols[2]
                            })
                except Exception as e:
                    print(f"  ⚠️ Error reading Event History: {e}")

                approved_event = None
                data_review_event = None
                completed_event = None
                results_entered_event = None

                for ev in event_history:
                    ev_name = ev["event"].lower()
                    if "status changed - approved" in ev_name and not approved_event:
                        approved_event = ev
                    elif "status changed - data review" in ev_name and not data_review_event:
                        data_review_event = ev
                    elif "status changed - completed" in ev_name and not completed_event:
                        completed_event = ev
                    elif "entered test results" in ev_name and not results_entered_event:
                        results_entered_event = ev

                entry = {
                    "Sample": sid,
                    "Packet": packet,
                    "found": True,
                    "url": details_url,
                    "current_status": current_status,
                    "approved_time": approved_event["date_performed"] if approved_event else None,
                    "approved_by": approved_event["performed_by"] if approved_event else None,
                    "data_review_time": data_review_event["date_performed"] if data_review_event else None,
                    "data_review_by": data_review_event["performed_by"] if data_review_event else None,
                    "completed_time": completed_event["date_performed"] if completed_event else None,
                    "results_entered_time": results_entered_event["date_performed"] if results_entered_event else None,
                    "total_events_count": len(event_history)
                }

                harvested[sid] = entry
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(list(harvested.values()), f, indent=2, ensure_ascii=False)

                app_str = f"Approved: {entry['approved_time']} by {entry['approved_by']}" if entry['approved_time'] else "Approved: None"
                rev_str = f"Review: {entry['data_review_time']}" if entry['data_review_time'] else "Review: None"
                print(f"  ✅ {sid} | Status=[{current_status}] | {app_str} | {rev_str}", flush=True)

            except Exception as ex:
                print(f"  ❌ Error processing {sid}: {ex}", flush=True)

    finally:
        # Keep Chrome alive in background on port 9222!
        try:
            driver.minimize_window()
        except Exception:
            pass
        print("\n🔒 Chrome session kept alive in background (port 9222, persistent). Never quits!", flush=True)

    print("\n" + "=" * 75, flush=True)
    print(f"🎉 Harvesting run complete! Total records saved: {len(harvested)}", flush=True)
    print(f"Saved to: {OUTPUT_FILE}", flush=True)
    print("=" * 75, flush=True)

if __name__ == "__main__":
    main()
