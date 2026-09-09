import os
import time
import json
from playwright.sync_api import sync_playwright

ETX_ID = "ETX-260830-0040"
TARGET_URL = "https://etrax.eagleanalytical.com/SubmissionTest/Details/AZfBY7MUc4mMGrikVnZP2w__"
USERNAME = "qchen"
PIN = "1124"

user_data_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")

print("====================================================", flush=True)
print(f"  EagleTrax Single-Sample Auto-Approve Test: {ETX_ID}", flush=True)
print(f"  Target URL: {TARGET_URL}", flush=True)
print("====================================================", flush=True)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        channel="chrome",
        headless=False,
        viewport={"width": 1366, "height": 900}
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()

    print(f" -> Navigating to: {TARGET_URL}...", flush=True)
    page.goto(TARGET_URL, wait_until="domcontentloaded")
    time.sleep(3)

    # 1. Inspect current status
    status_select = page.wait_for_selector("#TestStatusId", timeout=15000)
    current_status = status_select.evaluate("el => el.selectedOptions[0]?.text?.trim() || el.value")
    print(f" -> Current Status: {current_status}", flush=True)

    if current_status.lower() == "approved":
        print(" -> Sample is ALREADY Approved! No action needed.", flush=True)
        page.screenshot(path="approve_already_done.png")
        ctx.close()
        exit(0)

    # 2. Select 'Approved'
    print(" -> Selecting 'Approved' in status dropdown...", flush=True)
    status_select.select_option(label="Approved")
    time.sleep(1)

    # 3. Wait for Username (#AUN) and PIN (#APD) fields
    print(" -> Waiting for approval authorization fields (#AUN, #APD)...", flush=True)
    aun_field = page.wait_for_selector("#AUN", timeout=10000)
    apd_field = page.wait_for_selector("#APD", timeout=10000)

    print(f" -> Entering Username: {USERNAME}...", flush=True)
    aun_field.fill("")
    aun_field.fill(USERNAME)
    time.sleep(0.3)

    print(" -> Entering PIN: ****...", flush=True)
    apd_field.fill("")
    apd_field.fill(PIN)
    time.sleep(0.5)

    # Screenshot before clicking save
    page.screenshot(path="approve_before_save.png")
    print(" -> Saved screenshot before clicking save: approve_before_save.png", flush=True)

    # 4. Click Save button (#ChangeTestStatusSaveButton)
    print(" -> Clicking Save button (#ChangeTestStatusSaveButton)...", flush=True)
    save_btn = page.wait_for_selector("#ChangeTestStatusSaveButton", timeout=10000)
    save_btn.click()

    # 5. Wait for save to complete
    print(" -> Waiting for save completion...", flush=True)
    time.sleep(3)
    try:
        page.wait_for_selector("#ChangeTestStatusSaveButton", state="hidden", timeout=15000)
        print(" -> Save button hidden, status updated!", flush=True)
    except Exception:
        time.sleep(2)

    # Refresh / check updated status
    page.goto(TARGET_URL, wait_until="domcontentloaded")
    time.sleep(2)
    new_status_select = page.wait_for_selector("#TestStatusId", timeout=10000)
    new_status = new_status_select.evaluate("el => el.selectedOptions[0]?.text?.trim() || el.value")
    print(f" -> VERIFIED NEW STATUS: {new_status}", flush=True)

    page.screenshot(path="approve_after_save.png")
    print(" -> Saved screenshot after save: approve_after_save.png", flush=True)

    if new_status.lower() == "approved":
        print(f"\n[SUCCESS] ETX-260830-0040 successfully APPROVED in EagleTrax!", flush=True)
    else:
        print(f"\n[WARNING] Status is currently: {new_status}", flush=True)

    time.sleep(2)
    ctx.close()
