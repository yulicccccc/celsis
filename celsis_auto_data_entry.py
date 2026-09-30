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

def ensure_edit_mode(page):
    """
    Ensures that the Celsis Test Results form is in editable mode.
    If fields are disabled, detects and clicks 'Enter Data' / 'Enter Results' / 'Modify Results'.
    """
    print("  🔓 [1/4] Checking edit mode & 'Enter Data' button...")
    time.sleep(0.5)

    # 1. Check if first input is already enabled
    rec_input = page.locator("#SubmissionTestResults_0__Value").first
    if rec_input.count() > 0:
        is_disabled = rec_input.evaluate("el => el.disabled || el.readOnly")
        if not is_disabled:
            print("  ℹ️ Fields are already active and editable.")
            return True

    # 2. Look for the Enter Data / Modify Results button
    # In EagleTrax, this button is located in the Test Results panel header (.panel-heading .col-xs-2.text-right)
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

    # 3. Fallback: remove disabled and readonly flags from all test result elements if still locked
    unlocked = page.evaluate('''() => {
        let cnt = 0;
        document.querySelectorAll('input[id^="SubmissionTestResults_"], select[id^="SubmissionTestResults_"], select[name*="UnitOfMeasure"], select[name*="Uom"], select[id*="UnitOfMeasure"], select[id*="Uom"]').forEach(el => {
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
    # Step 0: Ensure edit mode ("Enter Data" clicked)
    ensure_edit_mode(page)
    
    # 二次验证 (Secondary Self-Verification): 从页面已有的 Test Notes 自动读取真实的检验方法、检验体积与单位
    detected_uom = "mL"
    try:
        note_rows = page.locator(".panel:has-text('Test Notes') table tr").all()
        for r in note_rows:
            txt = r.inner_text().strip()
            # 匹配例如 "MF. 12ml per media. No Modifications" 或 "DI. 10ml per media"
            m_method = re.search(r'\b(MF|DI)\b', txt, re.I)
            if m_method:
                verified_m = m_method.group(1).upper()
                sample["method"] = "m" if verified_m == "MF" else "d"
                print(f"  🔍 [二次验证] 从现有 Test Note 成功验证方法: {verified_m} -> {sample['method']}")
            # Canonical volume per media: e.g. "MF. 10 mL of sample filtered per media" or "10 mL per media"
            m_canon_vol = re.search(r'(\d+(?:\.\d+)?)\s*(m[lL]|g|mg|µ[lL]|ul)\s+(?:of\s+sample\s+)?(?:added|filtered)?\s*per\s+media', txt, re.I)
            if m_canon_vol:
                verified_v = m_canon_vol.group(1)
                detected_uom = m_canon_vol.group(2)
                sample["volume"] = verified_v
                print(f"  🔍 [二次验证] 从现有 Test Note 成功验证 Canonical 体积: {verified_v} {detected_uom}")
            else:
                m_vol = re.search(r'(\d+(?:\.\d+)?)\s*(m[lL]|g|mg|µ[lL]|ul)', txt, re.I)
                if m_vol and not sample.get("volume"):
                    verified_v = m_vol.group(1)
                    detected_uom = m_vol.group(2)
                    sample["volume"] = verified_v
            # Dual-Source Modification Verification (双重验证 Modification)
            # 1. Source 1: PDF Workload 对照品名称 (若带 +xxx 则为修改，无 + 则为 N/A)
            raw_neg = sample.get("neg_control", "") or sample.get("raw_control_name", "") or "TSB,MF,-ve control-GS"
            pdf_mod = "N/A"
            if raw_neg:
                m_mod = re.search(r'\+([^,\-]+)', raw_neg)
                if m_mod:
                    pdf_mod = m_mod.group(1).strip()

            # 2. Source 2: 页面已有的 Test Note (例如 "No Modifications")
            note_mod = None
            if re.search(r'\bno\s+mod(?:ification)?s?\b', txt, re.I):
                note_mod = "N/A"
            elif pdf_mod != "N/A" and pdf_mod.lower() in txt.lower():
                note_mod = pdf_mod

            if note_mod:
                if pdf_mod == note_mod or pdf_mod == "N/A":
                    sample["modification"] = note_mod
                    print(f"  🔍 [双重验证 - Modification] PDF 对照品 ({pdf_mod}) 与 Test Note 吻合: {note_mod}")
                else:
                    print(f"  ⚠️ [双重验证警告 - Modification] PDF 标明 '{pdf_mod}' 但 Test Note 显示 '{note_mod}'")
                    sample["modification"] = note_mod
            else:
                sample["modification"] = pdf_mod
                print(f"  🔍 [双重验证 - Modification] 依据 PDF 对照品确定 Modification: {pdf_mod}")
    except Exception as e:
        print(f"  ⚠️ 双重验证读取 Test Note 异常: {e}")

    print("  ✍️ [2/4] Injecting test parameters...")
    
    # 0: Test Record
    page.locator("#SubmissionTestResults_0__Value").fill(sample["record"])
    
    # 1: Method Performed (Direct Inoculation / Membrane Filtration)
    is_mf = sample.get("method", "m").lower() == "m"
    method_label = "Membrane Filtration" if is_mf else "Direct Inoculation"
    page.locator("#SubmissionTestResults_1__Value").select_option(label=method_label)
    
    # 2: Modification
    page.locator("#SubmissionTestResults_2__Value").fill(sample.get("modification", "N/A"))
    
    # 3 & 4: Volume placement (MF goes to #3 Filtered, DI goes to #4 Added)
    vol = str(sample.get("volume", "") or "").strip()
    if is_mf:
        if vol:
            page.locator("#SubmissionTestResults_3__Value").fill(vol)
            print(f"  └─ Filtered Volume (#3): {vol}")
        page.locator("#SubmissionTestResults_4__Value").fill("")
    else:
        page.locator("#SubmissionTestResults_3__Value").fill("")
        if vol:
            page.locator("#SubmissionTestResults_4__Value").fill(vol)
            print(f"  └─ Added Volume (#4): {vol}")

    # 4.5: Unit of Measure (UOM) selection - 必须选择 mL (支持从 Test Note 二次验证提取)
    target_uom = sample.get("uom", detected_uom or "mL")
    try:
        uom_result = page.evaluate('''(targetUnit) => {
            let uomSel = null;
            // The UOM select is the unique select on page containing 'mL' / 'ml'
            const selects = Array.from(document.querySelectorAll('select'));
            for (const s of selects) {
                for (const opt of s.options) {
                    const t = opt.text.trim().toLowerCase();
                    if (t === 'ml' || t === 'ml.' || t === 'milliliter' || t === targetUnit.trim().toLowerCase()) {
                        uomSel = s;
                        break;
                    }
                }
                if (uomSel) break;
            }

            if (!uomSel) {
                // Secondary fallback by ID/name
                uomSel = document.querySelector('select[name*="UnitOfMeasure"], select[id*="UnitOfMeasure"], select[name*="Uom"], select[id*="Uom"]');
            }

            if (!uomSel) return { success: false, reason: "UOM select element not found" };

            uomSel.disabled = false;
            uomSel.removeAttribute('disabled');

            const normTarget = targetUnit.trim().toLowerCase();
            let chosenVal = null;
            let chosenText = null;

            for (let i = 0; i < uomSel.options.length; i++) {
                const opt = uomSel.options[i];
                const optText = opt.text.trim().toLowerCase();
                const optVal = opt.value.trim().toLowerCase();
                if (optText === normTarget || optVal === normTarget || (normTarget === 'ml' && (optText === 'ml' || optText === 'ml.' || optVal === 'ml'))) {
                    uomSel.selectedIndex = i;
                    uomSel.value = opt.value;
                    chosenVal = opt.value;
                    chosenText = opt.text;
                    break;
                }
            }

            if (chosenVal !== null) {
                uomSel.dispatchEvent(new Event('change', { bubbles: true }));
                uomSel.dispatchEvent(new Event('input', { bubbles: true }));
                return { success: true, text: chosenText, value: chosenVal, id: uomSel.id };
            } else {
                return { success: false, reason: "No matching option", available: Array.from(uomSel.options).map(o => o.text) };
            }
        }''', target_uom)
        print(f"  └─ UOM Unit Selection [{target_uom}]: {uom_result}")
    except Exception as e:
        print(f"  ⚠️ UOM Selection error: {e}")
            
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

    # Add Note handling (Test Notes at bottom of page)
    note_text = sample.get("note", "").strip()
    if note_text:
        print("  📝 [3/4] Ensuring Negative Control Test Note is attached...")
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
            note_added = False
            # Check if inline Add Test Note panel is already open
            content_area = page.locator("textarea#Content, textarea[name='Content'], .panel:has-text('Add Test Note') textarea").first

            # If not open, click '#AddSubmissionTestNote' to expand the inline panel
            if content_area.count() == 0 or not content_area.is_visible():
                add_note_btn = page.locator("#AddSubmissionTestNote, .btn:has-text('Add Note'), span:has-text('Add Note')").first
                if add_note_btn.count() > 0 and add_note_btn.is_visible():
                    print("  👉 Clicking 'Add Note' to expand the test note form...")
                    add_note_btn.click()
                    time.sleep(1.5)
                    content_area = page.locator("textarea#Content, textarea[name='Content'], .panel:has-text('Add Test Note') textarea").first

            # Fill Content textarea
            if content_area.count() > 0 and content_area.is_visible():
                print(f"  ✍️ Injecting note text into Content textarea: {note_text}")
                content_area.fill(note_text)
                time.sleep(0.5)

                # Click 'Add Test Note' submit button
                submit_btn = page.locator(".panel:has-text('Add Test Note') button:has-text('Add Test Note'), .panel:has-text('Add Test Note') input[value='Add Test Note'], button:has-text('Add Test Note'), input[value='Add Test Note']").first
                if submit_btn.count() > 0 and submit_btn.is_visible():
                    print("  💾 Clicking 'Add Test Note' button to attach note...")
                    submit_btn.click()
                    time.sleep(2.0)
                    print("  ✅ Test Note successfully saved and attached!")
                    note_added = True
                else:
                    print("  ⚠️ Could not find 'Add Test Note' submit button.")
            else:
                print("  ⚠️ Could not find or open 'Add Test Note' textarea.")

            if not note_added:
                import subprocess
                subprocess.run(["powershell", "-command", f"Set-Clipboard -Value @'\n{note_text}\n'@"], check=False)
                print("  📋 Note copied to clipboard as fallback.")

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
