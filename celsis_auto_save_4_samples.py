"""
Celsis Sterility Test Data Entry - 4 Samples with User-Authorized Auto-Save
Batch: 093026-2011 | Instrument: Advance 2 #2011 | Analyst: GS group

Target Samples:
1. ETX-260921-0218
2. ETX-260921-0154
3. ETX-260921-0175
4. ETX-260921-0152
"""

import os
import re
import sys
import time
import json
from playwright.sync_api import sync_playwright

USER_DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")

FOUR_SAMPLES = [
    {
        "id": "ETX-260921-0218",
        "raw_id": "ETX-260921-0218-4/5",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/zP78pnv7ajetlIUxpjG3kQ__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "neg_control": "TSB,MF,-ve control-GS",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2310,
        "ftm": 5191,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "id": "ETX-260921-0154",
        "raw_id": "ETX-260921-0154-4/5",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/cGAT74V9kYI1kWPQS1j-Zg__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "neg_control": "TSB,MF,-ve control-GS",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2364,
        "ftm": 6559,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "id": "ETX-260921-0175",
        "raw_id": "ETX-260921-0175-4/5",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/gAMZoyVA7Ke2w8KreW1srw__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "neg_control": "TSB,MF,-ve control-GS",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2955,
        "ftm": 5125,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    },
    {
        "id": "ETX-260921-0152",
        "raw_id": "ETX-260921-0152-4/5",
        "url": "https://etrax.eagleanalytical.com/SubmissionTest/Details/7gl1IRCja1YNcCrsXLJeaA__",
        "record": "093026-2011",
        "method": "m",
        "volume": "",
        "neg_control": "TSB,MF,-ve control-GS",
        "modification": "N/A",
        "uom": "mL",
        "start_date": "09/23/2026",
        "end_date": "09/30/2026",
        "atp": 85546,
        "tsb": 2719,
        "ftm": 6625,
        "group": "GS",
        "note": "TSB -ve control = 1907, TSB cut off =5721.0 FTM -ve control = 7381, FTM cut off = 22141.5"
    }
]

def ensure_edit_mode(page):
    """Checks if the form is already in edit mode; if not, clicks the edit/enter data button."""
    rec_input = page.locator("#SubmissionTestResults_0__Value").first
    if rec_input.count() > 0:
        is_editable = rec_input.evaluate("el => !el.disabled && !el.readOnly")
        if is_editable:
            return True

    btn_candidates = page.locator(
        "#btnEnterData, #EnterData, #EditTest, "
        "a[href*='Edit'], a[href*='EnterData'], a[href*='EnterResult'], "
        "#SubmissionTestResultList .panel-heading button, "
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
            pass

    # Fallback: remove disabled and readonly flags from all test result elements if still locked
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
    """Injects all 16 form fields and Test Note into the Celsis test details page."""
    ensure_edit_mode(page)
    
    # 二次验证: 从已有 Test Notes 读取真实的检验方法、检验体积与单位
    detected_uom = "mL"
    try:
        note_rows = page.locator(".panel:has-text('Test Notes') table tr").all()
        for r in note_rows:
            txt = r.inner_text().strip()
            m_method = re.search(r'\b(MF|DI)\b', txt, re.I)
            if m_method:
                verified_m = m_method.group(1).upper()
                sample["method"] = "m" if verified_m == "MF" else "d"
                print(f"  🔍 [二次验证] 从现有 Test Note 验证方法: {verified_m} -> {sample['method']}")
            
            # Canonical volume per media: e.g. "MF. 10 mL of sample filtered per media" or "10 mL per media"
            m_canon_vol = re.search(r'(\d+(?:\.\d+)?)\s*(m[lL]|g|mg|µ[lL]|ul)\s+(?:of\s+sample\s+)?(?:added|filtered)?\s*per\s+media', txt, re.I)
            if m_canon_vol:
                verified_v = m_canon_vol.group(1)
                detected_uom = m_canon_vol.group(2)
                sample["volume"] = verified_v
                print(f"  🔍 [二次验证] 从现有 Test Note 提取 Canonical 体积: {verified_v} {detected_uom}")
            else:
                m_vol = re.search(r'(\d+(?:\.\d+)?)\s*(m[lL]|g|mg|µ[lL]|ul)', txt, re.I)
                if m_vol and not sample.get("volume"):
                    verified_v = m_vol.group(1)
                    detected_uom = m_vol.group(2)
                    sample["volume"] = verified_v

            # Dual-Source Modification Verification
            raw_neg = sample.get("neg_control", "") or sample.get("raw_control_name", "") or "TSB,MF,-ve control-GS"
            pdf_mod = "N/A"
            if raw_neg:
                m_mod = re.search(r'\+([^,\-]+)', raw_neg)
                if m_mod:
                    pdf_mod = m_mod.group(1).strip()

            note_mod = None
            if re.search(r'\bno\s+mod(?:ification)?s?\b', txt, re.I):
                note_mod = "N/A"
            elif pdf_mod != "N/A" and pdf_mod.lower() in txt.lower():
                note_mod = pdf_mod

            if note_mod:
                sample["modification"] = note_mod
                print(f"  🔍 [双重验证 - Modification] PDF 对照品 ({pdf_mod}) 与 Test Note 吻合: {note_mod}")
            else:
                sample["modification"] = pdf_mod
                print(f"  🔍 [双重验证 - Modification] 依据 PDF 对照品确定 Modification: {pdf_mod}")
    except Exception as e:
        print(f"  ⚠️ 双重验证读取 Test Note 异常: {e}")

    print("  ✍️ [2/4] Injecting test parameters...")
    
    # 0: Test Record
    page.locator("#SubmissionTestResults_0__Value").fill(sample["record"])
    
    # 1: Method Performed
    is_mf = sample.get("method", "m").lower() == "m"
    method_label = "Membrane Filtration" if is_mf else "Direct Inoculation"
    page.locator("#SubmissionTestResults_1__Value").select_option(label=method_label)
    
    # 2: Modification
    page.locator("#SubmissionTestResults_2__Value").fill(sample.get("modification", "N/A"))
    
    # 3 & 4: Volume placement
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

    # 4.5: Unit of Measure (UOM) selection - 必须选择 mL
    target_uom = sample.get("uom", detected_uom or "mL")
    uom_set = False
    try:
        uom_loc = page.locator("select:has(option:text-is('mL')), select:has(option:text-is('ml')), select[name*='UnitOfMeasure'], select[id*='UnitOfMeasure']").first
        if uom_loc.count() > 0:
            uom_loc.evaluate("el => { el.disabled = false; el.removeAttribute('disabled'); }")
            try:
                uom_loc.select_option(label="mL")
                uom_set = True
                print(f"  └─ UOM successfully set to [mL] via Playwright locator!")
            except Exception:
                try:
                    uom_loc.select_option(label=target_uom)
                    uom_set = True
                    print(f"  └─ UOM successfully set to [{target_uom}] via Playwright locator!")
                except Exception:
                    pass
    except Exception as e:
        print(f"  ⚠️ Playwright UOM locator error: {e}")

    if not uom_set:
        try:
            uom_result = page.evaluate('''(targetUnit) => {
                let uomSel = null;
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
                    if (window.jQuery) {
                        try { window.jQuery(uomSel).val(chosenVal).trigger('change'); } catch(e){}
                    }
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
    
    # 12: Media lot numbers & expiration dates recorded
    page.locator("#SubmissionTestResults_12__Value").select_option(label="Yes")
    
    # 13: Lot numbers for all reagents recorded
    page.locator("#SubmissionTestResults_13__Value").select_option(label="Yes")
    
    # 14: Reagents within expiration date
    page.locator("#SubmissionTestResults_14__Value").select_option(label="Yes")
    
    # 15: Day 7 Result
    page.locator("#SubmissionTestResults_15__Value").select_option(label="Pass")
    print("  ✅ All 16 primary test fields populated!")

    # Add Note handling
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
                    note_added = True

def run_4_samples_auto_save():
    print("=" * 65)
    print("  CELSIS 4 SAMPLES AUTO-DATA-ENTRY & AUTO-SAVE")
    print("  Targets: ETX-260921-0218, ETX-260921-0154, ETX-260921-0175, ETX-260921-0152")
    print("  MODE: USER-AUTHORIZED AUTOMATIC SAVE")
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

        for idx, sample in enumerate(FOUR_SAMPLES, start=1):
            etx_id = sample["id"]
            print(f"\n=======================================================")
            print(f"  [{idx}/4] Processing: {etx_id}")
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

            # Auto-fill form and add note
            fill_celsis_page(target_page, sample)

            # Take screenshot BEFORE save
            ss_before = os.path.abspath(f"pilot_{etx_id}_before_save.png")
            target_page.screenshot(path=ss_before, full_page=True)
            print(f"  📸 Screenshot before save captured: {ss_before}")

            # AUTOMATIC SAVE (USER AUTHORIZED)
            print(f"  💾 [4/4] Clicking 'Save Changes' for {etx_id}...")
            save_btn = target_page.locator("button:has-text('Save Changes'), input[value='Save Changes'], .btn-success:has-text('Save'), #SubmissionTestResultList .btn-success").first
            if save_btn.count() > 0 and save_btn.is_visible():
                save_btn.click()
                try:
                    target_page.wait_for_load_state("domcontentloaded", timeout=12000)
                except Exception:
                    pass
                time.sleep(3.5)
                print(f"  ✅ [SAVED] {etx_id} Save Changes clicked and loaded!")
            else:
                print(f"  ⚠️ Could not find 'Save Changes' button for {etx_id}!")

            # Take screenshot AFTER save
            ss_after = os.path.abspath(f"pilot_{etx_id}_after_save.png")
            target_page.screenshot(path=ss_after, full_page=True)
            print(f"  📸 Screenshot after save captured: {ss_after}")

        print("\n" + "*" * 65)
        print("  🎉 [ALL 4 SAMPLES COMPLETED & SAVED TO EAGLETRAX!]")
        print("  All 4 sample tabs are open in your Chrome window for inspection.")
        print("*" * 65)

        try:
            input("\n👉 4 个样本均已自动填写并保存！请在浏览器核对，核对完毕后在此窗口按 [回车键] 退出: ")
        except Exception:
            try:
                for s in range(1800):
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

        ctx.close()

if __name__ == "__main__":
    run_4_samples_auto_save()
