import os
import sys
import time
import json
import socket
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding="utf-8")

DB_FILE = "celsis_100926_database.json"
OUTPUT_FILE = "celsis_100926_links.json"

if not os.path.exists(DB_FILE):
    print(f"Error: {DB_FILE} not found!")
    sys.exit(1)

with open(DB_FILE, "r", encoding="utf-8") as f:
    db_samples = json.load(f)

# Exclude overload/special sample
SAMPLES = [s["Sample"] for s in db_samples if s.get("Status") == "PASS"]
print(f"====================================================")
print(f"  EagleTrax Link & Status Resolver for 10SEP26")
print(f"  Total PASS Samples to resolve: {len(SAMPLES)}")
print(f"  Output target: {OUTPUT_FILE}")
print(f"====================================================")

def is_port_open(port=9222):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

user_home = os.path.expanduser("~")
chrome_profile_dir = os.path.join(user_home, "chrome_automation_profile")

if is_port_open(9222):
    try:
        opts = Options()
        opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=opts)
        print("🔗 Connected to existing Chrome on port 9222!", flush=True)
    except Exception:
        opts = Options()
        opts.add_argument(f"--user-data-dir={chrome_profile_dir}")
        opts.add_argument("--profile-directory=Default")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_argument("--window-size=1366,900")
        driver = webdriver.Chrome(options=opts)
        print("🌐 Launched Chrome with automation profile...", flush=True)
else:
    opts = Options()
    opts.add_argument(f"--user-data-dir={chrome_profile_dir}")
    opts.add_argument("--profile-directory=Default")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_argument("--window-size=1366,900")
    driver = webdriver.Chrome(options=opts)
    print("🌐 Launched Chrome with automation profile...", flush=True)

# Load existing progress if any
results_map = {}
if os.path.exists(OUTPUT_FILE):
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for item in json.load(f):
                if item.get("url"):
                    results_map[item["Sample"]] = item
        print(f"Loaded {len(results_map)} already resolved links from {OUTPUT_FILE}.", flush=True)
    except Exception:
        pass

try:
    driver.get("https://etrax.eagleanalytical.com/Submission")
    time.sleep(2)

    # Check login
    cur_url = driver.current_url.lower()
    if "/account/login" in cur_url or "microsoft" in cur_url or "login.live" in cur_url:
        print("🔑 Login required. Auto-filling username...")
        try:
            u_input = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.ID, "Username"))
            )
            if not u_input.get_attribute("value"):
                u_input.clear()
                u_input.send_keys("qchen")
                print("  -> Auto-filled qchen")
            cont_btn = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue'] | //button[contains(text(), 'Continue')]"))
            )
            cont_btn.click()
            print("  -> Clicked Continue")
        except Exception:
            pass

        print("👉 Waiting for SSO authentication...")
        start_l = time.time()
        while True:
            time.sleep(2)
            now_url = driver.current_url.lower()
            try:
                kmsi = driver.find_elements(By.ID, "KmsiCheckboxField")
                if kmsi and not kmsi[0].is_selected():
                    kmsi[0].click()
                yes_btn = driver.find_elements(By.XPATH, "//input[@id='idSIButton9' or @value='Yes'] | //button[contains(text(), 'Yes')]")
                if yes_btn and yes_btn[0].is_displayed():
                    yes_btn[0].click()
            except Exception:
                pass

            if "eagleanalytical.com" in now_url and "/account/login" not in now_url and "microsoft" not in now_url and "login.live" not in now_url:
                print(f"✅ Logged in successfully ({int(time.time() - start_l)}s)!")
                break
            if time.time() - start_l > 180:
                print("❌ Login timeout.")
                sys.exit(1)

        driver.get("https://etrax.eagleanalytical.com/Submission")
        time.sleep(2)

    try:
        driver.minimize_window()
        print("🪟 Minimized Chrome window to background.", flush=True)
    except Exception:
        pass

    for idx, sid in enumerate(SAMPLES, 1):
        if sid in results_map and results_map[sid].get("url"):
            print(f"[{idx:02d}/{len(SAMPLES):02d}] {sid} -> already resolved", flush=True)
            continue

        print(f"[{idx:02d}/{len(SAMPLES):02d}] Searching: {sid} ...", flush=True)
        try:
            # Clear search
            try:
                clear_btn = driver.find_element(By.ID, "ClearButton")
                clear_btn.click()
                time.sleep(0.3)
            except Exception:
                pass

            srch_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "srchCriteria"))
            )
            srch_input.clear()
            srch_input.send_keys(sid)
            time.sleep(0.2)

            find_btn = driver.find_element(By.ID, "FindButton")
            find_btn.click()
            time.sleep(1.2)

            # Switch to Tests tab
            try:
                tests_tab = driver.find_element(By.XPATH, "//a[@href='#SubmissionTests' or contains(text(), 'Tests')]")
                tests_tab.click()
                time.sleep(0.8)
            except Exception:
                pass

            rows = driver.find_elements(By.XPATH, f"//table//tbody//tr[contains(., '{sid}')]")
            if not rows:
                time.sleep(1.2)
                rows = driver.find_elements(By.XPATH, f"//table//tbody//tr[contains(., '{sid}')]")

            found_url = None
            found_title = "Celsis Sterility Test"
            found_status = "Data Review"

            for r in rows:
                r_text = r.text
                if "celsis" in r_text.lower():
                    links = r.find_elements(By.TAG_NAME, "a")
                    for l in links:
                        href = l.get_attribute("href") or ""
                        if "/SubmissionTest/Details/" in href:
                            found_url = href if href.startswith("http") else f"https://etrax.eagleanalytical.com{href}"
                            found_title = l.text.strip()
                            break
                    cols = r.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 4:
                        found_status = cols[-1].text.strip()
                    if found_url:
                        break

            if found_url:
                print(f"  -> ✅ Found: {found_url} [{found_status}]", flush=True)
                results_map[sid] = {
                    "Sample": sid,
                    "url": found_url,
                    "test_name": found_title,
                    "status": found_status
                }
            else:
                print(f"  -> ⚠️ Not found: {sid}", flush=True)
                results_map[sid] = {
                    "Sample": sid,
                    "url": None,
                    "status": "Not Found"
                }

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(list(results_map.values()), f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"  -> ❌ Error on {sid}: {e}", flush=True)

    print("\n" + "=" * 70, flush=True)
    found_count = sum(1 for v in results_map.values() if v.get("url"))
    print(f"🎉 Resolution complete: {found_count} / {len(SAMPLES)} links found.", flush=True)
    print(f"Saved to {OUTPUT_FILE}", flush=True)
    print("=" * 70, flush=True)

except Exception as e:
    print(f"Fatal error: {e}", flush=True)
finally:
    try:
        driver.quit()
        print("Driver safely closed.", flush=True)
    except Exception:
        pass
