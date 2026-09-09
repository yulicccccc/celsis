import os
import time
import json
from playwright.sync_api import sync_playwright

TARGET_URL = "https://etrax.eagleanalytical.com/SubmissionTest/Details/yBqejclNPduhlEXTACLBiA__"
ETX_ID = "ETX-260825-0380"
user_data_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'pastdue_playwright_session')
output_json = os.path.abspath("etx_260825_0380_extracted.json")
output_png = os.path.abspath("etx_260825_0380_page.png")

print("====================================================")
print(f"  EagleTrax Details Extractor: {ETX_ID}")
print("====================================================")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        channel="chrome",
        headless=False,
        viewport={'width': 1366, 'height': 900}
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    
    print(f" -> Navigating to: {TARGET_URL}")
    page.goto(TARGET_URL, wait_until="domcontentloaded")
    time.sleep(2)
    
    # Check login
    url_now = page.url.lower()
    if "/account/login" in url_now or "microsoft" in url_now or "login.live" in url_now:
        print("[ACTION REQUIRED] Please complete SSO/MFA in Chrome window...")
        start_t = time.time()
        while time.time() - start_t < 300:
            time.sleep(3)
            u = page.url.lower()
            if "etrax.eagleanalytical.com" in u and "/account/login" not in u and "microsoft" not in u:
                print("\n[SUCCESS] Login verified! Returning to target page...")
                page.goto(TARGET_URL, wait_until="networkidle")
                break
            print(".", end="", flush=True)

    print(" -> Waiting for AJAX dynamic test results to render...")
    # Wait for results or form fields panels to render inside the DOM
    try:
        page.wait_for_selector("#SubmissionTestResultList .panel, #SubmissionTestFormFieldList .panel, input[id*='SubmissionTestResults'], select[id*='SubmissionTestResults']", timeout=25000)
        print(" -> Dynamic result containers detected!")
    except Exception as e:
        print(f" -> Info waiting for panels: {e}")

    time.sleep(3)
    
    # Save full page screenshot
    page.screenshot(path=output_png, full_page=True)
    print(f" -> Saved full-page screenshot to: {output_png}")

    # Extract structured fields
    extracted_data = page.evaluate('''() => {
        const out = {
            header: {},
            results: [],
            formFields: [],
            notes: [],
            statusOptions: [],
            buttons: []
        };
        
        // 1. Header Information
        const header = document.getElementById('SubmissionTestDetailsHeader');
        if (header) {
            out.header.testName = header.querySelector('h3')?.innerText?.trim() || '';
            const statusSel = document.getElementById('TestStatusId');
            if (statusSel) {
                out.header.currentStatus = statusSel.selectedOptions[0]?.text?.trim() || statusSel.value;
                out.header.currentStatusValue = statusSel.value;
                for (const opt of statusSel.options) {
                    out.statusOptions.push({ value: opt.value, text: opt.text.trim(), selected: opt.selected });
                }
            }
            out.header.rawText = header.innerText.trim();
        }

        // Helper to extract fields from a container
        function extractFromContainer(containerId) {
            const container = document.getElementById(containerId);
            if (!container) return [];
            const items = [];
            const rows = container.querySelectorAll('.row');
            for (const r of rows) {
                const labelEl = r.querySelector('label, .control-label, .col-xs-4');
                const label = labelEl ? labelEl.innerText.replace(/[\*\:]/g, '').trim() : '';
                
                // check input, select, textarea
                const input = r.querySelector('input, select, textarea');
                if (input && label) {
                    let val = input.value;
                    let displayVal = val;
                    if (input.tagName.toLowerCase() === 'select') {
                        displayVal = input.selectedIndex >= 0 ? input.options[input.selectedIndex]?.text?.trim() : val;
                    }
                    items.push({
                        label: label,
                        id: input.id,
                        name: input.name,
                        tagName: input.tagName,
                        type: input.type,
                        value: val,
                        displayValue: displayVal,
                        disabled: input.disabled
                    });
                }
            }
            return items;
        }

        // 2. SubmissionTestResultList (ATP, TSB, FTM, Method, Start/End Date, etc.)
        out.results = extractFromContainer('SubmissionTestResultList');

        // 3. SubmissionTestFormFieldList
        out.formFields = extractFromContainer('SubmissionTestFormFieldList');

        // 4. Notes
        const noteContainer = document.getElementById('SubmissionTestNoteList');
        if (noteContainer) {
            const noteRows = noteContainer.querySelectorAll('table tbody tr, .note-item, .row');
            for (const nr of noteRows) {
                const txt = nr.innerText.trim();
                if (txt) out.notes.push(txt);
            }
        }

        // 5. Buttons & Action Links
        document.querySelectorAll('button, input[type="submit"], input[type="button"], a.btn').forEach(b => {
            const txt = b.innerText ? b.innerText.trim() : (b.value || '');
            if (txt) {
                out.buttons.push({
                    text: txt,
                    id: b.id,
                    className: b.className,
                    disabled: b.disabled
                });
            }
        });

        return out;
    }''')

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2)
    print(f" -> Extracted {len(extracted_data['results'])} result fields, {len(extracted_data['formFields'])} form fields, {len(extracted_data['statusOptions'])} status options.")
    print(f" -> Saved clean JSON to: {output_json}")

    time.sleep(2)
    ctx.close()
