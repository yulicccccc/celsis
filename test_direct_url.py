import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

chrome_profile_dir = os.path.join(os.path.expanduser('~'), 'chrome_automation_profile')
opts = Options()
opts.add_argument(f'--user-data-dir={chrome_profile_dir}')
opts.add_argument('--profile-directory=Default')
opts.add_argument('--window-size=1366,900')
driver = webdriver.Chrome(options=opts)

try:
    sid = 'ETX-260901-0265'
    driver.get(f'https://etrax.eagleanalytical.com/Submission/Details/{sid}')
    time.sleep(2)
    print('Current URL:', driver.current_url)
    print('Title:', driver.title)
    
    # Click Tests tab if needed
    try:
        tab = driver.find_element(By.XPATH, "//a[contains(text(), 'Tests') or @href='#Tests']")
        tab.click()
        time.sleep(1)
    except Exception:
        pass
        
    links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Celsis')]")
    for l in links:
        print('Found direct link:', l.text, l.get_attribute('href'))
finally:
    driver.quit()
