import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_profile_dir = os.path.join(os.path.expanduser('~'), 'chrome_automation_profile')
opts = Options()
opts.add_argument(f'--user-data-dir={chrome_profile_dir}')
opts.add_argument('--profile-directory=Default')
opts.add_argument('--window-size=1366,900')
driver = webdriver.Chrome(options=opts)

try:
    driver.get('https://etrax.eagleanalytical.com/Submission')
    time.sleep(2)

    sid = "ETX-260827-0040"
    srch = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "srchCriteria")))
    srch.clear()
    srch.send_keys(sid)
    time.sleep(0.3)

    find_btn = driver.find_element(By.ID, "FindButton")
    find_btn.click()
    print("Clicked Find...")

    time.sleep(3)

    tests_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'SubmissionTests') or text()='Tests']"))
    )
    tests_tab.click()
    print("Clicked Tests tab...")
    time.sleep(2)

    rows = driver.find_elements(By.XPATH, f"//table//tbody//tr[contains(., '{sid}')]")
    print(f"Found {len(rows)} rows for {sid}!")
    for r in rows:
        print(" ->", r.text)
        links = r.find_elements(By.TAG_NAME, "a")
        for l in links:
            href = l.get_attribute("href") or ""
            print("    link:", l.text, href)

    driver.save_screenshot("test_one_result.png")
finally:
    driver.quit()
