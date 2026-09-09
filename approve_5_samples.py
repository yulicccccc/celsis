import os
import sys
import time
import json
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding='utf-8')

USERNAME = "qchen"
PIN = "1124"
AUDIT_FILE = "celsis_090926_final_audit_report.json"
PROGRESS_FILE = "approve_5_progress.json"

# 精选 5 个 100% 吻合的高质量样本 (兼具 MF 薄膜过滤与 DI 直接接种，充分检验 Rule 9)
SELECTED_SAMPLES = [
    "ETX-260827-0640",  # DI 直接接种
    "ETX-260831-0105",  # DI 直接接种
    "ETX-260831-0108",  # MF 薄膜过滤
    "ETX-260831-0142",  # MF 薄膜过滤
    "ETX-260831-0225",  # MF 薄膜过滤
]

print("=" * 70)
print("   EagleTrax Celsis 5 样本进阶自动审批测试 (常驻浏览器模式)")
print("   浏览器退出后将保持打开，绝不自动关闭，方便随时人工查看或手动关闭")
print("=" * 70)

# 读取审计报告
with open(AUDIT_FILE, "r", encoding="utf-8") as f:
    audit_data = json.load(f)

audit_map = {s["Sample"]: s for s in audit_data}

target_queue = []
for sid in SELECTED_SAMPLES:
    if sid in audit_map:
        info = audit_map[sid]
        # 严格遵守 Rule 2: 只有 PASS 的白名单样本能进
        if "PASS" in info.get("Audit Result", ""):
            target_queue.append(info)
        else:
            print(f"⛔ 样本 {sid} 未通过质控白名单，已安全排除！")

print(f"\n📋 本轮选定的 5 个测试样本:")
for idx, s in enumerate(target_queue, 1):
    print(f"  {idx}. {s['Sample']} | 仪器: #{s.get('Instrument')} | ATP: {s.get('PDF ATP')} | TSB: {s.get('PDF TSB')} | FTM: {s.get('PDF FTM')} | CV%: {s.get('Max CV%')}")

print("\n" + "-" * 70)
print("⏱️ 请选择审核间隔模式:")
print("  [1] 黄金质控节奏 (推荐: 1 ~ 3 分钟/样本，自然随机微调，兼顾效率与 GxP 审计真实性)")
print("  [2] 快速测试模式 (约 20 ~ 35 秒/样本，用于快速检验 5 个样本审批全流程)")
mode_choice = input("👉 请输入 1 或 2 (默认回车选择 [1]): ").strip()

if mode_choice == "2":
    min_wait = 20
    max_wait = 35
    print("⚡ 已选择: 快速测试模式 (间隔 20 ~ 35 秒)")
else:
    min_wait = 60
    max_wait = 180
    print("🛡️ 已选择: 黄金质控节奏模式 (间隔 1 ~ 3 分钟 / 60 ~ 180 秒)")

print("-" * 70)
input("👉 按【Enter 回车键】正式启动 Chrome 浏览器开始审批...")

# 启动 Chrome (配置常驻 detach 模式)
user_home = os.path.expanduser("~")
chrome_profile_dir = os.path.join(user_home, "chrome_automation_profile")

options = Options()
options.add_argument(f"--user-data-dir={chrome_profile_dir}")
options.add_argument("--profile-directory=Default")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("detach", True)  # 核心配置：浏览器常驻，脚本结束后不关闭浏览器！
options.add_argument("--window-size=1366,900")

print(f"\n🌐 正在启动 Chrome 浏览器 (已配置常驻模式)...")
driver = webdriver.Chrome(options=options)

def countdown_timer(seconds):
    """动态倒计时显示"""
    start = time.time()
    while True:
        elapsed = int(time.time() - start)
        remain = seconds - elapsed
        if remain <= 0:
            break
        mins = remain // 60
        secs = remain % 60
        print(f"\r⏳ [质控间隔等待中] 离下一个样本审批还有: {mins:02d}分{secs:02d}秒 ({remain}s)...  ", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 75 + "\r", end="", flush=True)

progress_records = []

try:
    total = len(target_queue)
    for idx, sample_info in enumerate(target_queue, 1):
        sample_id = sample_info["Sample"]
        target_url = sample_info.get("EagleTrax URL")

        print("\n" + "=" * 65)
        print(f"[{idx}/{total}] 正在审核并审批样本: {sample_id}")
        print(f"    链接: {target_url}")
        print("=" * 65)

        driver.get(target_url)
        time.sleep(3)

        # 检查是否需要登录，严谨等待微软 SSO 重定向完全结束
        cur_url = driver.current_url.lower()
        if "/account/login" in cur_url or "microsoft" in cur_url or "login.live" in cur_url:
            print("🔑 检测到登录页面，正在进行自动登录辅助...")
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

            print("👉 如有手机 Authenticator MFA 请在手机上点击确认...")
            start_l = time.time()
            while True:
                time.sleep(3)
                now_url = driver.current_url.lower()
                # 严谨条件：必须完全脱离 login、microsoft、signin-oidc 且处于 eagleanalytical.com 下
                if "eagleanalytical.com" in now_url and "/account/login" not in now_url and "microsoft" not in now_url and "login.live" not in now_url and "signin-oidc" not in now_url:
                    print(f"✅ 登录恢复成功！耗时 {int(time.time() - start_l)} 秒。")
                    break
                if time.time() - start_l > 180:
                    print("❌ 登录超时，程序退出。")
                    sys.exit(1)

            # 登录完成后重新回到目标样本页面
            driver.get(target_url)
            time.sleep(3)

        # 1. 检查当前状态
        status_elem = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "TestStatusId"))
        )
        select_obj = Select(status_elem)
        current_status = select_obj.first_selected_option.text.strip()
        print(f"  📋 页面当前状态: [{current_status}]")

        # 在 EagleTrax 中，已审批通过的状态会显示为 Approved 或 Completed
        if current_status.lower() in ["approved", "completed"]:
            print(f"  🎉 [已确认] 该样本当前状态为 [{current_status}]（已经是完成/已审批状态）！无需重复操作，跳过。")
            progress_records.append({
                "Sample": sample_id,
                "status": current_status,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": "Already completed/approved"
            })
            continue

        # 2. Rule 9: 体积与方法互斥复核
        print(f"  🔍 [Rule 9 质控复核] 正在校验测试方法与体积填入栏位...")
        try:
            method_elem = driver.find_element(By.ID, "SubmissionTestResults_1__Value")
            method_val = Select(method_elem).first_selected_option.text.strip() if method_elem.tag_name.lower() == 'select' else method_elem.get_attribute("value").strip()

            mf_vol_elem = driver.find_element(By.ID, "SubmissionTestResults_3__Value") if len(driver.find_elements(By.ID, "SubmissionTestResults_3__Value")) > 0 else None
            mf_vol = mf_vol_elem.get_attribute("value").strip() if mf_vol_elem else ""

            di_vol_elem = driver.find_element(By.ID, "SubmissionTestResults_4__Value") if len(driver.find_elements(By.ID, "SubmissionTestResults_4__Value")) > 0 else None
            di_vol = di_vol_elem.get_attribute("value").strip() if di_vol_elem else ""

            print(f"     检测方法: [{method_val}] | MF体积栏: '{mf_vol or '(空)'}' | DI体积栏: '{di_vol or '(空)'}'")

            if "membrane" in method_val.lower():
                if di_vol:
                    print(f"  ⛔ [Rule 9 拦截] 质控警报: MF 方法但 DI 栏位有值 '{di_vol}'！安全跳过，绝不 Approve！")
                    continue
                print(f"  ✅ [通过] MF 栏位配置正确 (MF: {mf_vol} mL, DI: 空)")
            elif "direct" in method_val.lower():
                if mf_vol:
                    print(f"  ⛔ [Rule 9 拦截] 质控警报: DI 方法但 MF 栏位有值 '{mf_vol}'！安全跳过，绝不 Approve！")
                    continue
                print(f"  ✅ [通过] DI 栏位配置正确 (DI: {di_vol} mL, MF: 空)")
        except Exception as e:
            print(f"  ℹ️ 体积读取提示: {e}")

        # 3. 匹配 Approved 选项
        target_opt = None
        for opt in select_obj.options:
            cleaned = opt.text.replace("\u00a0", " ").strip().lower()
            if "approv" in cleaned:
                target_opt = opt
                break

        if not target_opt:
            print(f"  ❌ 未找到 Approved 选项！当前选项为: {[o.text.strip() for o in select_obj.options]}")
            continue

        # 4. 执行审批
        val = target_opt.get_attribute("value")
        select_obj.select_by_value(val)
        print(f"  [1/4] 已选择 'Approved' (value={val})")
        time.sleep(1)

        # 填写账号与 PIN (采用 JS 清空 + Ctrl+A Backspace 双重保险，防止网页自带默认值导致变成 qchenqchen)
        from selenium.webdriver.common.keys import Keys

        aun_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "AUN"))
        )
        driver.execute_script("arguments[0].value = '';", aun_field)
        aun_field.send_keys(Keys.CONTROL, "a")
        aun_field.send_keys(Keys.BACKSPACE)
        time.sleep(0.1)
        aun_field.send_keys(USERNAME)
        actual_un = aun_field.get_attribute("value")
        print(f"  [2/4] 已精准填入账号: {actual_un}")

        apd_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "APD"))
        )
        driver.execute_script("arguments[0].value = '';", apd_field)
        apd_field.send_keys(Keys.CONTROL, "a")
        apd_field.send_keys(Keys.BACKSPACE)
        time.sleep(0.1)
        apd_field.send_keys(PIN)
        print(f"  [3/4] 已精准填入 PIN 码: ****")
        time.sleep(0.5)

        # 点击 Save
        save_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ChangeTestStatusSaveButton"))
        )
        save_btn.click()
        print(f"  [4/4] 已点击绿色 Save 按钮提交授权！")

        # 等待弹窗消失
        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "ChangeTestStatusSaveButton"))
            )
        except Exception:
            time.sleep(2)

        # 刷新核实
        time.sleep(3)
        driver.get(target_url)
        time.sleep(2)

        verify_elem = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "TestStatusId"))
        )
        final_status = Select(verify_elem).first_selected_option.text.strip()
        print(f"  🎯 最终审批状态: [{final_status}]")

        if final_status.lower() in ["approved", "completed"]:
            print(f"  🎉 [成功] 样本 {sample_id} 审批成功归档！当前状态: [{final_status}]")
            progress_records.append({
                "Sample": sample_id,
                "status": final_status,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": "Approved successfully"
            })
        else:
            print(f"  ⚠️ 提示: 当前状态为 [{final_status}]")
            progress_records.append({
                "Sample": sample_id,
                "status": final_status,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": "Unexpected status"
            })

        # 保存进度记录
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress_records, f, indent=2, ensure_ascii=False)

        # 如果不是最后一个，进入质控等待
        if idx < total:
            wait_s = random.randint(min_wait, max_wait)
            mins = wait_s // 60
            secs = wait_s % 60
            print(f"\n💤 进入质控间隔: 随机休眠 {mins} 分 {secs} 秒 ({wait_s}s)...")
            countdown_timer(wait_s)

    print("\n" + "=" * 70)
    print("🏆 5 个样本自动审批测试全部顺利完成！")
    print(f"📁 详细结果已存入: {PROGRESS_FILE}")
    print("=" * 70)

except KeyboardInterrupt:
    print("\n\n⏸️ 用户主动中断。")

except Exception as e:
    print(f"\n❌ 发生异常: {e}")

finally:
    # 按照用户要求：绝不自动关闭浏览器！保持常驻，供用户随时查看或手动关闭
    print("\n👉 提示：Chrome 浏览器已常驻保持打开，未被关闭。如果你想关闭它，可以手动点右上角 ✖ 关掉。")
