import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding='utf-8')

# 配置信息
ETX_ID = "ETX-260830-0040"
TARGET_URL = "https://etrax.eagleanalytical.com/SubmissionTest/Details/AZfBY7MUc4mMGrikVnZP2w__"
USERNAME = "qchen"
PIN = "1124"

# 使用与 Scan 项目一致的独立 Chrome Profile
user_home = os.path.expanduser("~")
chrome_profile_dir = os.path.join(user_home, "chrome_automation_profile")

print("=" * 60)
print(f"  EagleTrax 单样本审批测试: {ETX_ID}")
print(f"  目标链接: {TARGET_URL}")
print("=" * 60)

options = Options()
options.add_argument(f"--user-data-dir={chrome_profile_dir}")
options.add_argument("--profile-directory=Default")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("--window-size=1366,900")

print(f"\n🌐 正在启动 Chrome 浏览器 (可视窗口)...")
driver = webdriver.Chrome(options=options)

try:
    print(f"🔍 正在打开页面: {TARGET_URL}")
    driver.get(TARGET_URL)
    time.sleep(3)

    # 检查是否需要登录
    current_url = driver.current_url.lower()
    if "/account/login" in current_url or "microsoft" in current_url or "login.live" in current_url:
        print("\n🔑 检测到需要登录 EagleTrax...")
        # 尝试自动填入用户名并点击 Continue
        try:
            user_input = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.ID, "Username"))
            )
            if not user_input.get_attribute("value"):
                user_input.clear()
                user_input.send_keys(USERNAME)
                print(f"  └─ 自动填入用户名: {USERNAME}")
            
            cont_btn = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue'] | //button[contains(text(), 'Continue')]"))
            )
            cont_btn.click()
            print("  └─ 自动点击 Continue 按钮")
        except Exception:
            pass

        print("\n👉 请在弹出的 Chrome 窗口中完成登录 (如有手机 Authenticator MFA 请在手机上点击确认)...")
        print("   脚本正在后台等待登录完成，登录后会自动继续执行，无需手动刷新。")

        # 轮询等待登录完成
        start_time = time.time()
        while True:
            time.sleep(3)
            now_url = driver.current_url.lower()
            if "/account/login" not in now_url and "microsoft" not in now_url and "login.live" not in now_url:
                print(f"✅ 登录成功！耗时 {int(time.time() - start_time)} 秒。")
                break
            if time.time() - start_time > 180:
                print("❌ 登录超时 (超过3分钟)，请重新运行脚本。")
                sys.exit(1)

        # 重新回到目标样本页面
        print(f"🔄 导航回目标样本页面: {TARGET_URL}")
        driver.get(TARGET_URL)
        time.sleep(3)

    # 检查当前审批状态
    status_elem = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "TestStatusId"))
    )
    select_obj = Select(status_elem)
    current_status = select_obj.first_selected_option.text.strip()
    print(f"\n📋 当前样本状态: [{current_status}]")

    if current_status.lower() == "approved":
        print(f"\n🎉 [已确认] 样本 {ETX_ID} 已经是 Approved 状态！无需重复批准。")
        driver.save_screenshot("etx_0040_approved_confirmed.png")
        print("📸 状态截图已保存至: etx_0040_approved_confirmed.png")
    else:
        print("\n⚡ 开始执行审批流程...")
        # 1. 下拉框选择 Approved
        select_obj.select_by_visible_text("Approved")
        print("  [1/4] 已在下拉菜单中选择 'Approved'")
        time.sleep(1)

        # 2. 填写 Username
        aun_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "AUN"))
        )
        aun_field.clear()
        aun_field.send_keys(USERNAME)
        print(f"  [2/4] 已输入账号: {USERNAME}")

        # 3. 填写 PIN
        apd_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "APD"))
        )
        apd_field.clear()
        apd_field.send_keys(PIN)
        print("  [3/4] 已输入 PIN 码: ****")
        time.sleep(0.5)

        # 4. 点击 Save 按钮
        save_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ChangeTestStatusSaveButton"))
        )
        save_btn.click()
        print("  [4/4] 已点击绿色 Save 按钮，正在提交保存...")

        # 等待弹窗和保存按钮隐藏
        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "ChangeTestStatusSaveButton"))
            )
            print("  └─ 授权弹窗已关闭")
        except Exception:
            time.sleep(2)

        # 重新刷新页面验证
        time.sleep(3)
        driver.get(TARGET_URL)
        time.sleep(2)

        verify_elem = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "TestStatusId"))
        )
        final_status = Select(verify_elem).first_selected_option.text.strip()
        print("\n" + "=" * 60)
        print(f"🎯 最终验证结果: {ETX_ID} 当前状态为 -> [{final_status}]")
        print("=" * 60)

        driver.save_screenshot("etx_0040_approved_confirmed.png")
        print("📸 最终确认截图已保存至: etx_0040_approved_confirmed.png")

        if final_status.lower() == "approved":
            print(f"\n🎉 恭喜！单样本 {ETX_ID} 自动审批测试 100% 成功！")
        else:
            print(f"\n⚠️ 提示：状态显示为 [{final_status}]，请在浏览器中查看详情。")

    print("\n" + "-" * 60)
    input("👉 浏览器保持打开中供你查看。按【Enter 回车键】即可安全退出并关闭浏览器...")

finally:
    driver.quit()
    print("🔒 浏览器已关闭。测试完毕。")
