import os
import time
from playwright.sync_api import sync_playwright

ETX_ID = "ETX-260830-0040"
TARGET_URL = "https://etrax.eagleanalytical.com/SubmissionTest/Details/AZfBY7MUc4mMGrikVnZP2w__"

user_data_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        channel="chrome",
        headless=False,
        viewport={"width": 1366, "height": 900}
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()

    print(" -> Navigating to /Submission...", flush=True)
    page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded")
    time.sleep(3)

    # Check login
    if "/account/login" in page.url.lower():
        print(" -> Auto-filling login...", flush=True)
        try:
            u_input = page.locator("input[name='Username'], #Username").first
            if u_input.count() > 0:
                u_input.fill("qchen")
                page.locator("input[type='submit'][value='Continue'], button:has-text('Continue')").first.click()
                time.sleep(3)
        except Exception:
            pass

    # Now navigate to target
    print(f" -> Navigating to {TARGET_URL}...", flush=True)
    page.goto(TARGET_URL, wait_until="domcontentloaded")
    time.sleep(3)

    # Check status
    try:
        # Check if status is in #TestStatusId or in header text
        status_text = "Unknown"
        status_el = page.locator("#TestStatusId").first
        if status_el.count() > 0:
            status_text = status_el.evaluate("el => el.selectedOptions[0]?.text?.trim() || el.value")
        else:
            # Check header text
            header = page.locator("#SubmissionTestDetailsHeader, .page-header, body").first
            status_text = header.inner_text()

        print(f" -> CURRENT STATUS FOUND: {status_text}", flush=True)
        page.screenshot(path="etx_0040_verified_live.png")
    except Exception as e:
        print(f" -> Error checking status: {e}", flush=True)

    ctx.close()
