import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding='utf-8')

SAMPLES = [
  'ETX-260827-0040', 'ETX-260831-0002', 'ETX-260831-0004', 'ETX-260831-0019', 'ETX-260831-0083',
  'ETX-260831-0504', 'ETX-260831-0557', 'ETX-260831-0604', 'ETX-260831-0667', 'ETX-260831-0737',
  'ETX-260901-0075', 'ETX-260901-0265', 'ETX-260901-0283', 'ETX-260901-0365', 'ETX-260901-0375',
  'ETX-260901-0376', 'ETX-260901-0398', 'ETX-260901-0423', 'ETX-260901-0469', 'ETX-260901-0476',
  'ETX-260901-0649', 'ETX-260901-0666', 'ETX-260901-0673', 'ETX-260901-0681'
]

OUTPUT_FILE = "celsis_090926_new_links.json"

print("=" * 70, flush=True)
print(f"  EagleTrax Selenium 快速链接检索器 ({len(SAMPLES)} 个新样本)", flush=True)
print("=" * 70, flush=True)

import socket

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
        print("🔗 成功接入桌面上已打开的 9222 端口 Chrome 浏览器！", flush=True)
    except Exception:
        opts = Options()
        opts.add_argument(f"--user-data-dir={chrome_profile_dir}")
        opts.add_argument("--profile-directory=Default")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_argument("--window-size=1366,900")
        driver = webdriver.Chrome(options=opts)
        print("🌐 启动新的常驻 Chrome 浏览器...", flush=True)
else:
    opts = Options()
    opts.add_argument(f"--user-data-dir={chrome_profile_dir}")
    opts.add_argument("--profile-directory=Default")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_argument("--window-size=1366,900")
    driver = webdriver.Chrome(options=opts)
    print("🌐 启动常驻 Chrome 浏览器 (使用 profile: chrome_automation_profile)...", flush=True)


# 加载历史检索结果
results_map = {}
if os.path.exists(OUTPUT_FILE):
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for item in json.load(f):
                if item.get("url"):
                    results_map[item["Sample"]] = item
        print(f"已加载 {len(results_map)} 个历史检索结果。", flush=True)
    except Exception:
        pass

driver.get("https://etrax.eagleanalytical.com/Submission")
time.sleep(2)

# 检查是否需要登录
cur_url = driver.current_url.lower()
if "/account/login" in cur_url or "microsoft" in cur_url or "login.live" in cur_url:
    print("🔑 检测到登录页面，正在进行自动登录辅助...")
    try:
        user_input = WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((By.ID, "Username"))
        )
        if not user_input.get_attribute("value"):
            user_input.clear()
            user_input.send_keys("qchen")
            print("  └─ 自动填入用户名: qchen")
        cont_btn = WebDriverWait(driver, 4).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue'] | //button[contains(text(), 'Continue')]"))
        )
        cont_btn.click()
        print("  └─ 自动点击 Continue 按钮")
    except Exception:
        pass

    print("👉 窗口已保持前台，如需密码或手机 Authenticator MFA 请在屏幕/手机上确认...")
    start_l = time.time()
    last_print = 0
    while True:
        time.sleep(2)
        now_url = driver.current_url.lower()
        try:
            driver.save_screenshot("login_debug.png")
        except Exception:
            pass

        # 检查是否出现 "Stay signed in?" 按钮并自动点击 Yes
        try:
            kmsi_checkbox = driver.find_elements(By.ID, "KmsiCheckboxField")
            if kmsi_checkbox and not kmsi_checkbox[0].is_selected():
                kmsi_checkbox[0].click()
            yes_btn = driver.find_elements(By.XPATH, "//input[@id='idSIButton9' or @value='Yes'] | //button[contains(text(), 'Yes')]")
            if yes_btn and yes_btn[0].is_displayed():
                yes_btn[0].click()
                print("  └─ 自动点击 'Stay signed in? -> Yes'", flush=True)
        except Exception:
            pass

        if "eagleanalytical.com" in now_url and "/account/login" not in now_url and "microsoft" not in now_url and "login.live" not in now_url and "signin-oidc" not in now_url:
            print(f"✅ 登录恢复成功！耗时 {int(time.time() - start_l)} 秒。")
            break

        elapsed = int(time.time() - start_l)
        if elapsed - last_print >= 5:
            last_print = elapsed
            print(f"  [等待认证 {elapsed:02d}s] 当前URL: {driver.current_url[:65]}...", flush=True)

        if elapsed > 180:
            print("❌ 登录超时，程序退出。")
            sys.exit(1)

    driver.get("https://etrax.eagleanalytical.com/Submission")
    time.sleep(2)

# 登录成功后，最小化到后台静默运行
try:
    driver.minimize_window()
    print("🪟 检索器已自动最小化到任务栏静默执行！", flush=True)
except Exception:
    pass



try:
    for idx, sid in enumerate(SAMPLES, 1):
        if sid in results_map and results_map[sid].get("url"):
            print(f"[{idx:02d}/{len(SAMPLES):02d}] {sid} 已有链接 -> 跳过", flush=True)
            continue

        print(f"\n[{idx:02d}/{len(SAMPLES):02d}] 正在检索: {sid} ...", flush=True)
        try:
            # 1. 清空并填入搜索词
            try:
                clear_btn = driver.find_element(By.ID, "ClearButton")
                clear_btn.click()
                time.sleep(0.4)
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

            # 2. 点击 Tests 选项卡
            try:
                tests_tab = driver.find_element(By.XPATH, "//a[@href='#SubmissionTests' or contains(text(), 'Tests')]")
                tests_tab.click()
                time.sleep(0.8)
            except Exception:
                pass

            # 3. 等待表格加载出现
            rows = driver.find_elements(By.XPATH, f"//table//tbody//tr[contains(., '{sid}')]")
            if not rows:
                time.sleep(1.5)
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
                print(f"  ✅ 检索成功: {sid} => {found_url} (状态: {found_status})", flush=True)
                results_map[sid] = {
                    "Sample": sid,
                    "url": found_url,
                    "test_name": found_title,
                    "status": found_status
                }
            else:
                print(f"  ⚠️ 未找到 Celsis 链接: {sid}", flush=True)
                results_map[sid] = {
                    "Sample": sid,
                    "url": None,
                    "status": "Not Found"
                }

            # 实时保存
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(list(results_map.values()), f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"  ❌ 检索出错 {sid}: {e}", flush=True)

    print("\n" + "=" * 70, flush=True)
    found_count = sum(1 for v in results_map.values() if v.get("url"))
    print(f"🎉 检索完成！成功获取链接: {found_count} / {len(SAMPLES)} 个", flush=True)
    print(f"📁 结果保存在: {OUTPUT_FILE}", flush=True)
    print("=" * 70, flush=True)

except Exception as ex:
    print(f"\n❌ 程序异常: {ex}", flush=True)
finally:
    try:
        driver.quit()
        print("🔒 检索浏览器已安全关闭。", flush=True)
    except Exception:
        pass

