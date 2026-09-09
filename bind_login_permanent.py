import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding='utf-8')

USERNAME = "qchen"

user_home = os.path.expanduser("~")
chrome_profile_dir = os.path.join(user_home, "chrome_automation_profile")

print("=" * 70)
print("   EagleTrax 永久登录状态绑定器 (对标 Scan step1 机制)")
print("   只需操作一次，永久保存微软 SSO 长效 Token (Stay Signed In)")
print("=" * 70)

options = Options()
options.add_argument(f"--user-data-dir={chrome_profile_dir}")
options.add_argument("--profile-directory=Default")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("detach", True)
options.add_argument("--window-size=1366,900")

print(f"\n🌐 正在启动 Chrome 浏览器...")
try:
    driver = webdriver.Chrome(options=options)
except Exception as e:
    print(f"\n⚠️ 启动冲突: {e}")
    print("👉 请先手动关掉屏幕上已有的自动化 Chrome 窗口，然后再运行！")
    sys.exit(1)

# 打开 EagleTrax 首页
driver.get("https://etrax.eagleanalytical.com/Submission")
time.sleep(3)

# 尝试自动输入用户名
try:
    username_field = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, 'Username'))
    )
    username_field.clear()
    username_field.send_keys(USERNAME)
    print(f"  └─ 自动填入用户名: {USERNAME}")

    continue_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue']"))
    )
    continue_button.click()
    print("  └─ 自动点击 Continue 按钮")
except Exception:
    print("💡 已在主界面或无需输入用户名")

print("\n" + "=" * 70)
print("👉 【核心关键操作 - 只需一次】:")
print("   1. 请在 Chrome 窗口中完成手机 Authenticator 确认。")
print("   2. 极其重要：当微软提示 'Stay signed in?' (保持登录状态) 时，")
print("      务必勾选 'Don't show this again' 并点击 【Yes】！")
print("   3. 当看到 EagleTrax 的 Submissions 正常主列表页面后：")
print("=" * 70)

input("\n>>> 看到正常页面后，回到这里按 【Enter 回车键】保存退出: ")

print("\n🎉 恭喜！长效登录 Token 已永久保存到 chrome_automation_profile！")
print("   以后无论运行单样本审批、5 样本测试还是全量 38 样本批量审批，")
print("   均会自动复用该长效 Token，再也不会被频繁要求登录了！")

# 安全关闭
driver.quit()
print("🔒 绑定完成，浏览器已安全退出。")
