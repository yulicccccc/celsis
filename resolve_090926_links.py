import os
import time
import json
from playwright.sync_api import sync_playwright

with open("celsis_090926_summary.json", "r", encoding="utf-8") as f:
    summary_data = json.load(f)

SAMPLES = [item["Sample"] for item in summary_data]

user_data_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pastdue_playwright_session")
output_json = os.path.abspath("celsis_090926_links_verified.json")

print("====================================================")
print(f"  EagleTrax Strict Link Resolver ({len(SAMPLES)} samples)")
print(f"  Target output: {output_json}")
print("====================================================")

# Load existing results if any to support resume
results_map = {}
if os.path.exists(output_json):
    try:
        with open(output_json, "r", encoding="utf-8") as f:
            existing = json.load(f)
            for r in existing:
                if r.get("url"):
                    results_map[r["etx_id"]] = r
        print(f"Loaded {len(results_map)} already resolved links from existing file.")
    except Exception:
        pass

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        channel="chrome",
        headless=False,
        viewport={"width": 1366, "height": 850}
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    
    print(" -> Opening Submission search page...")
    page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded")
    time.sleep(3)

    # Check if redirected to login
    if "login.microsoftonline.com" in page.url or "login.live.com" in page.url:
        print("[AUTH REQUIRED] Please complete SSO login in the browser window!")
        # Wait up to 60 seconds for login
        for _ in range(30):
            time.sleep(2)
            if "etrax.eagleanalytical.com" in page.url and "login" not in page.url:
                print(" -> Login detected successfully!")
                break

    for idx, etx in enumerate(SAMPLES, start=1):
        if etx in results_map and results_map[etx].get("url"):
            print(f"[{idx}/{len(SAMPLES)}] {etx} already resolved -> skipping.")
            continue

        print(f"\n[{idx}/{len(SAMPLES)}] Searching strictly for {etx}...")
        try:
            search_box = page.wait_for_selector("#srchCriteria", timeout=15000)
            
            # Clear button
            try:
                clear_btn = page.locator("#ClearButton, button[title='Clear'], input[value='Clear']").first
                if clear_btn.count() > 0:
                    clear_btn.click()
                    time.sleep(0.5)
            except Exception:
                pass
                
            # Fill exact ETX
            search_box.fill("")
            search_box.fill(etx)
            time.sleep(0.3)
            
            # Click Find
            find_btn = page.locator("#FindButton, button:has-text('Find'), input[value='Find']").first
            find_btn.click()
            
            # Wait for Tests tab and click it
            time.sleep(1.2)
            try:
                tests_tab = page.locator("a[href='#SubmissionTests'], a:has-text('Tests')").first
                if tests_tab.count() > 0:
                    tests_tab.click()
            except Exception:
                pass

            # STRICT WAIT: Wait until table contains this exact ETX ID!
            target_row_sel = f"#SubmissionTestList table tbody tr:has-text('{etx}')"
            try:
                page.wait_for_selector(target_row_sel, timeout=12000)
            except Exception:
                page.wait_for_selector(f"table tbody tr:has-text('{etx}')", timeout=5000)

            # Locate matching rows that have BOTH the ETX and Celsis
            matching_rows = page.locator(f"table tbody tr:has-text('{etx}')").all()
            found_url = None
            test_title = None
            status_text = None
            
            for r in matching_rows:
                r_text = r.inner_text().strip()
                if "celsis" in r_text.lower():
                    links = r.locator("a").all()
                    for l in links:
                        href = l.get_attribute("href") or ""
                        txt = l.inner_text().strip()
                        if "/SubmissionTest/Details/" in href:
                            found_url = href if href.startswith("http") else f"https://etrax.eagleanalytical.com{href}"
                            test_title = txt
                            break
                    cols = r.locator("td").all()
                    if len(cols) >= 4:
                        status_text = cols[-1].inner_text().strip()
                    if found_url:
                        break

            if found_url:
                print(f" -> VERIFIED: {etx} => {found_url} (status: {status_text})")
                results_map[etx] = {
                    "index": idx,
                    "etx_id": etx,
                    "test_name": test_title or "Celsis Sterility Test",
                    "url": found_url,
                    "status": status_text or "Completed"
                }
            else:
                print(f" -> [ERROR] Could not find Celsis row for {etx}")
                results_map[etx] = {
                    "index": idx,
                    "etx_id": etx,
                    "test_name": "Not Found",
                    "url": None,
                    "status": "Failed"
                }
        except Exception as e:
            print(f" -> [EXCEPTION] {etx}: {e}")
            results_map[etx] = {
                "index": idx,
                "etx_id": etx,
                "test_name": "Error",
                "url": None,
                "status": f"Error: {e}"
            }

        # Save incremental progress
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(list(results_map.values()), f, indent=2)

    print(f"\nAll done! Verified links written to: {output_json}")
    ctx.close()
