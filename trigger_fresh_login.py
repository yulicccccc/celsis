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
opts.add_argument("--remote-debugging-port=9222")
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_argument("--window-size=1366,900")

print("🌐 Launching Chrome for fresh login...", flush=True)
driver = webdriver.Chrome(options=opts)

try:
    # Go to signout or direct login
    driver.get("https://etrax.eagleanalytical.com/Submission")
    time.sleep(2)

    cur_url = driver.current_url.lower()
    if "/account/login" in cur_url or "microsoft" in cur_url or "login.live" in cur_url:
        print("Handling username...", flush=True)
        try:
            u_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "Username"))
            )
            u_input.clear()
            u_input.send_keys("qchen")
            cont_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue'] | //button[contains(text(), 'Continue')]"))
            )
            cont_btn.click()
            time.sleep(2)
        except Exception:
            pass

        # If on Microsoft login page and says "Send another request" or similar
        try:
            resend_btn = driver.find_elements(By.XPATH, "//a[contains(text(), 'Send another') or contains(text(), 'resend') or contains(text(), 'try again')]")
            if resend_btn:
                resend_btn[0].click()
                print("Clicked resend request...", flush=True)
                time.sleep(2)
        except Exception:
            pass

        start_l = time.time()
        while time.time() - start_l < 180:
            time.sleep(1.0)
            now_url = driver.current_url.lower()

            try:
                driver.save_screenshot("login_code.png")
            except Exception:
                pass

            # Extract 2-digit number
            code = None
            try:
                elements = driver.find_elements(By.XPATH, "//*[@id='richId-number' or contains(@class, 'display-sign-in-large-text') or contains(@class, 'number') or @data-testid='display-sign-in-large-text']")
                for el in elements:
                    txt = el.text.strip()
                    if txt.isdigit() and len(txt) == 2:
                        code = txt
                        break
            except Exception:
                pass

            if code:
                print(f"MFA_CODE:{code}", flush=True)

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
                print("LOGIN_SUCCESS", flush=True)
                break

finally:
    print("Done.", flush=True)
