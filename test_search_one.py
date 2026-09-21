import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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

print("Launching Chrome...", flush=True)
driver = webdriver.Chrome(options=options)

try:
    sid = "ETX-260825-0380"
    print(f"Testing search for: {sid}", flush=True)
    driver.get("https://etrax.eagleanalytical.com/Submission")
    time.sleep(2)

    try:
        clear_btn = driver.find_element(By.ID, "ClearButton")
        clear_btn.click()
        time.sleep(0.5)
    except Exception as e:
        print(f"Clear error: {e}", flush=True)

    srch_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "srchCriteria"))
    )
    srch_input.clear()
    srch_input.send_keys(sid)
    time.sleep(0.2)

    find_btn = driver.find_element(By.ID, "FindButton")
    find_btn.click()
    time.sleep(2.0)

    # Click Tests tab
    try:
        tests_tab = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='#SubmissionTests' or contains(text(), 'Tests')]"))
        )
        tests_tab.click()
        time.sleep(1.5)
    except Exception as e:
        print(f"Tests tab error: {e}", flush=True)

    driver.save_screenshot("test_search_screenshot.png")
    print("Saved test_search_screenshot.png", flush=True)

    # Find links
    all_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/SubmissionTest/Details/')]")
    print(f"Found {len(all_links)} SubmissionTest/Details links:", flush=True)
    for l in all_links:
        print(f"  Href: {l.get_attribute('href')} | Text: {l.text.strip()}", flush=True)

finally:
    driver.quit()
    print("Done.", flush=True)
