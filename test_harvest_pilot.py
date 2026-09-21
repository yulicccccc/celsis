import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding="utf-8")

user_home = os.path.expanduser("~")
chrome_profile_dir = os.path.join(user_home, "chrome_automation_profile")

options = Options()
options.add_argument(f"--user-data-dir={chrome_profile_dir}")
options.add_argument("--profile-directory=Default")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("--window-size=1366,900")

print("🌐 Launching Chrome...", flush=True)
driver = webdriver.Chrome(options=options)

try:
    driver.get("https://etrax.eagleanalytical.com/Submission")
    time.sleep(2)
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
            cont_btn = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue'] | //button[contains(text(), 'Continue')]"))
            )
            cont_btn.click()
        except Exception:
            pass

        print("👉 Waiting for SSO authentication in browser window...")
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
            if time.time() - start_l > 300:
                print("❌ Login timeout.")
                sys.exit(1)

        driver.get("https://etrax.eagleanalytical.com/Submission")
        time.sleep(2)

    # Test sample: ETX-260825-0380
    test_samples = ["ETX-260825-0380", "ETX-260825-0186"]
    for sid in test_samples:
        print(f"\nSearching for {sid}...", flush=True)
        # Clear
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
        time.sleep(1.5)

        # Switch to Tests tab
        try:
            tests_tab = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='#SubmissionTests' or contains(text(), 'Tests')]"))
            )
            tests_tab.click()
            time.sleep(1.0)
        except Exception:
            pass

        rows = driver.find_elements(By.XPATH, f"//table//tbody//tr[contains(., '{sid}')]")
        if not rows:
            time.sleep(1.5)
            rows = driver.find_elements(By.XPATH, f"//table//tbody//tr[contains(., '{sid}')]")

        details_url = None
        for r in rows:
            if "celsis" in r.text.lower():
                links = r.find_elements(By.TAG_NAME, "a")
                for l in links:
                    href = l.get_attribute("href") or ""
                    if "/SubmissionTest/Details/" in href:
                        details_url = href if href.startswith("http") else f"https://etrax.eagleanalytical.com{href}"
                        break
                if details_url:
                    break

        print(f"  Details URL: {details_url}")
        if details_url:
            driver.get(details_url)
            time.sleep(2.5)

            # Extract Event History table
            event_history = []
            table_rows = driver.find_elements(By.XPATH, "//table[contains(., 'Date Performed') or contains(., 'Event')]//tbody//tr")
            for tr in table_rows:
                cols = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, "td")]
                if len(cols) >= 3:
                    event_history.append({
                        "event": cols[0],
                        "date_performed": cols[1],
                        "performed_by": cols[2]
                    })

            print(f"  Found {len(event_history)} events in Event History:")
            for ev in event_history:
                if any(k in ev["event"].lower() for k in ["approved", "review", "completed", "entered"]):
                    print(f"    • {ev['event']} | {ev['date_performed']} | {ev['performed_by']}")

finally:
    driver.quit()
    print("Test finished.")
