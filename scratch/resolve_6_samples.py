import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

USER_DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")

TARGET_ETXS = [
    "ETX-260921-0130",
    "ETX-260921-0110",
    "ETX-260921-0105",
    "ETX-260921-0145",
    "ETX-260921-0103",
    "ETX-260921-0133"
]

def resolve_link_for_etx(page, etx_id):
    print(f"Searching for {etx_id}...")
    page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded")
    time.sleep(1.5)

    try:
        clear_btn = page.locator("#ClearButton").first
        if clear_btn.count() > 0 and clear_btn.is_visible():
            clear_btn.click()
            time.sleep(0.8)
    except Exception:
        pass

    search_box = page.locator("#srchCriteria").first
    search_box.fill(etx_id)
    page.locator("#FindButton").first.click()
    time.sleep(2.5)

    tests_tab = page.locator("a[href='#SubmissionTests']").first
    if tests_tab.count() > 0:
        tests_tab.click()
        time.sleep(1.5)

    # Scan rows for Celsis Sterility Test
    rows = page.locator("#SubmissionTestList table tbody tr, table tbody tr").all()
    celsis_url = None
    for r in rows:
        text = r.inner_text().lower()
        if "celsis" in text:
            for a in r.locator("a[href*='/SubmissionTest/Details/']").all():
                href = a.get_attribute("href")
                if href:
                    celsis_url = f"https://etrax.eagleanalytical.com{href}" if href.startswith("/") else href
                    break
            if celsis_url:
                break

    if not celsis_url:
        for a in page.locator("a[href*='/SubmissionTest/Details/']").all():
            if "celsis" in a.inner_text().lower():
                href = a.get_attribute("href")
                celsis_url = f"https://etrax.eagleanalytical.com{href}" if href.startswith("/") else href
                break

    return celsis_url

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(user_data_dir=USER_DATA_DIR, channel="chrome", headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()

    resolved_map = {}
    for etx in TARGET_ETXS:
        url = resolve_link_for_etx(page, etx)
        resolved_map[etx] = url
        print(f"  -> {etx}: {url}")

    with open("scratch/resolved_6_samples.json", "w", encoding="utf-8") as f:
        json.dump(resolved_map, f, indent=2)

    ctx.close()
