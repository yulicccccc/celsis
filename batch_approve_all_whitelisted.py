import os
import time
import json
import sys
from playwright.sync_api import sync_playwright

USERNAME = "qchen"
PIN = "1124"

user_data_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")
audit_report_file = os.path.abspath("celsis_090926_final_audit_report.json")
approval_log_file = os.path.abspath("celsis_090926_approval_log.json")

with open(audit_report_file, "r", encoding="utf-8") as f:
    audit_data = json.load(f)

# Whitelist: strictly exclude blocked samples (e.g. CV >= 30%)
whitelisted = [item for item in audit_data if "PASS" in item.get("Audit Result", "")]
blocked = [item for item in audit_data if "BLOCK" in item.get("Audit Result", "")]

print("====================================================", flush=True)
print(f"  EagleTrax Batch Auto-Approval ({len(whitelisted)} Whitelisted Samples)", flush=True)
print(f"  Blocked items: {len(blocked)} ({', '.join(b['Sample'] for b in blocked)})", flush=True)
print("====================================================", flush=True)

# Load existing progress if any
approved_map = {}
if os.path.exists(approval_log_file):
    try:
        with open(approval_log_file, "r", encoding="utf-8") as f:
            existing = json.load(f)
            for item in existing:
                if item.get("approved"):
                    approved_map[item["Sample"]] = item
        print(f"Loaded {len(approved_map)} already approved records.", flush=True)
    except Exception:
        pass

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        channel="chrome",
        headless=False,
        viewport={"width": 1366, "height": 900}
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()

    print(" -> Connecting to EagleTrax...", flush=True)
    page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded")
    time.sleep(3)

    # Check login
    url_now = page.url.lower()
    if "/account/login" in url_now or "microsoft" in url_now or "login.live" in url_now:
        print("\n[ACTION REQUIRED] Please sign in in the Chrome window...", flush=True)
        try:
            u_input = page.locator("input[name='Username'], #Username").first
            if u_input.count() > 0 and not u_input.input_value():
                u_input.fill(USERNAME)
                page.locator("input[type='submit'][value='Continue'], button:has-text('Continue')").first.click()
                print(" -> Auto-filled username and clicked Continue.", flush=True)
        except Exception:
            pass

        start_time = time.time()
        while True:
            time.sleep(4)
            elapsed = int(time.time() - start_time)
            try:
                page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded", timeout=10000)
                time.sleep(2)
            except Exception:
                pass
            u = page.url.lower()
            if "/account/login" not in u and "microsoft" not in u and "login.live" not in u:
                print(f"[SUCCESS] Login detected after {elapsed}s!", flush=True)
                break
            if elapsed > 300:
                print("[TIMEOUT] Login timeout after 5 minutes.", flush=True)
                ctx.close()
                sys.exit(1)

    for idx, item in enumerate(whitelisted, start=1):
        etx = item["Sample"]
        url = item["EagleTrax URL"]

        if etx in approved_map and approved_map[etx].get("approved"):
            print(f"[{idx}/{len(whitelisted)}] {etx} already approved -> skipping.", flush=True)
            continue

        print(f"\n[{idx}/{len(whitelisted)}] Processing {etx} (URL: {url})...", flush=True)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            time.sleep(2)

            status_select = page.wait_for_selector("#TestStatusId", timeout=15000)
            current_status = status_select.evaluate("el => el.selectedOptions[0]?.text?.trim() || el.value")
            print(f"  └─ Current status: {current_status}", flush=True)

            if current_status.lower() in ["approved", "completed"]:
                print(f"  └─ Already {current_status}! Skipping approval.", flush=True)
                approved_map[etx] = {**item, "approved": True, "status": current_status}
            else:
                # Select Approved
                status_select.select_option(label="Approved")
                time.sleep(0.8)

                # Fill credentials
                page.wait_for_selector("#AUN", timeout=10000).fill(USERNAME)
                page.wait_for_selector("#APD", timeout=10000).fill(PIN)
                time.sleep(0.4)

                # Save
                save_btn = page.wait_for_selector("#ChangeTestStatusSaveButton", timeout=10000)
                save_btn.click()
                time.sleep(3)

                # Wait for save button to hide
                try:
                    page.wait_for_selector("#ChangeTestStatusSaveButton", state="hidden", timeout=10000)
                except Exception:
                    pass

                # Verify updated status
                page.goto(url, wait_until="domcontentloaded")
                time.sleep(1.5)
                final_status = page.locator("#TestStatusId").evaluate("el => el.selectedOptions[0]?.text?.trim() || el.value")
                print(f"  └─ ✅ Updated to: {final_status}", flush=True)
                approved_map[etx] = {**item, "approved": True, "status": final_status}

        except Exception as e:
            print(f"  └─ ⚠️ Error on {etx}: {e}", flush=True)
            approved_map[etx] = {**item, "approved": False, "error": str(e)}

        # Save progress after each sample
        with open(approval_log_file, "w", encoding="utf-8") as f:
            json.dump(list(approved_map.values()), f, indent=2)

    print(f"\n====================================================", flush=True)
    print(f"  Batch approval finished! Log saved to: {approval_log_file}", flush=True)
    print("====================================================", flush=True)
    ctx.close()
