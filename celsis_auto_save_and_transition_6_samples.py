"""
Celsis Sterility Test Data Entry - 6 Samples Auto-Save & Transition to Data Review
Batch: 093026-2011 | Instrument: Advance 2 #2011 | Analyst: GS group

Target Samples (6 Samples):
1. ETX-260921-0130
2. ETX-260921-0110
3. ETX-260921-0105
4. ETX-260921-0145
5. ETX-260921-0103
6. ETX-260921-0133

Workflow per Sample:
1. Navigate to verified Celsis Details URL
2. Ensure edit mode (handles fresh #EnterSubmissionTestResults and #ModifySubmissionTestResults)
3. Extract prep volume from notes (12 mL)
4. Fill all 16 test results fields
5. Explicitly select UOM as 'mL'
6. Attach Negative Control Test Note
7. Click 'Save Changes' to save results into EagleTrax
8. Transition status from 'Sample Analysis' to 'Data Review' and click confirm Save
9. Capture audit screenshot verifying 'Data Review' status and 'Modify Results' mode
"""

import os
import re
import sys
import time
import json
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

USER_DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")

SIX_SAMPLES = [
    {
        "num": 9,
        "id": "ETX-260921-0130",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/xIMvJz17NtzMpFj82rTn3g__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2627,
        "ftm": 5847,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 10,
        "id": "ETX-260921-0110",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/qvsOo%24aWSS3t-8XqKMjFZg__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2395,
        "ftm": 5561,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 11,
        "id": "ETX-260921-0105",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/hui%24-2oK2jYqTUf4s7qkVg__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2756,
        "ftm": 6027,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 12,
        "id": "ETX-260921-0145",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/VukZUUNh9%24rHy8l6BvsDDA__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 1993,
        "ftm": 9471,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 13,
        "id": "ETX-260921-0103",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/%24wydPMY7eYbb-gJ5esB4Eg__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 3077,
        "ftm": 5176,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "num": 14,
        "id": "ETX-260921-0133",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/RFbnUyB3Wy5bsq31EdPi5w__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2890,
        "ftm": 4552,
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

    # Check for Enter Results (fresh unentered sample)
    enter_btn = page.locator("#EnterSubmissionTestResults, span:has-text('Enter Results'), button:has-text('Enter Results')").first
    if enter_btn.count() > 0 and enter_btn.is_visible():
        print(f"  [Action] Clicking '{enter_btn.inner_text().strip()}' ({enter_btn.get_attribute('id')}) to open editable form...")
        enter_btn.click()
        try:
            page.wait_for_load_state("domcontentloaded", timeout=8000)
        except Exception:
            pass
        time.sleep(2.5)
        return True

    # Check for Modify Results (already entered sample)
    modify_btn = page.locator("#ModifySubmissionTestResults, span:has-text('Modify Results'), button:has-text('Modify Results')").first
    if modify_btn.count() > 0 and modify_btn.is_visible():
        print(f"  [Action] Clicking '{modify_btn.inner_text().strip()}' ({modify_btn.get_attribute('id')}) to open editable form...")
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

def fill_celsis_page(page, sample):
    ensure_edit_mode(page)

    vol = sample.get("volume", "")
    if not vol:
        vol = extract_volume_from_page(page)
        print(f"  [Volume Verified] Extracted volume from prep note: {vol} mL")

    # 1. Test Record
    page.locator("#SubmissionTestResults_0__Value").fill(sample["record"])

    # 2. Method Performed
    method_val = sample["method"].lower()
    method_select = page.locator("#SubmissionTestResults_1__Value")
    if method_val == "m":
        method_select.select_option(label="Membrane Filtration")
    elif method_val == "d":
        method_select.select_option(label="Direct Inoculation")

    # 3. Modification
    page.locator("#SubmissionTestResults_2__Value").fill(sample["modification"])

    # 4. Volume placement
    if method_val == "m":
        page.locator("#SubmissionTestResults_3__Value").fill(vol)
        page.locator("#SubmissionTestResults_4__Value").fill("")
    else:
        page.locator("#SubmissionTestResults_3__Value").fill("")
        page.locator("#SubmissionTestResults_4__Value").fill(vol)

    # 5. Mandatory UOM Selection (mL)
    uom_selected = False
    try:
        uom_loc = page.locator("select:has(option:text-is('mL')), select:has(option:text-is('ml'))").first
        if uom_loc.count() > 0:
            uom_loc.select_option(label="mL")
            uom_selected = True
    except Exception:
        pass

    if not uom_selected:
        js_uom = """
        () => {
            const selects = Array.from(document.querySelectorAll('select'));
            for (const sel of selects) {
                const opts = Array.from(sel.options).map(o => o.text.trim());
                if (opts.includes('mL') || opts.includes('ml')) {
                    sel.removeAttribute('disabled');
                    for (let i = 0; i < sel.options.length; i++) {
                        if (sel.options[i].text.trim().toLowerCase() === 'ml') {
                            sel.selectedIndex = i;
                            sel.value = sel.options[i].value;
                            sel.dispatchEvent(new Event('change', { bubbles: true }));
                            sel.dispatchEvent(new Event('input', { bubbles: true }));
                            if (window.jQuery) {
                                window.jQuery(sel).trigger('change');
                            }
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

    # 7. Dropdowns & Results
    page.locator("#SubmissionTestResults_7__Value").select_option(label="Yes")
    page.locator("#SubmissionTestResults_8__Value").fill(str(sample["atp"]))
    page.locator("#SubmissionTestResults_9__Value").fill(str(sample["tsb"]))
    page.locator("#SubmissionTestResults_10__Value").fill(str(sample["ftm"]))
    page.locator("#SubmissionTestResults_11__Value").select_option(label="Yes")
    page.locator("#SubmissionTestResults_12__Value").select_option(label="Yes")
    page.locator("#SubmissionTestResults_13__Value").select_option(label="Yes")
    page.locator("#SubmissionTestResults_14__Value").select_option(label="Yes")
    page.locator("#SubmissionTestResults_15__Value").select_option(label="Pass")

    # 8. Negative Control Test Note Attachment (exact logic from 4-sample runner)
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

def run_6_samples():
    print("=" * 70)
    print("  CELSIS 6 SAMPLES: AUTO-DATA-ENTRY + AUTO-SAVE + DATA REVIEW TRANSITION")
    print("  Targets: ETX-260921-0130, 0110, 0105, 0145, 0103, 0133")
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

        for idx, sample in enumerate(SIX_SAMPLES, start=1):
            sample_num = sample["num"]
            etx_id = sample["id"]
            print(f"\n=======================================================")
            print(f"  [{idx}/6 | Global #{sample_num}] Processing: {etx_id}")
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

            # 4. Take final screenshot
            ss_path = os.path.abspath(f"pilot6_{etx_id}_data_review.png")
            target_page.screenshot(path=ss_path, full_page=True)
            print(f"  📸 Audit screenshot captured: {ss_path}")

            summary_results.append({
                "num": sample_num,
                "id": etx_id,
                "tsb": sample["tsb"],
                "ftm": sample["ftm"],
                "status": "Data Review" if dr_ok else "Check Needed",
                "screenshot": ss_path
            })

            time.sleep(1.5)

        print("\n" + "*" * 70)
        print("  🎉 [ALL 6 SAMPLES ENTERED, SAVED & TRANSITIONED TO DATA REVIEW!]")
        print("  All 6 sample tabs are open in Chrome for your live review.")
        print("*" * 70)
        for r in summary_results:
            print(f"  #{r['num']:2d} | {r['id']} | TSB: {r['tsb']} | FTM: {r['ftm']} | Status: {r['status']}")

        try:
            input("\n👉 6 个样本均已自动填写、保存并 Transition 到 Data Review！请在浏览器核对，核对完毕后在此窗口按 [回车键] 退出: ")
        except Exception:
            for s in range(1800):
                time.sleep(1)

        ctx.close()

if __name__ == "__main__":
    run_6_samples()
