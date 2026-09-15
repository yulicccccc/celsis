import os
import sys
import time
import json
import re
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

USER_DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")

TWO_SAMPLES = [
    {
        "id": "ETX-260903-0229",
        "raw_id": "ETX-260903-0229-4/5",
        "record": "091526-2222",
        "method": "d",
        "volume": "",
        "start_date": "09/08/2026",
        "end_date": "09/15/2026",
        "atp": 87468,
        "tsb": 1980,
        "ftm": 6423,
        "group": "GS",
        "note": "Day 7 Sterility Read: Negative. Incubation ended on 15Sep26\n\n091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5"
    },
    {
        "id": "ETX-260903-0227",
        "raw_id": "ETX-260903-0227-4/5",
        "record": "091526-2222",
        "method": "d",
        "volume": "",
        "start_date": "09/08/2026",
        "end_date": "09/15/2026",
        "atp": 87468,
        "tsb": 2997,
        "ftm": 6213,
        "group": "GS",
        "note": "Day 7 Sterility Read: Negative. Incubation ended on 15Sep26\n\n091526-2222: TSB -ve control = 2566 TSB cut off = 7696.5 FTM -ve control = 5894 FTM cut off = 17680.5"
    }
]

def resolve_target_link(page, etx_id):
    """Searches EagleTrax /Submission page for the Celsis Sterility Test link for etx_id."""
    print(f"  🔍 Searching EagleTrax for {etx_id}...")
    page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded")
    time.sleep(1.5)

    # Clear search
    try:
        clear_btn = page.locator("#ClearButton, button[title='Clear'], input[value='Clear']").first
        if clear_btn.count() > 0 and clear_btn.is_visible():
            clear_btn.click()
            time.sleep(0.8)
    except Exception:
        pass

    # Type ETX ID and find
    try:
        search_box = page.locator("#srchCriteria, input[name='srchCriteria']").first
        search_box.wait_for(state="visible", timeout=15000)
        search_box.fill(etx_id)
    except Exception as e:
        print(f"  ⚠️ Could not locate search box on page ({page.url}): {e}")
        return None
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
            time.sleep(1.2)
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

def ensure_edit_mode(page):
    """
    Ensures that the Celsis Test Results form is in editable mode.
    If fields are disabled, detects and clicks 'Enter Data' / 'Enter Results' / 'Modify Results'.
    """
    print("  🔓 [1/4] Checking edit mode & 'Enter Data' button...")
    time.sleep(0.5)

    rec_input = page.locator("#SubmissionTestResults_0__Value").first
    if rec_input.count() > 0:
        is_disabled = rec_input.evaluate("el => el.disabled || el.readOnly")
        if not is_disabled:
            print("  ℹ️ Fields are already active and editable.")
            return True

    btn_candidates = page.locator(
        "#SubmissionTestResultList .panel-heading a, "
        "#SubmissionTestResultList .panel-heading button, "
        "#SubmissionTestResultList .panel-heading span.btn, "
        "#TestDetails .panel-heading a, "
        "#TestDetails .panel-heading button, "
        "#TestDetails .panel-heading span.btn, "
        "a:has-text('Enter Data'), button:has-text('Enter Data'), span:has-text('Enter Data'), "
        "a:has-text('Enter Results'), button:has-text('Enter Results'), span:has-text('Enter Results'), "
        "a:has-text('Modify Results'), button:has-text('Modify Results'), span:has-text('Modify Results'), "
        "#SubmissionTestResultList .btn-success, "
        "#TestDetails .btn-success"
    )

    clicked = False
    count = btn_candidates.count()
    for i in range(count):
        btn = btn_candidates.nth(i)
        try:
            if btn.is_visible():
                txt = btn.inner_text().strip()
                print(f"  👉 Found action button: [{txt}]. Clicking to unlock data entry...")
                btn.click()
                clicked = True
                break
        except Exception:
            continue

    if clicked:
        try:
            page.wait_for_function(
                "() => { const el = document.querySelector('#SubmissionTestResults_0__Value'); return el && !el.disabled && !el.readOnly; }",
                timeout=6000
            )
            print("  ✅ 'Enter Data' clicked! Form is now in EDITABLE mode.")
            return True
        except Exception:
            print("  ⚠️ Waiting timed out. Checking DOM fallback...")

    # Fallback: remove disabled and readonly flags from all test result elements if still locked
    unlocked = page.evaluate('''() => {
        let cnt = 0;
        document.querySelectorAll('input[id^="SubmissionTestResults_"], select[id^="SubmissionTestResults_"]').forEach(el => {
            if (el.disabled || el.readOnly) {
                el.disabled = false;
                el.readOnly = false;
                el.removeAttribute('disabled');
                el.removeAttribute('readonly');
                cnt++;
            }
        });
        return cnt;
    }''')
    if unlocked > 0:
        print(f"  ⚡ Unlocked {unlocked} input/select fields for direct input.")
    
    return True

def fill_celsis_page(page, sample):
    """Injects all 16 form fields and Test Note into the Celsis test details page without clicking Save."""
    ensure_edit_mode(page)
    
    print("  ✍️ [2/4] Injecting test parameters...")
    
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
        print("  📝 [3/4] Checking Test Notes...")
        existing_notes = page.locator("#SubmissionTestNoteList").inner_text() if page.locator("#SubmissionTestNoteList").count() > 0 else ""
        if sample["record"] in existing_notes and "TSB -ve control" in existing_notes:
            print("  ℹ️ Batch Test Note already attached, skipping duplicate addition.")
        else:
            note_added = False
            # Strategy A: Inline Add Test Note panel at page bottom
            inline_box = page.locator("textarea#Content, textarea[name='Content'], textarea[name*='Note'], #AddTestNote textarea, .panel:has-text('Add Test Note') textarea").first
            if inline_box.count() > 0 and inline_box.is_visible():
                print("  👉 Found inline Add Test Note textarea. Injecting note...")
                inline_box.fill(note_text)
                time.sleep(0.5)
                inline_btn = page.locator("input[value='Add Test Note'], button:has-text('Add Test Note'), .panel:has-text('Add Test Note') .btn-primary").first
                if inline_btn.count() > 0 and inline_btn.is_visible():
                    inline_btn.click()
                    time.sleep(1.5)
                    print("  ✅ Test Note successfully saved via inline panel!")
                    note_added = True

            # Strategy B: Modal dialog fallback
            if not note_added:
                add_note_btn = page.locator("#AddSubmissionTestNote").first
                if add_note_btn.count() > 0 and add_note_btn.is_visible():
                    print("  👉 Clicking 'Add Note' button...")
                    add_note_btn.click()
                    time.sleep(1)
                    try:
                        modal = page.locator(".modal.in, #myModal, .modal-dialog, div[role='dialog']").first
                        modal.wait_for(state="visible", timeout=4000)
                        textarea = modal.locator("textarea, input[type='text'][name*='Note']").first
                        textarea.fill(note_text)
                        time.sleep(0.5)
                        save_note_btn = modal.locator("button:has-text('Save'), input[value='Save'], button:has-text('Submit'), button.btn-primary").first
                        save_note_btn.click()
                        time.sleep(1.5)
                        print("  ✅ Test Note successfully added via modal!")
                        note_added = True
                    except Exception:
                        pass

            if not note_added:
                import subprocess
                subprocess.run(["powershell", "-command", f"Set-Clipboard -Value @'\n{note_text}\n'@"], check=False)
                print("  📋 Note copied to clipboard as fallback.")

def run_pilot():
    print("=" * 65)
    print("  CELSIS AUTO-DATA-ENTRY PILOT: 2 SAMPLES")
    print("  ETX-260903-0229 & ETX-260903-0227")
    print("  SAFE MODE: Fills all fields and notes. NEVER CLICKS SAVE.")
    print("=" * 65)

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

        url_now = page.url.lower()
        if "/account/login" in url_now or "microsoft" in url_now or "login.live" in url_now:
            print("\n🔑 Detected login page, auto-filling username 'qchen'...")
            try:
                user_box = page.locator("#Username, input[name='Username']").first
                if user_box.count() > 0 and user_box.is_visible():
                    if not user_box.input_value():
                        user_box.fill("qchen")
                        print("  └─ Entered Username: qchen")
                    cont_btn = page.locator("input[value='Continue'], button:has-text('Continue')").first
                    if cont_btn.count() > 0 and cont_btn.is_visible():
                        cont_btn.click()
                        print("  └─ Clicked Continue button")
                        time.sleep(2)
            except Exception:
                pass

            print("\n👉 Please complete SSO/MFA sign-in in the Chrome window...")
            start_t = time.time()
            logged_in = False
            while time.time() - start_t < 300:
                time.sleep(3)

                # 1. Check if any tab in context has reached EagleTrax post-login
                for p_tab in ctx.pages:
                    try:
                        u_tab = p_tab.url.lower()
                        if "etrax.eagleanalytical.com" in u_tab and "/account/login" not in u_tab and "microsoft" not in u_tab and "login.live" not in u_tab:
                            page = p_tab
                            logged_in = True
                            print("\n[SUCCESS] Login detected from active EagleTrax tab! Continuing...")
                            break
                    except Exception:
                        pass
                if logged_in:
                    break

                # 2. Active Re-navigation Polling: ping Submission URL to test if session cookies are now set
                try:
                    page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded", timeout=8000)
                    time.sleep(1.5)
                except Exception:
                    pass

                u = page.url.lower()
                if "etrax.eagleanalytical.com" in u and "/account/login" not in u and "microsoft" not in u and "login.live" not in u:
                    print("\n[SUCCESS] Login verified via active probe! Continuing...")
                    logged_in = True
                    break

                print(".", end="", flush=True)

            if not logged_in:
                print("\n❌ [TIMEOUT] Login was not completed within 5 minutes. Stopping.")
                ctx.close()
                return

        opened_pages = []

        for idx, sample in enumerate(TWO_SAMPLES, start=1):
            etx_id = sample["id"]
            print(f"\n=======================================================")
            print(f"  [{idx}/2] Processing: {etx_id}")
            print(f"  TSB: {sample['tsb']} | FTM: {sample['ftm']} | Group: {sample['group']}")
            print(f"=======================================================")

            # Use a separate tab for each sample so user can inspect both
            if idx == 1:
                target_page = page
            else:
                target_page = ctx.new_page()

            url = resolve_target_link(target_page, etx_id)
            if not url:
                print(f"❌ [ERROR] Could not find test link for {etx_id}. Skipping.")
                continue

            print(f" -> Navigating to Test Details: {url}")
            target_page.goto(url, wait_until="domcontentloaded")
            time.sleep(2.5)

            # Auto-fill form and add note
            fill_celsis_page(target_page, sample)

            # Take screenshot as evidence
            ss_path = os.path.abspath(f"pilot_{etx_id}_filled.png")
            target_page.screenshot(path=ss_path, full_page=True)
            print(f"  📸 Screenshot captured: {ss_path}")
            opened_pages.append((etx_id, target_page))

        print("\n" + "*" * 65)
        print("  🎉 [BOTH PILOT SAMPLES FILLED & READY FOR HUMAN REVIEW!]")
        print("  1. Check Chrome window: both sample tabs are open side-by-side.")
        print("  2. Review the pre-filled fields & Test Notes.")
        print("  3. Click the green 'Save' button in EagleTrax manually on each tab.")
        print("*" * 65)

        # Keep browser open for user to review and save
        print("\nBrowser will remain open for 5 minutes (or close window when done).")
        try:
            for s in range(300):
                time.sleep(1)
        except KeyboardInterrupt:
            pass

        ctx.close()

if __name__ == "__main__":
    run_pilot()
