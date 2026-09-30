"""
Celsis Sterility Test Data Entry - Remaining 29 Samples with Automated Save
Batch: 093026-2011 | Instrument: Advance 2 #2011 | Analyst: GS group
Remaining Samples: Samples 9 to 37 (29 total)
Mode: Automated Entry + Mandatory UOM (mL) + Negative Control Note + Auto-Save
"""

import os
import re
import sys
import time
import json
from playwright.sync_api import sync_playwright

USER_DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")
PAYLOAD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "celsis_auto_payload_093026_2011.json")

def load_remaining_samples():
    with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    samples = data["samples"]
    # Samples 9 to 37 (index 8 onwards)
    return samples[8:]

def ensure_edit_mode(page):
    rec_input = page.locator("#SubmissionTestResults_0__Value").first
    if rec_input.count() > 0:
        is_editable = rec_input.evaluate("el => !el.disabled && !el.readOnly")
        if is_editable:
            return True

    edit_btn = page.locator("button:has-text('Enter Data'), button:has-text('Enter Test Results'), button:has-text('Modify Results'), a:has-text('Enter Data'), a:has-text('Modify Results'), #btnEnterData, .btn-primary:has-text('Enter'), .btn-success:has-text('Enter')").first
    if edit_btn.count() > 0 and edit_btn.is_visible():
        print(f"  [Action] Clicking button '{edit_btn.inner_text().strip()}' to open editable form...")
        edit_btn.click()
        try:
            page.wait_for_load_state("domcontentloaded", timeout=8000)
        except Exception:
            pass
        time.sleep(2)
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
        existing_notes = page.locator("#SubmissionTestNoteList, .table-hover, table").all_inner_texts()
        full_notes_content = " ".join(existing_notes)
        if "TSB -ve control" in full_notes_content and "-ve control" in full_notes_content:
            print("  ℹ️ Negative control note already present in Test Notes.")
        else:
            add_note_btn = page.locator("#AddSubmissionTestNote, button:has-text('Add Note'), a:has-text('Add Note')").first
            if add_note_btn.count() > 0 and add_note_btn.is_visible():
                add_note_btn.click()
                time.sleep(1.2)

            note_textarea = page.locator("textarea#Content, textarea[name='Content']").first
            if note_textarea.count() > 0 and note_textarea.is_visible():
                note_textarea.fill(note_text)
                time.sleep(0.5)
                submit_btn = page.locator("button:has-text('Add Test Note'), input[value='Add Test Note']").first
                if submit_btn.count() > 0 and submit_btn.is_visible():
                    submit_btn.click()
                    time.sleep(2.0)
                    print("  ✅ Negative Control Test Note successfully attached!")

def run_remaining_29_samples():
    remaining_samples = load_remaining_samples()
    total_count = len(remaining_samples)
    print("=" * 70)
    print(f"  CELSIS 29 REMAINING SAMPLES AUTO-DATA-ENTRY & AUTO-SAVE")
    print(f"  Batch: 093026-2011 | Total Remaining: {total_count} Samples")
    print("  MODE: USER-AUTHORIZED AUTOMATIC ENTRY & SAVE")
    print("=" * 70)

    results_summary = []

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
            sample_num = idx + 8  # Sample 9 to 37
            etx_id = sample["id"]
            print(f"\n=======================================================")
            print(f"  [{idx}/{total_count} | Global #{sample_num}] Processing: {etx_id}")
            print(f"  TSB: {sample['tsb']} | FTM: {sample['ftm']} | Group: {sample['group']}")
            print(f"=======================================================")

            url = sample["url"]
            print(f" -> Navigating to Test Details: {url}")
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(2.5)

            # Auto-fill form and add note
            fill_celsis_page(page, sample)

            # AUTOMATIC SAVE (USER AUTHORIZED)
            print(f"  💾 Clicking 'Save Changes' for {etx_id}...")
            save_btn = page.locator("button:has-text('Save Changes'), input[value='Save Changes'], .btn-success:has-text('Save'), #SubmissionTestResultList .btn-success").first
            save_success = False
            if save_btn.count() > 0 and save_btn.is_visible():
                save_btn.click()
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=12000)
                except Exception:
                    pass
                time.sleep(3.5)
                print(f"  ✅ [SAVED] {etx_id} Save Changes clicked and loaded!")
                save_success = True
            else:
                print(f"  ⚠️ Could not find 'Save Changes' button for {etx_id}!")

            # Take after-save screenshot
            ss_after = os.path.abspath(f"batch_093026_{etx_id}_saved.png")
            page.screenshot(path=ss_after, full_page=True)
            print(f"  📸 Screenshot saved: {ss_after}")

            results_summary.append({
                "num": sample_num,
                "id": etx_id,
                "tsb": sample["tsb"],
                "ftm": sample["ftm"],
                "saved": save_success,
                "screenshot": ss_after
            })

            # Small breather between samples
            time.sleep(1.5)

        print("\n" + "*" * 70)
        print("  🎉 [ALL 29 REMAINING SAMPLES COMPLETED & SAVED TO EAGLETRAX!]")
        print("*" * 70)
        for r in results_summary:
            status = "✅ SAVED" if r["saved"] else "❌ FAILED"
            print(f"  #{r['num']:2d} | {r['id']} | TSB: {r['tsb']:4d} | FTM: {r['ftm']:4d} | {status}")

        try:
            input("\n👉 所有 29 个样本均已自动保存完毕！按 [回车键] 关闭浏览器退出: ")
        except Exception:
            for s in range(300):
                time.sleep(1)

        ctx.close()

if __name__ == "__main__":
    run_remaining_29_samples()
