import os
import time
import json
import sys
from playwright.sync_api import sync_playwright

with open("celsis_090926_step2_full_verified.json", "r", encoding="utf-8") as f:
    samples_data = json.load(f)

user_data_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")
output_json = os.path.abspath("celsis_090926_step3_audit_results.json")

print("====================================================", flush=True)
print(f"  EagleTrax Batch DOM Extractor & Auditor ({len(samples_data)} samples)", flush=True)
print(f"  Output file: {output_json}", flush=True)
print("====================================================", flush=True)

# Load existing progress
audit_results = {}
if os.path.exists(output_json):
    try:
        with open(output_json, "r", encoding="utf-8") as f:
            existing = json.load(f)
            for item in existing:
                if item.get("extracted_fields"):
                    audit_results[item["Sample"]] = item
        print(f"Loaded {len(audit_results)} already extracted samples.", flush=True)
    except Exception:
        pass

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        channel="chrome",
        headless=True,
        viewport={"width": 1366, "height": 900}
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()

    for idx, s in enumerate(samples_data, start=1):
        etx = s["Sample"]
        url = s["EagleTrax URL"]

        if etx in audit_results and audit_results[etx].get("extracted_fields"):
            print(f"[{idx}/{len(samples_data)}] {etx} already extracted -> skipping.", flush=True)
            continue

        if not url or url == "N/A" or "http" not in url:
            print(f"[{idx}/{len(samples_data)}] {etx} has no valid URL -> skipping.", flush=True)
            continue

        print(f"[{idx}/{len(samples_data)}] Auditing {etx} (URL: {url})...", flush=True)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            
            # Check if login needed
            if "/account/login" in page.url.lower():
                print(f" -> Session expired at {etx}, stopping.", flush=True)
                break

            # Wait for results or form fields container
            try:
                page.wait_for_selector("#SubmissionTestResultList, #SubmissionTestFormFieldList, input[id*='SubmissionTestResults']", timeout=8000)
            except Exception:
                time.sleep(1)

            # Extract fields via JavaScript
            dom_data = page.evaluate('''() => {
                const res = {
                    results: {},
                    formFields: {},
                    notes: [],
                    status: ''
                };
                
                const statusSel = document.getElementById('TestStatusId');
                if (statusSel) {
                    res.status = statusSel.selectedOptions[0]?.text?.trim() || statusSel.value;
                }
                
                // Extract from SubmissionTestResultList
                document.querySelectorAll('#SubmissionTestResultList .row').forEach(r => {
                    const labelEl = r.querySelector('label, .control-label, .col-xs-4');
                    const input = r.querySelector('input, select, textarea');
                    if (labelEl && input) {
                        const lbl = labelEl.innerText.replace(/[\\*\\:]/g, '').trim();
                        let val = input.value;
                        if (input.tagName.toLowerCase() === 'select' && input.selectedIndex >= 0) {
                            val = input.options[input.selectedIndex]?.text?.trim() || val;
                        }
                        res.results[input.id || lbl] = {
                            label: lbl,
                            id: input.id,
                            value: val,
                            disabled: input.disabled
                        };
                    }
                });

                // Extract notes
                const noteContainer = document.getElementById('SubmissionTestNoteList');
                if (noteContainer) {
                    noteContainer.querySelectorAll('table tbody tr, .note-item').forEach(nr => {
                        const t = nr.innerText.trim();
                        if (t) res.notes.push(t);
                    });
                }

                return res;
            }''')

            # 3-Way Cross-Check against PDF data
            # Check Rule 7: Modifications field (SubmissionTestResults_2__Value)
            mod_field = dom_data["results"].get("SubmissionTestResults_2__Value", {}).get("value", "")
            
            # Check ATP, TSB, FTM values if present
            atp_val = dom_data["results"].get("SubmissionTestResults_8__Value", {}).get("value", "")
            tsb_val = dom_data["results"].get("SubmissionTestResults_9__Value", {}).get("value", "")
            ftm_val = dom_data["results"].get("SubmissionTestResults_10__Value", {}).get("value", "")
            test_rec = dom_data["results"].get("SubmissionTestResults_0__Value", {}).get("value", "")
            method_val = dom_data["results"].get("SubmissionTestResults_1__Value", {}).get("value", "")
            res_val = dom_data["results"].get("SubmissionTestResults_15__Value", {}).get("value", "")

            # Audit flags
            discrepancies = []
            
            # If sample was flagged CV >= 30%
            if s["Audit Status"] != "Negative":
                discrepancies.append(f"CV% Failsafe triggered: {s['Audit Status']}")

            audit_entry = {
                **s,
                "LIMS Current Status": dom_data["status"],
                "LIMS Test Record": test_rec,
                "LIMS Method": method_val,
                "LIMS Modification": mod_field,
                "LIMS ATP": atp_val,
                "LIMS TSB": tsb_val,
                "LIMS FTM": ftm_val,
                "LIMS Result": res_val,
                "Discrepancies": discrepancies,
                "Notes Count": len(dom_data["notes"]),
                "Extracted Notes": dom_data["notes"][:3],
                "extracted_fields": True
            }

            audit_results[etx] = audit_entry
            print(f" -> OK: {etx} | Status: {dom_data['status']} | Mod: '{mod_field}' | TSB: '{tsb_val}' | FTM: '{ftm_val}'", flush=True)

        except Exception as e:
            print(f" -> [ERROR] {etx}: {e}", flush=True)
            audit_results[etx] = {
                **s,
                "Error": str(e),
                "extracted_fields": False
            }

        # Incremental save
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(list(audit_results.values()), f, indent=2)

    print(f"\nAudit complete! {len(audit_results)} samples saved to: {output_json}", flush=True)
    ctx.close()
