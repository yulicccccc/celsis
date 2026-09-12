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

opts = Options()
opts.add_argument(f"--user-data-dir={chrome_profile_dir}")
opts.add_argument("--profile-directory=Default")
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_argument("--window-size=1366,900")

driver = webdriver.Chrome(options=opts)

try:
    driver.get("https://etrax.eagleanalytical.com/Submission")
    time.sleep(2)

    cur_url = driver.current_url.lower()
    if "/account/login" in cur_url or "microsoft" in cur_url or "login.live" in cur_url:
        print("Redirected to login. Handling username...")
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
            time.sleep(2)
        except Exception:
            pass

        start_l = time.time()
        while True:
            time.sleep(1.5)
            now_url = driver.current_url.lower()
            
            # Save screenshot continuously
            try:
                driver.save_screenshot("login_code.png")
            except Exception:
                pass

            # Check for richId-number or displaySign
            code = None
            try:
                elem = driver.find_elements(By.XPATH, "//*[@id='richId-number' or contains(@class, 'display-sign-in-large-text') or contains(@class, 'number')]")
                for el in elem:
                    txt = el.text.strip()
                    if txt.isdigit() and len(txt) == 2:
                        code = txt
                        break
            except Exception:
                pass

            if code:
                print(f"\n==========================================")
                print(f"  👉 MICROSOFT MFA CODE: 【 {code} 】")
                print(f"==========================================\n", flush=True)

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
                print("Timeout.")
                break

finally:
    driver.quit()
