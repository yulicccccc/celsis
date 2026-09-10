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

    sid = "ETX-260901-0075"
    srch = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "srchCriteria")))
    srch.clear()
    srch.send_keys(sid)
    time.sleep(0.3)

    find_btn = driver.find_element(By.ID, "FindButton")
    find_btn.click()
    print("Clicked Find...")
    time.sleep(3)

    cur_url = driver.current_url
    print("URL after search:", cur_url)

    # If it navigated to /Submission/Details/...
    if "/submission/details/" in cur_url.lower():
        print("Directly on Submission Details page!")
        # Click Tests tab on details page
        tests_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Tests') or @href='#Tests']"))
        )
        tests_tab.click()
        time.sleep(1.5)

        # Look for Celsis Sterility Test
        links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Celsis')]")
        for l in links:
            print("Found Celsis Link:", l.text, l.get_attribute("href"))
    else:
        print("On list page, checking table...")
        tests_tab = driver.find_element(By.XPATH, "//a[contains(@href, 'SubmissionTests') or text()='Tests']")
        tests_tab.click()
        time.sleep(2)
        links = driver.find_elements(By.XPATH, "//table//tbody//tr//a[contains(text(), 'Celsis') or contains(@href, '/SubmissionTest/Details/')]")
        for l in links:
            print("Found Link:", l.text, l.get_attribute("href"))

    driver.save_screenshot("test_0075_result.png")
finally:
    driver.quit()
