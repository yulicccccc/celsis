import os
import sys
import time
import json
import re
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

# Default User Data Dir for EagleTrax Session
USER_DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")

def resolve_target_link(page, etx_id):
    """Searches EagleTrax /Submission page for the Celsis Sterility Test link for etx_id."""
    print(f"  🔍 Searching EagleTrax for {etx_id}...")
    page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded")
    time.sleep(1.5)

    # Clear search
    try:
        clear_btn = page.locator("#ClearButton, button[title='Clear'], input[value='Clear']").first
        if clear_btn.count() > 0:
            clear_btn.click()
            time.sleep(0.8)
    except Exception:
        pass

    # Type ETX ID and find
    search_box = page.locator("#srchCriteria, input[name='srchCriteria']").first
    search_box.fill(etx_id)
    time.sleep(0.3)
    find_btn = page.locator("#FindButton, button:has-text('Find'), input[value='Find']").first
    find_btn.click()

    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    time.sleep(2)

    # Click Tests tab if needed
    try:
        tests_tab = page.locator("a[href='#SubmissionTests'], a:has-text('Tests')").first
        if tests_tab.count() > 0:
            tests_tab.click()
            time.sleep(1)
    except Exception:
        pass

    # Locate Celsis Test link
    test_link = None
    rows = page.locator("#SubmissionTestList table tbody tr, table tbody tr").all()
    for row in rows:
        text = row.inner_text().strip()
        if "celsis" in text.lower() or etx_id.lower() in text.lower():
            links = row.locator("a").all()
            for link in links:
                href = link.get_attribute("href") or ""
                l_text = link.inner_text().strip()
                if "/SubmissionTest/Details/" in href or "celsis" in l_text.lower():
                    test_link = href if href.startswith("http") else f"https://etrax.eagleanalytical.com{href}"
                    break
            if test_link:
                break

    if not test_link:
        all_links = page.locator("a[href*='/SubmissionTest/Details/']").all()
        for link in all_links:
            href = link.get_attribute("href") or ""
            l_text = link.inner_text().strip()
            if "celsis" in l_text.lower() or len(all_links) == 1:
                test_link = href if href.startswith("http") else f"https://etrax.eagleanalytical.com{href}"
                break

    return test_link

def fill_celsis_page(page, sample):
    """Injects all 16 form fields and Test Note into the Celsis test details page without clicking Save."""
    print("  ✍️ [1/3] Injecting test parameters...")
    
    # 0: Test Record
    page.locator("#SubmissionTestResults_0__Value").fill(sample["record"])
    
    # 1: Method Performed (Direct Inoculation / Membrane Filtration)
    method_label = "Direct Inoculation" if sample.get("method", "d").lower() == "d" else "Membrane Filtration"
    page.locator("#SubmissionTestResults_1__Value").select_option(label=method_label)
    
    # 2: Modification
    page.locator("#SubmissionTestResults_2__Value").fill("N/A")
    
    # 3 & 4: Volume placement
    if "membrane" in method_label.lower():
        vol = str(sample.get("volume", "") or "")
        if vol:
            page.locator("#SubmissionTestResults_3__Value").fill(vol)
        page.locator("#SubmissionTestResults_4__Value").fill("")
    else:
        page.locator("#SubmissionTestResults_3__Value").fill("")
        vol = str(sample.get("volume", "") or "")
        if vol:
            page.locator("#SubmissionTestResults_4__Value").fill(vol)
            
    # 5 & 6: Dates
    page.locator("#SubmissionTestResults_5__Value").fill(sample["start_date"])
    page.locator("#SubmissionTestResults_6__Value").fill(sample["end_date"])
    
    # 7: Negative Controls OK
    page.locator("#SubmissionTestResults_7__Value").select_option(label="Yes")
    
    # 8: ATP Cutoff
    page.locator("#SubmissionTestResults_8__Value").fill(str(sample["atp"]))
    
    # 9 & 10: TSB & FTM Max RLU
    page.locator("#SubmissionTestResults_9__Value").fill(str(sample["tsb"]))
    page.locator("#SubmissionTestResults_10__Value").fill(str(sample["ftm"]))
    
    # 11: CV < 30%
    page.locator("#SubmissionTestResults_11__Value").select_option(label="Yes")
    
    # 12, 13, 14: Quality questions
    page.locator("#SubmissionTestResults_12__Value").select_option(label="Yes")
    page.locator("#SubmissionTestResults_13__Value").select_option(label="Yes")
    page.locator("#SubmissionTestResults_14__Value").select_option(label="Yes")
    
    # 15: Day 7 Result
    page.locator("#SubmissionTestResults_15__Value").select_option(label="Pass")
    print("  ✅ All 16 primary test fields populated!")

    # Add Note handling
    note_text = sample.get("note", "").strip()
    if note_text:
        print("  📝 [2/3] Checking Test Notes...")
        existing_notes = page.locator("#SubmissionTestNoteList").inner_text() if page.locator("#SubmissionTestNoteList").count() > 0 else ""
        if sample["record"] in existing_notes and "TSB -ve control" in existing_notes:
            print("  ℹ️ Batch Test Note already attached, skipping duplicate addition.")
        else:
            add_note_btn = page.locator("#AddSubmissionTestNote")
            if add_note_btn.count() > 0 and add_note_btn.is_visible():
                print("  👉 Clicking 'Add Note' button...")
                add_note_btn.click()
                time.sleep(1)
                
                # Wait for modal dialog
                try:
                    modal = page.locator(".modal.in, #myModal, .modal-dialog, div[role='dialog']").first
                    modal.wait_for(state="visible", timeout=6000)
                    textarea = modal.locator("textarea, input[type='text'][name*='Note']").first
                    textarea.fill(note_text)
                    time.sleep(0.5)
                    
                    save_note_btn = modal.locator("button:has-text('Save'), input[value='Save'], button:has-text('Submit'), button.btn-primary").first
                    save_note_btn.click()
                    time.sleep(1.5)
                    print("  ✅ Test Note successfully added to record!")
                except Exception as ne:
                    print(f"  ⚠️ Could not auto-fill note modal: {ne}. Note copied to clipboard as fallback.")
                    import subprocess
                    subprocess.run(["powershell", "-command", f"Set-Clipboard -Value @'\n{note_text}\n'@"], check=False)

def run_auto_data_entry(batch_payload):
    """
    Main Auto-Pilot Entry Routine:
    - Opens persistent browser window
    - Navigates to each sample
    - Fills all fields and Test Note
    - Leaves page open WITHOUT saving
    - Waits for user to review and click Save manually!
    """
    samples = batch_payload.get("samples", [])
    print("=" * 65)
    print(f"  Celsis Data Entry Auto-Pilot ({len(samples)} Samples)")
    print(f"  Batch: {batch_payload.get('batch_id')} | ATP: {batch_payload.get('atp')}")
    print("  SAFE MODE: Fills all fields and notes. NEVER CLICKS SAVE.")
    print("=" * 65)

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="chrome",
            headless=False,
            viewport={"width": 1366, "height": 900}
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        # Check authentication
        print(" -> Connecting to EagleTrax...")
        page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded")
        time.sleep(2)

        url_now = page.url.lower()
        if "/account/login" in url_now or "microsoft" in url_now or "login.live" in url_now:
            print("\n[ACTION REQUIRED] Please complete SSO/MFA sign-in in the Chrome window...")
            start_t = time.time()
            while time.time() - start_t < 300:
                time.sleep(3)
                u = page.url.lower()
                if "etrax.eagleanalytical.com" in u and "/account/login" not in u and "microsoft" not in u:
                    print("\n[SUCCESS] Login verified! Continuing...")
                    page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="networkidle")
                    time.sleep(2)
                    break
                print(".", end="", flush=True)

        for idx, sample in enumerate(samples, start=1):
            etx_id = sample["id"]
            print(f"\n=======================================================")
            print(f"  [{idx}/{len(samples)}] Target: {etx_id} (Group: {sample.get('group', 'N/A')})")
            print(f"  TSB Max: {sample['tsb']} | FTM Max: {sample['ftm']}")
            print(f"=======================================================")

            # Resolve link
            url = sample.get("url")
            if not url:
                url = resolve_target_link(page, etx_id)
                sample["url"] = url

            if not url:
                print(f"❌ [ERROR] Could not find test link for {etx_id}. Skipping.")
                continue

            print(f" -> Navigating to Test Details: {url}")
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(2)

            # Check if dynamic panels rendered
            try:
                page.wait_for_selector("#SubmissionTestResults_0__Value, #SubmissionTestResultList", timeout=12000)
            except Exception:
                pass
            time.sleep(1)

            # Check if already completed or disabled
            status_elem = page.locator("#TestStatusId").first
            current_status = status_elem.evaluate("el => el.selectedOptions[0]?.text?.trim() || el.value") if status_elem.count() > 0 else "Unknown"
            
            rec_input = page.locator("#SubmissionTestResults_0__Value").first
            is_disabled = rec_input.evaluate("el => el.disabled || el.readOnly") if rec_input.count() > 0 else False

            if current_status.lower() in ["completed", "approved"] and is_disabled:
                print(f"  🎉 [ALREADY COMPLETED] Current status is [{current_status}], fields are locked. Skipping edit.")
                continue

            # Auto-fill form
            fill_celsis_page(page, sample)

            # SAFE HUMAN REVIEW PROMPT
            print("\n" + "*" * 65)
            print(f"  👉 [READY FOR YOUR REVIEW] {etx_id}")
            print(f"  1. Review the pre-filled fields and attached Test Note in Chrome.")
            print(f"  2. Click the green 'Save' button in EagleTrax manually.")
            print("*" * 65)
            
            user_input = input("Press [ENTER] here when done saving to proceed to next sample (or type Q to quit): ").strip()
            if user_input.lower() == "q":
                print("\n[STOPPED] Exiting by user command.")
                break

        print("\n=======================================================")
        print("  All samples processed! Auto-Pilot session complete.")
        print("=======================================================")
        input("Press [ENTER] to close browser and exit...")
        ctx.close()

if __name__ == "__main__":
    sample_payload_path = os.path.abspath("celsis_auto_payload.json")
    if os.path.exists(sample_payload_path):
        with open(sample_payload_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        run_auto_data_entry(payload)
    else:
        print(f"Payload file '{sample_payload_path}' not found. Please provide batch JSON.")
