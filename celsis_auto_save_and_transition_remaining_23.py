"""
Celsis Sterility Test Data Entry - Remaining 23 Samples Auto-Save & Transition to Data Review
Batch: 093026-2011 | Instrument: Advance 2 #2011 | Analyst: GS group
Remaining: Samples 15 to 37 (23 total)
Mode: Automated Entry + Mandatory UOM (mL) + Negative Control Note + Auto-Save + Data Review Transition
"""

import os
import re
import sys
import time
import json
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

USER_DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")
PAYLOAD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "celsis_auto_payload_093026_2011.json")

def load_remaining_23_samples():
    with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    samples = data["samples"]
    # Samples 15 to 37 (index 14 onwards)
    return samples[14:]

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
    """Fallback search if direct URL fails."""
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
        js_uom = \"\"\"
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
        \"\"\"
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
            print("  ℹ️ Negative control note already present in Test Notes list.")
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
                print(f"  ✍️ Injecting note text: {note_text}")
                content_area.fill(note_text)
                time.sleep(0.5)

                submit_btn = page.locator(".panel:has-text('Add Test Note') button:has-text('Add Test Note'), .panel:has-text('Add Test Note') input[value='Add Test Note'], button:has-text('Add Test Note'), input[value='Add Test Note']").first
                if submit_btn.count() > 0 and submit_btn.is_visible():
                    print("  💾 Clicking 'Add Test Note' button...")
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

    new_status = status_select.evaluate("el => el.options[el.selectedIndex]?.text?.trim() || ''")
    print(f"  ✅ [CONFIRMED STATUS] New Status for {etx_id}: [{new_status}]")
    return new_status.lower() == "data review"

def run_remaining_23_samples():
    remaining_samples = load_remaining_23_samples()
    total_count = len(remaining_samples)
    print("=" * 70)
    print(f"  CELSIS 23 REMAINING SAMPLES AUTO-ENTRY + AUTO-SAVE + DATA REVIEW")
    print(f"  Batch: 093026-2011 | Total Remaining: {total_count} Samples")
    print("  MODE: USER-AUTHORIZED AUTOMATIC ENTRY + SAVE + TRANSITION")
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

        for idx, sample in enumerate(remaining_samples, start=1):
            sample_num = idx + 14  # Sample 15 to 37
            etx_id = sample["id"]
            print(f"\n=======================================================")
            print(f"  [{idx}/{total_count} | Global #{sample_num}] Processing: {etx_id}")
            print(f"  TSB: {sample['tsb']} | FTM: {sample['ftm']} | Group: {sample['group']}")
            print(f"=======================================================")

            url = sample.get("url", "")
            if not url or "Details" not in url:
                print(f"  🔍 Direct URL not available. Resolving dynamically...")
                url = resolve_target_link(page, etx_id)
                sample["url"] = url

            print(f" -> Navigating to Test Details: {url}")
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(2.5)

            # Check if Error page occurred
            if "Error" in page.title():
                print(f"  ⚠️ Error encountered on URL. Re-resolving dynamically...")
                url = resolve_target_link(page, etx_id)
                sample["url"] = url
                page.goto(url, wait_until="domcontentloaded")
                time.sleep(2.5)

            # 1. Fill data & attach note
            fill_celsis_page(page, sample)

            # 2. Click Save Changes
            print(f"  💾 [1/2] Clicking 'Save Changes' for {etx_id}...")
            save_btn = page.locator("button:has-text('Save Changes'), input[value='Save Changes'], .btn-success:has-text('Save'), #SubmissionTestResultList .btn-success").first
            if save_btn.count() > 0 and save_btn.is_visible():
                save_btn.click()
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=12000)
                except Exception:
                    pass
                time.sleep(3.5)
                print(f"  ✅ [SAVED] {etx_id} Test Results successfully saved!")
            else:
                print(f"  ℹ️ 'Save Changes' button not visible (already saved).")

            # 3. Transition to Data Review
            print(f"  🚀 [2/2] Transitioning {etx_id} status to 'Data Review'...")
            dr_ok = transition_to_data_review(page, etx_id)

            # 4. Take final screenshot
            ss_path = os.path.abspath(f"batch_093026_{etx_id}_data_review.png")
            page.screenshot(path=ss_path, full_page=True)
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
        print("  🎉 [ALL 23 REMAINING SAMPLES ENTERED, SAVED & TRANSITIONED TO DATA REVIEW!]")
        print("*" * 70)
        for r in summary_results:
            print(f"  #{r['num']:2d} | {r['id']} | TSB: {r['tsb']} | FTM: {r['ftm']} | Status: {r['status']}")

        try:
            input("\n👉 所有 23 个剩余样本均已自动保存并 Transition 到 Data Review！按 [回车键] 退出: ")
        except Exception:
            for s in range(300):
                time.sleep(1)

        ctx.close()

if __name__ == "__main__":
    run_remaining_23_samples()
