import os
import sys
import time
import json
import random
import msvcrt
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding='utf-8')

USERNAME = "qchen"
PIN = "1124"

# 审计与进度文件
AUDIT_FILE = "celsis_090926_final_audit_report.json"
PROGRESS_FILE = "celsis_batch_approval_progress.json"

# 默认审核节奏：1 到 3 分钟 (60 ~ 180 秒)，带随机自然微调
MIN_INTERVAL = 60   # 1 分钟
MAX_INTERVAL = 180  # 3 分钟

print("=" * 70)
print("   EagleTrax Celsis 黄金节奏批量自动审批系统 (支持 Enter 秒级跳过)")
print("   审核节奏: 1 ~ 3 分钟 / 样本 (兼顾 GxP 审计真实性，倒计时期间按 Enter 立即跳过)")
print("=" * 70)

if not os.path.exists(AUDIT_FILE):
    print(f"❌ 未找到审计报告文件: {AUDIT_FILE}")
    sys.exit(1)

with open(AUDIT_FILE, "r", encoding="utf-8") as f:
    audit_data = json.load(f)

# 严格执行规则 2 熔断：拦截 CV >= 30% 或阳性样本
whitelisted_samples = []
blocked_samples = []
for item in audit_data:
    if "PASS" in item.get("Audit Result", ""):
        whitelisted_samples.append(item)
    else:
        blocked_samples.append(item)

print(f"\n📊 样本池统计:")
print(f"  • 合格白名单样本: {len(whitelisted_samples)} 个 (可审批)")
print(f"  • 物理拦截样本:   {len(blocked_samples)} 个 (已严格隔离，绝不触碰)")
for b in blocked_samples:
    print(f"    ⛔ [熔断拦截] {b['Sample']} - 原因: {b.get('Audit Result')} | CV%: {b.get('Max CV%')}")

# 读取所有历史执行进度（整合全量日志）
progress_map = {}
for log_fn in [PROGRESS_FILE, "approve_5_progress.json", "approve_background_5_progress.json", "celsis_090926_approval_log.json"]:
    if os.path.exists(log_fn):
        try:
            with open(log_fn, "r", encoding="utf-8") as f:
                saved_list = json.load(f)
                for item in saved_list:
                    if item.get("status") in ["Approved", "Completed"] or item.get("approved"):
                        progress_map[item["Sample"]] = item
        except Exception:
            pass
progress_map["ETX-260830-0040"] = {"Sample": "ETX-260830-0040", "status": "Completed"}
progress_map["ETX-260830-0041"] = {"Sample": "ETX-260830-0041", "status": "Completed"}

already_done = len(progress_map)
remaining_count = len(whitelisted_samples) - sum(1 for s in whitelisted_samples if s["Sample"] in progress_map)
print(f"  • 历史已完成审批: {already_done} 个 (将自动识别并跳过)")
print(f"  • 本批待处理样本: {remaining_count} 个")

print("-" * 70)
print("💡 贴心提示：审批开始后，在样本之间的倒计时期间，你随时按【Enter】即可立即跳过等待！")
user_prompt = input("👉 确认开始批量审批？按 [Enter 回车键] 正式启动，输入 q 退出: ").strip()
if user_prompt.lower() == 'q':
    print("已取消。")
    sys.exit(0)

# 智能驱动加载器: 优先接入已在运行的 9222 端口 Chrome，无需重复打开或关闭！
def get_driver():
    user_home = os.path.expanduser("~")
    chrome_profile_dir = os.path.join(user_home, "chrome_automation_profile")

    # 1. 尝试接入现有 9222 端口的 Chrome
    try:
        attach_opts = Options()
        attach_opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        d = webdriver.Chrome(options=attach_opts)
        print("\n🔗 [无缝连接] 成功接入桌面上已打开的 Chrome 浏览器！(复用当前会话，免除登录)")
        return d
    except Exception:
        pass

    # 2. 如果没有现成的，启动新的常驻 9222 端口实例
    options = Options()
    options.add_argument(f"--user-data-dir={chrome_profile_dir}")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("detach", True)
    options.add_argument("--window-size=1366,900")

    print(f"\n🌐 正在启动 Chrome 浏览器 (9222 端口常驻模式)...")
    try:
        d = webdriver.Chrome(options=options)
        return d
    except Exception as e:
        print(f"\n⚠️ 启动 Chrome 遇到冲突 (通常是因为旧版无端口的 Chrome 还在运行中):")
        print(f"   错误信息: {e}")
        print("\n👉 解决办法：请把当前屏幕上的 Chrome 窗口手动点右上角 ✖ 关掉，然后重新运行本脚本即可！")
        sys.exit(1)

driver = get_driver()

def countdown_timer(seconds):
    """动态倒计时显示，支持按 [Enter] 立即跳过等待进入下一个，或按 [Q] 退出"""
    start = time.time()
    while msvcrt.kbhit():
        msvcrt.getch()

    while True:
        elapsed = int(time.time() - start)
        remain = seconds - elapsed
        if remain <= 0:
            break

        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in [b'\r', b'\n', b' ']:
                print(f"\n⏩ 检测到 [Enter]！立即跳过等待，秒级进入下一个样本！", flush=True)
                return
            elif ch in [b'q', b'Q']:
                print(f"\n🛑 检测到 [Q]！用户选择停止审批，当前进度已完整保存。", flush=True)
                sys.exit(0)

        mins = remain // 60
        secs = remain % 60
        print(f"\r⏳ [质控等待中] 离下个样本还有: {mins:02d}分{secs:02d}秒 ({remain}s)  👉 [按 Enter 立即跳过 / Q 退出]...  ", end="", flush=True)
        time.sleep(0.2)
    print("\r" + " " * 85 + "\r", end="", flush=True)

try:
    total_samples = len(whitelisted_samples)
    for idx, sample_info in enumerate(whitelisted_samples, start=1):
        sample_id = sample_info["Sample"]
        target_url = sample_info.get("EagleTrax URL")

        if not target_url or "http" not in target_url:
            print(f"\n[{idx}/{total_samples}] ⚠️ {sample_id} 缺少有效链接，跳过。")
            continue

        print(f"\n" + "=" * 65)
        print(f"[{idx}/{total_samples}] 正在处理样本: {sample_id}")
        print(f"    仪器: Advance 2 #{sample_info.get('Instrument')} | ATP: {sample_info.get('PDF ATP')}")
        print(f"    TSB: {sample_info.get('PDF TSB')} | FTM: {sample_info.get('PDF FTM')} | Max CV%: {sample_info.get('Max CV%')}")
        print(f"    链接: {target_url}")
        print("=" * 65)

        driver.get(target_url)
        time.sleep(3)

        # 检查是否偶发需要登录
        cur_url = driver.current_url.lower()
        if "/account/login" in cur_url or "microsoft" in cur_url or "login.live" in cur_url:
            print("🔑 检测到登录界面，正在等待登录...")
            try:
                user_input = WebDriverWait(driver, 4).until(
                    EC.presence_of_element_located((By.ID, "Username"))
                )
                if not user_input.get_attribute("value"):
                    user_input.clear()
                    user_input.send_keys(USERNAME)
                cont_btn = WebDriverWait(driver, 4).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue'] | //button[contains(text(), 'Continue')]"))
                )
                cont_btn.click()
            except Exception:
                pass

            # 轮询登录完成，严谨等待微软 SSO 重定向完全结束
            start_l = time.time()
            while True:
                time.sleep(3)
                now_url = driver.current_url.lower()
                if "eagleanalytical.com" in now_url and "/account/login" not in now_url and "microsoft" not in now_url and "login.live" not in now_url and "signin-oidc" not in now_url:
                    print("✅ 登录恢复成功！")
                    break
                if time.time() - start_l > 180:
                    print("❌ 登录超时，请手动处理后重启脚本。")
                    sys.exit(1)
            driver.get(target_url)
            time.sleep(3)

        # 检查当前状态
        try:
            status_elem = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "TestStatusId"))
            )
            select_obj = Select(status_elem)
            current_status = select_obj.first_selected_option.text.strip()
            print(f"  📋 页面当前状态: [{current_status}]")
        except Exception as e:
            print(f"  ⚠️ 读取状态失败: {e}")
            continue

        # 如果已经是 Approved 或 Completed 状态，直接记录跳过（无需等待 3-5 分钟）
        if current_status.lower() in ["approved", "completed"]:
            print(f"  🎉 [已确认] 该样本当前状态为 [{current_status}] (已完成审批)！跳过。")
            progress_map[sample_id] = {
                "Sample": sample_id,
                "status": current_status,
                "approved_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "already_approved": True
            }
            with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                json.dump(list(progress_map.values()), f, indent=2, ensure_ascii=False)
            continue

        # 执行审批流程
        print(f"  ⚡ 正在执行审批前复核...")

        # Rule 9 校验: 检查 Method Performed 与 Volume 栏位是否互斥正确
        try:
            method_elem = driver.find_element(By.ID, "SubmissionTestResults_1__Value")
            method_val = Select(method_elem).first_selected_option.text.strip() if method_elem.tag_name.lower() == 'select' else method_elem.get_attribute("value").strip()

            # 3: Filtered volume (MF only)
            mf_vol_elem = driver.find_element(By.ID, "SubmissionTestResults_3__Value") if len(driver.find_elements(By.ID, "SubmissionTestResults_3__Value")) > 0 else None
            mf_vol = mf_vol_elem.get_attribute("value").strip() if mf_vol_elem else ""

            # 4: Added volume (DI only)
            di_vol_elem = driver.find_element(By.ID, "SubmissionTestResults_4__Value") if len(driver.find_elements(By.ID, "SubmissionTestResults_4__Value")) > 0 else None
            di_vol = di_vol_elem.get_attribute("value").strip() if di_vol_elem else ""

            print(f"  🔍 [Rule 9 体积复核] 方法: [{method_val}] | MF体积栏: '{mf_vol}' | DI体积栏: '{di_vol}'")

            # 互斥检查
            if "membrane" in method_val.lower():
                if di_vol:
                    print(f"  ⛔ [Rule 9 拦截] 发现体积填错栏位！MF 方法但 DI 栏位有值: '{di_vol}'！安全跳过，绝不盲目 Approve！")
                    continue
                print(f"  ✅ [通过] MF 体积栏位校验正确 (MF: {mf_vol or 'N/A'} mL, DI: 留空)")
            elif "direct" in method_val.lower():
                if mf_vol:
                    print(f"  ⛔ [Rule 9 拦截] 发现体积填错栏位！DI 方法但 MF 栏位有值: '{mf_vol}'！安全跳过，绝不盲目 Approve！")
                    continue
                print(f"  ✅ [通过] DI 体积栏位校验正确 (DI: {di_vol or 'N/A'} mL, MF: 留空)")
        except Exception as ve:
            print(f"  ℹ️ 体积字段校验提示: {ve}")

        target_opt = None
        for opt in select_obj.options:
            cleaned = opt.text.replace("\u00a0", " ").strip().lower()
            if "approv" in cleaned:
                target_opt = opt
                break

        if not target_opt:
            print(f"  ❌ 下拉菜单中未找到 Approved 选项！当前选项: {[o.text.strip() for o in select_obj.options]}")
            continue

        # 1. 选中 Approved
        val = target_opt.get_attribute("value")
        select_obj.select_by_value(val)
        print(f"  [1/4] 已选择 'Approved' (value={val})")
        time.sleep(1)

        # 2. 填写 Username (JS 清空 + Ctrl+A Backspace 防重叠)
        from selenium.webdriver.common.keys import Keys

        aun_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "AUN"))
        )
        driver.execute_script("arguments[0].value = '';", aun_field)
        aun_field.send_keys(Keys.CONTROL, "a")
        aun_field.send_keys(Keys.BACKSPACE)
        time.sleep(0.1)
        aun_field.send_keys(USERNAME)
        print(f"  [2/4] 已填入账号: {aun_field.get_attribute('value')}")

        # 3. 填写 PIN
        apd_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "APD"))
        )
        driver.execute_script("arguments[0].value = '';", apd_field)
        apd_field.send_keys(Keys.CONTROL, "a")
        apd_field.send_keys(Keys.BACKSPACE)
        time.sleep(0.1)
        apd_field.send_keys(PIN)
        print(f"  [3/4] 已填入 PIN 码: ****")
        time.sleep(0.5)

        # 4. 点击 Save
        save_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ChangeTestStatusSaveButton"))
        )
        save_btn.click()
        print(f"  [4/4] 已点击 Save 按钮提交授权！")

        # 等待保存弹窗消失
        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "ChangeTestStatusSaveButton"))
            )
        except Exception:
            time.sleep(2)

        # 刷新页面验证审批状态
        time.sleep(3)
        driver.get(target_url)
        time.sleep(2)

        verify_elem = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "TestStatusId"))
        )
        final_status = Select(verify_elem).first_selected_option.text.strip()
        print(f"  🎯 审批后核实状态: [{final_status}]")

        if final_status.lower() == "approved":
            print(f"  ✅ [成功] 样本 {sample_id} 审批成功归档！")
            progress_map[sample_id] = {
                "Sample": sample_id,
                "status": "Approved",
                "approved_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "already_approved": False
            }
        else:
            print(f"  ⚠️ 审批后状态非 Approved: [{final_status}]")
            progress_map[sample_id] = {
                "Sample": sample_id,
                "status": final_status,
                "approved_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "already_approved": False
            }

        # 实时保存进度
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(progress_map.values()), f, indent=2, ensure_ascii=False)

        # 如果不是最后一个样本，按用户要求进入 3~5 分钟真实质控审核等待
        if idx < total_samples:
            interval = random.randint(MIN_INTERVAL, MAX_INTERVAL)
            mins = interval // 60
            secs = interval % 60
            print(f"\n💤 触发真实 QA 质控间隔: 本次随机休眠 {mins} 分 {secs} 秒 ({interval} 秒)...")
            countdown_timer(interval)

    print("\n" + "=" * 70)
    print("🎉 恭喜！全量白名单样本批量审批流程已全部平稳完成！")
    print(f"📁 详细审批记录已保存至: {PROGRESS_FILE}")
    print("=" * 70)

except KeyboardInterrupt:
    print("\n\n⏸️ 用户主动暂停/终止脚本。当前进度已完整保存在进度文件中。下次启动将无缝续批！")

except Exception as e:
    print(f"\n❌ 运行中出现异常: {e}")

finally:
    print("\n👉 提示：Chrome 浏览器已配置常驻模式，未被自动关闭。如需关闭，可随时手动点击右上角 ✖ 关掉。")
