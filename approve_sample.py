import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding='utf-8')

USERNAME = "qchen"
PIN = "1124"

# 加载已验证的 38 个样本及其链接
with open("celsis_090926_final_audit_report.json", "r", encoding="utf-8") as f:
    report_data = json.load(f)

url_map = {
    s["Sample"]: s["EagleTrax URL"] 
    for s in report_data 
    if s.get("Audit Result") == "PASS & 100% MATCH" and s.get("EagleTrax URL")
}

# 确定要审批的目标样本
target_etx = None
if len(sys.argv) > 1 and sys.argv[1].strip():
    target_etx = sys.argv[1].strip()
else:
    print("=" * 65)
    print("  EagleTrax 单样本审批测试器")
    print("=" * 65)
    print("推荐测试样本 (已 100% 核对通过):")
    print("  1. ETX-260830-0041 (样本 3，状态正常)")
    print("  2. ETX-260827-0640 (样本 1，状态正常)")
    print("  3. ETX-260831-0105 (样本 4，状态正常)")
    print("  4. ETX-260830-0040 (样本 2)")
    print("-" * 65)
    user_choice = input("👉 请输入要测试的样本号 (直接按 Enter 默认测试 ETX-260830-0041): ").strip()
    if user_choice:
        target_etx = user_choice
    else:
        target_etx = "ETX-260830-0041"

# 查找对应 URL
target_url = url_map.get(target_etx)
if not target_url:
    # 尝试模糊匹配或直接作为 URL
    if "http" in target_etx:
        target_url = target_etx
    else:
        # 在 report_data 中找包含该字符串的
        for k, v in url_map.items():
            if target_etx.lower() in k.lower():
                target_etx = k
                target_url = v
                break

if not target_url:
    print(f"❌ 未找到样本 {target_etx} 对应的 EagleTrax URL，请检查样本号。")
    sys.exit(1)

print(f"\n🎯 目标样本: {target_etx}")
print(f"🔗 目标链接: {target_url}")

# 使用与 Scan 项目一致的独立 Chrome Profile
user_home = os.path.expanduser("~")
chrome_profile_dir = os.path.join(user_home, "chrome_automation_profile")

options = Options()
options.add_argument(f"--user-data-dir={chrome_profile_dir}")
options.add_argument("--profile-directory=Default")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("--window-size=1366,900")

print(f"\n🌐 正在启动 Chrome 浏览器 (可视窗口)...")
driver = webdriver.Chrome(options=options)

try:
    print(f"🔍 正在打开页面: {target_url}")
    driver.get(target_url)
    time.sleep(3)

    # 检查是否需要登录
    current_url = driver.current_url.lower()
    if "/account/login" in current_url or "microsoft" in current_url or "login.live" in current_url:
        print("\n🔑 检测到需要登录 EagleTrax...")
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
        print("   脚本正在后台等待登录完成，登录后会自动继续执行...")

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
        print(f"🔄 导航回目标样本页面: {target_url}")
        driver.get(target_url)
        time.sleep(3)

    # 检查下拉菜单
    status_elem = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "TestStatusId"))
    )
    select_obj = Select(status_elem)
    current_status = select_obj.first_selected_option.text.strip()
    print(f"\n📋 当前样本状态: [{current_status}]")

    # 列出所有可用选项，确保完全透明
    options_list = [opt.text.strip() for opt in select_obj.options]
    print(f"📑 下拉菜单所有可选状态: {options_list}")

    if current_status.lower() == "approved":
        print(f"\n🎉 [已确认] 样本 {target_etx} 已经是 Approved 状态！无需重复批准。")
        screenshot_name = f"{target_etx}_approved_confirmed.png"
        driver.save_screenshot(screenshot_name)
        print(f"📸 状态截图已保存至: {screenshot_name}")
    else:
        # Rule 9: 体积与方法互斥校验
        print("\n🔍 [Rule 9 质控复核] 正在校验 Method Performed 与 Volume 栏位配置...")
        try:
            method_elem = driver.find_element(By.ID, "SubmissionTestResults_1__Value")
            method_val = Select(method_elem).first_selected_option.text.strip() if method_elem.tag_name.lower() == 'select' else method_elem.get_attribute("value").strip()

            mf_vol_elem = driver.find_element(By.ID, "SubmissionTestResults_3__Value") if len(driver.find_elements(By.ID, "SubmissionTestResults_3__Value")) > 0 else None
            mf_vol = mf_vol_elem.get_attribute("value").strip() if mf_vol_elem else ""

            di_vol_elem = driver.find_element(By.ID, "SubmissionTestResults_4__Value") if len(driver.find_elements(By.ID, "SubmissionTestResults_4__Value")) > 0 else None
            di_vol = di_vol_elem.get_attribute("value").strip() if di_vol_elem else ""

            print(f"  • 检测到测试方法: [{method_val}]")
            print(f"  • Filtered Volume (MF专用栏位): '{mf_vol or '(留空)'}'")
            print(f"  • Added Volume (DI专用栏位):    '{di_vol or '(留空)'}'")

            if "membrane" in method_val.lower():
                if di_vol:
                    print(f"\n⛔ [Rule 9 拦截] 严重质控隐患！当前为 MF 方法，但 DI 栏位误填了 '{di_vol}'！")
                    input("👉 质控拦截保护中。按【Enter 回车键】关闭浏览器...")
                    sys.exit(1)
                else:
                    print(f"  ✅ [通过] 栏位配置合法: MF 方法体积填写在 MF 栏位 ({mf_vol} mL)，DI 栏位保持为空。")
            elif "direct" in method_val.lower():
                if mf_vol:
                    print(f"\n⛔ [Rule 9 拦截] 严重质控隐患！当前为 DI 方法，但 MF 栏位误填了 '{mf_vol}'！")
                    input("👉 质控拦截保护中。按【Enter 回车键】关闭浏览器...")
                    sys.exit(1)
                else:
                    print(f"  ✅ [通过] 栏位配置合法: DI 方法体积填写在 DI 栏位 ({di_vol} mL)，MF 栏位保持为空。")
        except Exception as ve:
            print(f"  ℹ️ 体积字段读取提示: {ve}")

        print("\n⚡ 正在匹配审批选项...")
        # 智能查找包含 'Approve' 的选项（不区分大小写、忽略首尾空格）
        target_option = None
        for opt in select_obj.options:
            cleaned_text = opt.text.replace("\u00a0", " ").strip().lower()
            if "approv" in cleaned_text:
                target_option = opt
                break

        if not target_option:
            print(f"❌ 警告: 在下拉菜单中未找到 'Approved' 选项！")
            print(f"   可能原因: 当前状态 [{current_status}] 下不支持直接 Approve，或者账号权限限制。")
            print(f"   可用选项为: {options_list}")
        else:
            # 选中 Approved
            val = target_option.get_attribute("value")
            select_obj.select_by_value(val)
            print(f"  [1/4] 已选中审批选项: '{target_option.text.strip()}' (value={val})")
            time.sleep(1)

            # 填写 Username
            print("  [2/4] 正在输入授权账号...")
            aun_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "AUN"))
            )
            aun_field.clear()
            aun_field.send_keys(USERNAME)
            print(f"        账号已输入: {USERNAME}")

            # 填写 PIN
            print("  [3/4] 正在输入 PIN 码...")
            apd_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "APD"))
            )
            apd_field.clear()
            apd_field.send_keys(PIN)
            print("        PIN 码已输入: ****")
            time.sleep(0.5)

            # 点击 Save
            print("  [4/4] 正在点击绿色 Save 按钮提交授权...")
            save_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "ChangeTestStatusSaveButton"))
            )
            save_btn.click()
            print("        已点击 Save 按钮！")

            # 等待保存完成（弹窗隐去）
            try:
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.ID, "ChangeTestStatusSaveButton"))
                )
                print("  └─ 授权弹窗已关闭")
            except Exception:
                time.sleep(2)

            # 重新刷新页面验证
            print("🔄 正在刷新页面核实审批结果...")
            time.sleep(3)
            driver.get(target_url)
            time.sleep(2)

            verify_elem = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "TestStatusId"))
            )
            final_status = Select(verify_elem).first_selected_option.text.strip()
            print("\n" + "=" * 60)
            print(f"🎯 最终验证结果: {target_etx} 当前状态为 -> [{final_status}]")
            print("=" * 60)

            screenshot_name = f"{target_etx}_approved_confirmed.png"
            driver.save_screenshot(screenshot_name)
            print(f"📸 最终确认截图已保存至: {screenshot_name}")

            if final_status.lower() == "approved":
                print(f"\n🎉 恭喜！样本 {target_etx} 自动审批 100% 成功！")
            else:
                print(f"\n⚠️ 提示：状态显示为 [{final_status}]，请在浏览器中核实。")

    print("\n" + "-" * 60)
    input("👉 浏览器保持打开中供你查看。按【Enter 回车键】即可安全退出并关闭浏览器...")

except Exception as e:
    print(f"\n❌ 运行中出现异常: {e}")
    input("👉 按【Enter 回车键】关闭浏览器...")

finally:
    try:
        driver.quit()
    except Exception:
        pass
    print("🔒 浏览器已关闭。测试完毕。")
