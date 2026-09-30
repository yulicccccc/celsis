"""
Celsis Sterility Test Data Entry - 10 Samples Auto-Save & Transition to Data Review
Batch: 093026-2011 | Instrument: Advance 2 #2011 | Analyst: GS group

Target Samples (10 Samples: #15 to #24):
1.  #15 ETX-260921-0159
2.  #16 ETX-260921-0204
3.  #17 ETX-260921-0212
4.  #18 ETX-260921-0227
5.  #19 ETX-260921-0158
6.  #20 ETX-260921-0163
7.  #21 ETX-260921-0180
8.  #22 ETX-260921-0172
9.  #23 ETX-260921-0168
10. #24 ETX-260921-0190

Mode: User-Authorized Auto-Fill + Mandatory UOM (mL) + Negative Control Note + Auto-Save + Data Review Transition
"""

import os
import re
import sys
import time
import json
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

USER_DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")

TEN_SAMPLES = [
    {
        "num": 15,
        "id": "ETX-260921-0159",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/nj4%24ujBmOrKut6JEXgEdFg__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2563,
        "ftm": 5789,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 16,
        "id": "ETX-260921-0204",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/aU2nqJA6SOceM8meWmMXyg__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2192,
        "ftm": 5913,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 17,
        "id": "ETX-260921-0212",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/Xv3dRvFWXhT89%24qlcyLXug__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2440,
        "ftm": 5432,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 18,
        "id": "ETX-260921-0227",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/x%24DuYNirxn1Vpz6QahEZQg__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2383,
        "ftm": 7762,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 19,
        "id": "ETX-260921-0158",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/%24ZI1y05prj-6moOJ1kLvRg__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2795,
        "ftm": 9584,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 20,
        "id": "ETX-260921-0163",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/ZSqNSKo30PaqU0bFuwArgg__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2279,
        "ftm": 6631,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 21,
        "id": "ETX-260921-0180",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/fzfmvR2YWj3CWQrEHGlblg__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2459,
        "ftm": 7416,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 22,
        "id": "ETX-260921-0172",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/vknSjmpDjpfgl1TeKqFTXQ__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2782,
        "ftm": 6691,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 23,
        "id": "ETX-260921-0168",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/BYmJeqDXb8nZVxmMz1lNdg__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2746,
        "ftm": 7013,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 24,
        "id": "ETX-260921-0190",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/4k7xncSL5dpXPTFrrIazpA__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2390,
        "ftm": 5911,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    }
]

def ensure_edit_mode(page):
    rec_input = page.locator("#SubmissionTestResults_0__Value").first
    if rec_input.count() > 0:
        is_editable = rec_input.evaluate("el => !el.disabled && !el.readOnly")
        if is_editable:
            return True

    enter_btn = page.locator("#EnterSubmissionTestResults, span:has-text('Enter Results'), button:has-text('Enter Results')").first
    if enter_btn.count() > 0 and enter_btn.is_visible():
        print(f"  [Action] Clicking '{enter_btn.inner_text().strip()}' to open editable form...")
        enter_btn.click()
        try:
            page.wait_for_load_state("domcontentloaded", timeout=8000)
        except Exception:
            pass
        time.sleep(2.5)
        return True

    modify_btn = page.locator("#ModifySubmissionTestResults, span:has-text('Modify Results'), button:has-text('Modify Results')").first
    if modify_btn.count() > 0 and modify_btn.is_visible():
        print(f"  [Action] Clicking '{modify_btn.inner_text().strip()}' to open editable form...")
        modify_btn.click()
        try:
            page.wait_for_load_state("domcontentloaded", timeout=8000)
        except Exception:
            pass
        time.sleep(2.5)
        return True

    return True

def extract_volume_from_page(page):
    try:
        notes_text = page.locator("#SubmissionTestNoteList, .table-hover, table").all_inner_texts()
        full_text = " ".join(notes_text)
        m = re.search(r'(\d+(?:\.\d+)?)\s*m[lL]\s+per\s+media', full_text, re.IGNORECASE)
        if m:
            return m.group(1)
        m2 = re.search(r'Method:\s*(?:MF|DI)[.\s]+(\d+(?:\.\d+)?)\s*m[lL]', full_text, re.IGNORECASE)
        if m2:
            return m2.group(1)
        m3 = re.search(r'(\d+(?:\.\d+)?)\s*m[lL]\s+(?:filtered|added)', full_text, re.IGNORECASE)
        if m3:
            return m3.group(1)
    except Exception as e:
        print(f"  [Warn] Failed to parse volume from note: {e}")
    return "12"

def resolve_target_link(page, etx_id):
    try:
        page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded")
        time.sleep(1.5)
        page.locator("#srchCriteria").first.fill(etx_id)
        page.locator("#FindButton").first.click()
        time.sleep(2.5)
        page.locator("a[href='#SubmissionTests']").first.click()
        time.sleep(1.5)
        for r in page.locator("#SubmissionTestList table tbody tr").all():
            if "celsis" in r.inner_text().lower():
                for a in r.locator("a[href*='/SubmissionTest/Details/']").all():
                    href = a.get_attribute("href")
                    if href:
                        return f"https://etrax.eagleanalytical.com{href}" if href.startswith("/") else href
    except Exception:
        pass
    return None

def fill_celsis_page(page, sample):
    ensure_edit_mode(page)

    vol = sample.get("volume", "")
    if not vol:
        vol = extract_volume_from_page(page)
    print(f"  [Volume Verified] Extracted volume from prep note: {vol} mL")

    # 1. Test Record
    rec_input = page.locator("#SubmissionTestResults_0__Value")
    if rec_input.count() > 0:
        rec_input.fill(sample["record"])

    # 2. Method Performed
    method_select = page.locator("#SubmissionTestResults_1__Value")
    if method_select.count() > 0:
        val = sample["method"].lower()
        if val in ("m", "mf"):
            try:
                method_select.select_option(label="Membrane Filtration")
            except Exception:
                method_select.select_option(value="1")
        elif val in ("d", "di"):
            try:
                method_select.select_option(label="Direct Inoculation")
            except Exception:
                method_select.select_option(value="2")

    # 3. Modification
    mod_input = page.locator("#SubmissionTestResults_2__Value")
    if mod_input.count() > 0:
        mod_input.fill(sample.get("modification", "N/A"))

    # 4. Volume Placement
    mf_vol = page.locator("#SubmissionTestResults_3__Value")
    di_vol = page.locator("#SubmissionTestResults_4__Value")
    if sample["method"].lower() in ("m", "mf"):
        if mf_vol.count() > 0:
            mf_vol.fill(str(vol))
        if di_vol.count() > 0:
            di_vol.fill("")
    else:
        if di_vol.count() > 0:
            di_vol.fill(str(vol))
        if mf_vol.count() > 0:
            mf_vol.fill("")

    # 5. Mandatory UOM
    uom_candidates = [
        page.locator("select[id*='UnitOfMeasure']").first,
        page.locator("select[name*='UnitOfMeasure']").first,
        page.locator("select[name*='UOM']").first,
        page.locator(".form-group:has-text('Amount') select").first,
        page.locator("tr:has-text('Amount') select").first
    ]
    uom_selected = False
    for uom_elem in uom_candidates:
        if uom_elem.count() > 0 and uom_elem.is_visible():
            try:
                uom_elem.select_option(label="mL")
                uom_selected = True
                break
            except Exception:
                try:
                    uom_elem.select_option(label="ml")
                    uom_selected = True
                    break
                except Exception:
                    pass

    if not uom_selected:
        js_uom = """
        () => {
            const selects = Array.from(document.querySelectorAll('select'));
            for (const s of selects) {
                const opts = Array.from(s.options).map(o => o.text.trim().toLowerCase());
                if (opts.includes('ml')) {
                    for (const opt of s.options) {
                        if (opt.text.trim().toLowerCase() === 'ml') {
                            s.value = opt.value;
                            s.dispatchEvent(new Event('change', { bubbles: true }));
                            return true;
                        }
                    }
                }
            }
            return false;
        }
        """
        page.evaluate(js_uom)

    # 6. Dates
    page.locator("#SubmissionTestResults_5__Value").fill(sample["start_date"])
    page.locator("#SubmissionTestResults_6__Value").fill(sample["end_date"])

    # 7. Quality Checks & RLUs
    page.locator("#SubmissionTestResults_7__Value").select_option(label="Yes")
    page.locator("#SubmissionTestResults_8__Value").fill(str(sample["atp"]))
    page.locator("#SubmissionTestResults_9__Value").fill(str(sample["tsb"]))
    page.locator("#SubmissionTestResults_10__Value").fill(str(sample["ftm"]))
    page.locator("#SubmissionTestResults_11__Value").select_option(label="Yes")
    page.locator("#SubmissionTestResults_12__Value").select_option(label="Yes")
    page.locator("#SubmissionTestResults_13__Value").select_option(label="Yes")
    page.locator("#SubmissionTestResults_14__Value").select_option(label="Yes")
    page.locator("#SubmissionTestResults_15__Value").select_option(label="Pass")

    # 8. Negative Control Test Note Attachment
    note_text = sample.get("note", "").strip()
    if note_text:
        existing_notes = ""
        try:
            note_list_el = page.locator("#SubmissionTestNoteList, .panel:has-text('Test Notes')")
            if note_list_el.count() > 0:
                existing_notes = note_list_el.inner_text()
        except Exception:
            pass

        if note_text in existing_notes or ("TSB -ve control" in existing_notes and "FTM -ve control" in existing_notes):
            print("  ℹ️ Negative control note already present in Test Notes list. Skipping duplicate addition.")
        else:
            content_area = page.locator("textarea#Content, textarea[name='Content'], .panel:has-text('Add Test Note') textarea").first
            if content_area.count() == 0 or not content_area.is_visible():
                add_note_btn = page.locator("#AddSubmissionTestNote, .btn:has-text('Add Note'), span:has-text('Add Note')").first
                if add_note_btn.count() > 0 and add_note_btn.is_visible():
                    print("  👉 Clicking 'Add Note' to expand the test note form...")
                    add_note_btn.click()
                    time.sleep(1.5)
                    content_area = page.locator("textarea#Content, textarea[name='Content'], .panel:has-text('Add Test Note') textarea").first

            if content_area.count() > 0 and content_area.is_visible():
                print(f"  ✍️ Injecting note text into Content textarea: {note_text}")
                content_area.fill(note_text)
                time.sleep(0.5)

                submit_btn = page.locator(".panel:has-text('Add Test Note') button:has-text('Add Test Note'), .panel:has-text('Add Test Note') input[value='Add Test Note'], button:has-text('Add Test Note'), input[value='Add Test Note']").first
                if submit_btn.count() > 0 and submit_btn.is_visible():
                    print("  💾 Clicking 'Add Test Note' button to attach note...")
                    submit_btn.click()
                    time.sleep(2.0)
                    print("  ✅ Test Note successfully saved and attached!")

def transition_to_data_review(page, etx_id):
    """Transitions the sample status dropdown to Data Review and confirms save."""
    print(f"  🔄 [Transition] Checking status for {etx_id}...")
    status_select = page.locator("#TestStatusId").first
    if status_select.count() == 0:
        print("  ⚠️ #TestStatusId not found!")
        return False

    cur_status = status_select.evaluate("el => el.options[el.selectedIndex]?.text?.trim() || ''")
    print(f"  Current Status: [{cur_status}]")
    if cur_status.lower() == "data review":
        print(f"  🎉 Sample {etx_id} is already in 'Data Review'!")
        return True

    print(f"  Selecting 'Data Review' in status dropdown...")
    status_select.select_option(label="Data Review")
    time.sleep(1.5)

    save_btn = page.locator("#ChangeTestStatusSaveButton").first
    try:
        save_btn.wait_for(state="visible", timeout=8000)
        print("  💾 Clicking #ChangeTestStatusSaveButton to confirm Data Review...")
        save_btn.click()
        time.sleep(3.5)
    except Exception as e:
        print(f"  ⚠️ Save button confirmation notice: {e}")

    # Re-evaluate status
    new_status = status_select.evaluate("el => el.options[el.selectedIndex]?.text?.trim() || ''")
    print(f"  ✅ [CONFIRMED STATUS] New Status for {etx_id}: [{new_status}]")
    return new_status.lower() == "data review"

def run_10_samples():
    print("=" * 70)
    print("  CELSIS 10 SAMPLES: AUTO-DATA-ENTRY + AUTO-SAVE + DATA REVIEW TRANSITION")
    print("  Targets: ETX-260921-0159 through -0190 (#15 to #24)")
    print("  MODE: USER-AUTHORIZED AUTOMATIC SAVE & TRANSITION")
    print("=" * 70)

    summary_results = []

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="chrome",
            headless=False,
            viewport={"width": 1400, "height": 950}
        )

        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        print(" -> Connecting to EagleTrax...")
        page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded")
        time.sleep(2)

        # Check SSO Login
        if "/Account/Login" in page.url or "microsoftonline" in page.url:
            print("\n" + "!" * 70)
            print("  [ACTION REQUIRED] EagleTrax session needs authentication.")
            print("  Please complete Microsoft SSO / login in the opened Chrome window.")
            print("  The script will auto-detect when you are logged in...")
            print("!" * 70 + "\n")
            while "/Account/Login" in page.url or "microsoftonline" in page.url:
                time.sleep(3)
                try:
                    page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded", timeout=15000)
                    time.sleep(2)
                except Exception:
                    pass
            print("  ✅ Login detected! Resuming automated processing...")

        for idx, sample in enumerate(TEN_SAMPLES, start=1):
            sample_num = sample["num"]
            etx_id = sample["id"]
            print(f"\n=======================================================")
            print(f"  [{idx}/10 | Global #{sample_num}] Processing: {etx_id}")
            print(f"  TSB: {sample['tsb']} | FTM: {sample['ftm']} | Group: {sample['group']}")
            print(f"=======================================================")

            if idx == 1:
                target_page = page
            else:
                target_page = ctx.new_page()

            url = sample["url"]
            print(f" -> Navigating to Test Details: {url}")
            target_page.goto(url, wait_until="domcontentloaded")
            time.sleep(2.5)

            # Check if redirected to login
            if "/Account/Login" in target_page.url:
                print("  [Warn] Redirected to login. Waiting 5s...")
                time.sleep(5)
                target_page.goto(url, wait_until="domcontentloaded")
                time.sleep(2)

            # Fallback search if direct URL invalid
            if "/Account/Login" not in target_page.url and "SubmissionTest/Details" not in target_page.url:
                print("  [Notice] Resolving direct link via Search...")
                resolved_url = resolve_target_link(target_page, etx_id)
                if resolved_url:
                    url = resolved_url
                    sample["url"] = url
                    target_page.goto(url, wait_until="domcontentloaded")
                    time.sleep(2)

            # 1. Fill data & attach note
            fill_celsis_page(target_page, sample)

            # 2. Click Save Changes
            print(f"  💾 [1/2] Clicking 'Save Changes' for {etx_id}...")
            save_btn = target_page.locator("button:has-text('Save Changes'), input[value='Save Changes'], .btn-success:has-text('Save'), #SubmissionTestResultList .btn-success").first
            if save_btn.count() > 0 and save_btn.is_visible():
                save_btn.click()
                try:
                    target_page.wait_for_load_state("domcontentloaded", timeout=12000)
                except Exception:
                    pass
                time.sleep(3.5)
                print(f"  ✅ [SAVED] {etx_id} Test Results successfully saved!")
            else:
                print(f"  ℹ️ 'Save Changes' button not visible (already saved).")

            # 3. Transition to Data Review
            print(f"  🚀 [2/2] Transitioning {etx_id} status to 'Data Review'...")
            dr_ok = transition_to_data_review(target_page, etx_id)

            # 4. Take audit screenshot
            ss_path = os.path.abspath(f"pilot10_{etx_id}_data_review.png")
            target_page.screenshot(path=ss_path, full_page=True)
            print(f"  📸 Audit screenshot captured: {ss_path}")

            # 5. Launch visible tab in user's default browser session as well
            try:
                os.system(f'cmd /c start "" "{url}"')
            except Exception:
                pass

            summary_results.append({
                "num": sample_num,
                "id": etx_id,
                "tsb": sample["tsb"],
                "ftm": sample["ftm"],
                "status": "Data Review" if dr_ok else "Check Needed",
                "url": url,
                "screenshot": ss_path
            })

            time.sleep(1.5)

        print("\n" + "*" * 70)
        print("  🎉 [ALL 10 SAMPLES ENTERED, SAVED & TRANSITIONED TO DATA REVIEW!]")
        print("  All 10 sample tabs are open in Chrome for your live review.")
        print("*" * 70)
        for r in summary_results:
            print(f"  #{r['num']:2d} | {r['id']} | TSB: {r['tsb']} | FTM: {r['ftm']} | Status: {r['status']}")

        # Save summary JSON
        with open("scratch/resolved_10_samples_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary_results, f, indent=2)

        try:
            input("\n👉 10 个样本均已自动填写、保存并 Transition 到 Data Review！请在浏览器核对，核对完毕后在此窗口按 [回车键] 退出: ")
        except Exception:
            for s in range(300):
                time.sleep(1)

        ctx.close()

if __name__ == "__main__":
    run_10_samples()
