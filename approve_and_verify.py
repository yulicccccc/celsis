import os
import time
from playwright.sync_api import sync_playwright

ETX_ID = "ETX-260830-0040"
TARGET_URL = "https://etrax.eagleanalytical.com/SubmissionTest/Details/AZfBY7MUc4mMGrikVnZP2w__"
USERNAME = "qchen"
PIN = "1124"

user_data_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")

print("====================================================", flush=True)
print(f"  EagleTrax Approval Runner: {ETX_ID}", flush=True)
print(f"  URL: {TARGET_URL}", flush=True)
print("====================================================", flush=True)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        channel="chrome",
        headless=False,
        viewport={"width": 1366, "height": 900}
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()

    print(" -> Navigating to EagleTrax...", flush=True)
    page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded")
    time.sleep(3)

    # Check SSO login
    url_now = page.url.lower()
    if "/account/login" in url_now or "microsoft" in url_now or "login.live" in url_now:
        print("[ACTION REQUIRED] Please complete login in the Chrome window...", flush=True)
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
            if elapsed > 180:
                print("[TIMEOUT] Login timeout.", flush=True)
                ctx.close()
                exit(1)

    # Now open sample detail page
    print(f" -> Opening test details: {TARGET_URL}...", flush=True)
    page.goto(TARGET_URL, wait_until="domcontentloaded")
    time.sleep(3)

    status_select = page.wait_for_selector("#TestStatusId", timeout=15000)
    current_status = status_select.evaluate("el => el.selectedOptions[0]?.text?.trim() || el.value")
    print(f" -> Current Status on Page: {current_status}", flush=True)

    if current_status.lower() == "approved":
        print(f"\n[CONFIRMED] {ETX_ID} is ALREADY APPROVED! 🎉", flush=True)
        page.screenshot(path="etx_0040_approved_confirmed.png")
        ctx.close()
        exit(0)

    # Execute Approval
    print(" -> Selecting 'Approved'...", flush=True)
    status_select.select_option(label="Approved")
    time.sleep(1)

    print(" -> Entering Username and PIN...", flush=True)
    page.wait_for_selector("#AUN", timeout=10000).fill(USERNAME)
    page.wait_for_selector("#APD", timeout=10000).fill(PIN)
    time.sleep(0.5)

    print(" -> Clicking Save button...", flush=True)
    page.wait_for_selector("#ChangeTestStatusSaveButton", timeout=10000).click()

    # Wait for save
    time.sleep(4)
    try:
        page.wait_for_selector("#ChangeTestStatusSaveButton", state="hidden", timeout=15000)
    except Exception:
        pass

    # Verify
    page.goto(TARGET_URL, wait_until="domcontentloaded")
    time.sleep(3)
    final_status = page.locator("#TestStatusId").evaluate("el => el.selectedOptions[0]?.text?.trim() || el.value")
    print(f"\n[FINAL RESULT] Status is now: {final_status}", flush=True)

    page.screenshot(path="etx_0040_approved_confirmed.png")
    print("Saved final screenshot: etx_0040_approved_confirmed.png", flush=True)

    ctx.close()
