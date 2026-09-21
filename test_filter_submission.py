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
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("--window-size=1366,900")

print("Launching Chrome for filter inspection...", flush=True)
driver = webdriver.Chrome(options=options)

try:
    driver.get("https://etrax.eagleanalytical.com/Submission")
    time.sleep(2)

    cur_url = driver.current_url.lower()
    if "/account/login" in cur_url or "microsoft" in cur_url:
        print("Login required. Attempting auto-login...", flush=True)
        try:
            u_input = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.ID, "Username"))
            )
            u_input.send_keys("qchen")
            driver.find_element(By.XPATH, "//input[@value='Continue']").click()
            time.sleep(3)
        except Exception:
            pass

    # Inspect the filter controls
    driver.save_screenshot("filter_controls.png")
    print("Saved filter_controls.png", flush=True)

    # Print all button / select elements in the filter area
    buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'selectpicker') or contains(@class, 'dropdown-toggle') or contains(@data-id, 'Test')]")
    print(f"Found {len(buttons)} filter dropdown buttons:", flush=True)
    for b in buttons:
        print(f"  Button: title='{b.get_attribute('title')}' data-id='{b.get_attribute('data-id')}' text='{b.text.strip()}'", flush=True)

finally:
    driver.quit()
    print("Done.", flush=True)
