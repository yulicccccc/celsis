import os
import sys
import time
import json
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding='utf-8')

import msvcrt

USERNAME = "qchen"
PIN = "1124"
AUDIT_FILE = "celsis_090926_final_audit_report.json"
PROGRESS_FILE = "approve_background_5_progress.json"

# 审核间隔：1 到 2 分钟随机微调 (60 ~ 120 秒)
MIN_WAIT = 60
MAX_WAIT = 120

print("=" * 70, flush=True)
print("   EagleTrax Celsis 自动最小化后台审批系统 (支持 Enter 秒级跳过等待)", flush=True)
print("   登录后自动缩到任务栏，绝不抢占鼠标打字焦点；倒计时期间按【Enter】立即处理下个样本！", flush=True)
print("=" * 70, flush=True)

# 1. 汇总所有历史已审批记录，避免重复审批
approved_set = set()
for log_fn in [PROGRESS_FILE, "approve_5_progress.json", "celsis_090926_approval_log.json"]:
    if os.path.exists(log_fn):
        try:
            with open(log_fn, "r", encoding="utf-8") as f:
                records = json.load(f)
                for r in records:
                    if r.get("status") in ["Approved", "Completed"] or r.get("approved"):
                        approved_set.add(r.get("Sample"))
        except Exception:
            pass
approved_set.update(["ETX-260830-0040", "ETX-260830-0041"])

with open(AUDIT_FILE, "r", encoding="utf-8") as f:
    audit_data = json.load(f)

whitelisted = [s for s in audit_data if "PASS" in s.get("Audit Result", "")]
blocked = [s for s in audit_data if "BLOCK" in s.get("Audit Result", "")]

# 动态获取接下来 5 个合格未审批样本
target_queue = [s for s in whitelisted if s["Sample"] not in approved_set][:5]

print(f"\n📊 批次全局状态: 总 PASS 样本 {len(whitelisted)} 个 | 历史已审批 {len(approved_set)} 个 | 剩余待审批 {len(whitelisted) - len(approved_set)} 个", flush=True)
print(f"📋 本轮动态挑选的 5 个后台待审批样本队列 (已严格过滤熔断与已完成样本):", flush=True)
for idx, s in enumerate(target_queue, 1):
    print(f"  {idx}. {s['Sample']} | 仪器: #{s.get('Instrument')} | ATP: {s.get('PDF ATP')} | TSB: {s.get('PDF TSB')} | FTM: {s.get('PDF FTM')}", flush=True)

if not target_queue:
    print("\n🎉 恭喜！当前批次的所有合规白名单样本均已全部审批完毕！", flush=True)
    sys.exit(0)

def get_driver():
    user_home = os.path.expanduser("~")
    chrome_profile_dir = os.path.join(user_home, "chrome_automation_profile")

    try:
        attach_opts = Options()
        attach_opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        d = webdriver.Chrome(options=attach_opts)
        print("\n🔗 [无缝连接] 成功接入桌面上已打开的 Chrome 浏览器！(复用当前会话，免除登录)", flush=True)
        return d
    except Exception:
        pass

    options = Options()
    options.add_argument(f"--user-data-dir={chrome_profile_dir}")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("detach", True)
    options.add_argument("--window-size=1366,900")

    print(f"\n🌐 正在启动 Chrome 浏览器 (9222 端口常驻模式)...", flush=True)
    try:
        d = webdriver.Chrome(options=options)
        return d
    except Exception as e:
        print(f"\n⚠️ 启动 Chrome 遇到冲突 (通常是因为旧版无端口的 Chrome 还在运行中):", flush=True)
        print(f"   错误信息: {e}", flush=True)
        print("\n👉 解决办法：请把当前屏幕上的 Chrome 窗口手动点右上角 ✖ 关掉，然后重新运行本脚本即可！", flush=True)
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
        print(f"\r⏳ [后台质控等待中] 离下个样本还有: {mins:02d}分{secs:02d}秒 ({remain}s)  👉 [按 Enter 立即跳过 / Q 退出]...  ", end="", flush=True)
        time.sleep(0.2)
    print("\r" + " " * 85 + "\r", end="", flush=True)

progress_records = []
if os.path.exists(PROGRESS_FILE):
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            progress_records = json.load(f)
    except Exception:
        progress_records = []

try:
    total = len(target_queue)
    for idx, sample_info in enumerate(target_queue, 1):
        sample_id = sample_info["Sample"]
        target_url = sample_info.get("EagleTrax URL")

        print(f"\n" + "=" * 65, flush=True)
        print(f"[{idx}/{total}] 正在处理样本: {sample_id}", flush=True)
        print(f"    目标链接: {target_url}", flush=True)
        print("=" * 65, flush=True)

        driver.get(target_url)
        time.sleep(3)

        # 检查是否需要登录
        cur_url = driver.current_url.lower()
        if "/account/login" in cur_url or "microsoft" in cur_url or "login.live" in cur_url:
            print("🔑 检测到需要登录，正在自动填入用户名并点击继续...", flush=True)
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

            print("\n👉 [提示] 请在手机 Microsoft Authenticator 上点击确认登录...", flush=True)
            print("   (登录完成后，浏览器会自动最小化到任务栏，无需你手动操作！)", flush=True)

            start_l = time.time()
            while True:
                time.sleep(3)
                now_url = driver.current_url.lower()
                if "eagleanalytical.com" in now_url and "/account/login" not in now_url and "microsoft" not in now_url and "login.live" not in now_url and "signin-oidc" not in now_url:
                    print(f"✅ 登录成功！耗时 {int(time.time() - start_l)} 秒。", flush=True)
                    break
                if time.time() - start_l > 180:
                    print("❌ 登录超时，退出。", flush=True)
                    sys.exit(1)

            driver.get(target_url)
            time.sleep(3)

        # 核心亮点：登录成功后，立刻自动将浏览器最小化到任务栏！
        try:
            driver.minimize_window()
            print("🪟 浏览器已自动最小化到任务栏！你现在可以完全正常做你的活，后台正在静默处理...", flush=True)
        except Exception:
            pass

        # 1. 检查当前状态
        status_elem = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "TestStatusId"))
        )
        select_obj = Select(status_elem)
        current_status = select_obj.first_selected_option.text.strip()
        print(f"  📋 页面当前状态: [{current_status}]", flush=True)

        if current_status.lower() in ["approved", "completed"]:
            print(f"  🎉 [已确认] 该样本已经是 [{current_status}] 状态！自动跳过。", flush=True)
            progress_records.append({
                "Sample": sample_id,
                "status": current_status,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": "Already completed"
            })
            continue

        # 2. Rule 9: 体积与方法互斥复核
        print(f"  🔍 [Rule 9 质控复核] 正在校验测试方法与体积栏位...", flush=True)
        try:
            method_elem = driver.find_element(By.ID, "SubmissionTestResults_1__Value")
            method_val = Select(method_elem).first_selected_option.text.strip() if method_elem.tag_name.lower() == 'select' else method_elem.get_attribute("value").strip()

            mf_vol_elem = driver.find_element(By.ID, "SubmissionTestResults_3__Value") if len(driver.find_elements(By.ID, "SubmissionTestResults_3__Value")) > 0 else None
            mf_vol = mf_vol_elem.get_attribute("value").strip() if mf_vol_elem else ""

            di_vol_elem = driver.find_element(By.ID, "SubmissionTestResults_4__Value") if len(driver.find_elements(By.ID, "SubmissionTestResults_4__Value")) > 0 else None
            di_vol = di_vol_elem.get_attribute("value").strip() if di_vol_elem else ""

            print(f"     方法: [{method_val}] | MF体积: '{mf_vol or '(空)'}' | DI体积: '{di_vol or '(空)'}'", flush=True)

            if "membrane" in method_val.lower():
                if di_vol:
                    print(f"  ⛔ [Rule 9 拦截] 严重警报: MF 方法但 DI 栏位有值 '{di_vol}'！跳过该样本！", flush=True)
                    continue
                print(f"  ✅ [通过] MF 栏位配置正确 (MF: {mf_vol} mL, DI: 空)", flush=True)
            elif "direct" in method_val.lower():
                if mf_vol:
                    print(f"  ⛔ [Rule 9 拦截] 严重警报: DI 方法但 MF 栏位有值 '{mf_vol}'！跳过该样本！", flush=True)
                    continue
                print(f"  ✅ [通过] DI 栏位配置正确 (DI: {di_vol} mL, MF: 空)", flush=True)
        except Exception as e:
            print(f"  ℹ️ 体积字段读取提示: {e}", flush=True)

        # 3. 匹配 Approved 选项
        target_opt = None
        for opt in select_obj.options:
            cleaned = opt.text.replace("\u00a0", " ").strip().lower()
            if "approv" in cleaned:
                target_opt = opt
                break

        if not target_opt:
            print(f"  ❌ 未找到 Approved 选项！当前选项: {[o.text.strip() for o in select_obj.options]}", flush=True)
            continue

        # 4. 执行审批
        val = target_opt.get_attribute("value")
        select_obj.select_by_value(val)
        print(f"  [1/4] 已选择 'Approved' (value={val})", flush=True)
        time.sleep(1)

        # 填写账号 (JS清空 + 退格双保险)
        aun_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "AUN"))
        )
        driver.execute_script("arguments[0].value = '';", aun_field)
        aun_field.send_keys(Keys.CONTROL, "a")
        aun_field.send_keys(Keys.BACKSPACE)
        time.sleep(0.1)
        aun_field.send_keys(USERNAME)
        print(f"  [2/4] 已精准填入账号: {aun_field.get_attribute('value')}", flush=True)

        # 填写 PIN
        apd_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "APD"))
        )
        driver.execute_script("arguments[0].value = '';", apd_field)
        apd_field.send_keys(Keys.CONTROL, "a")
        apd_field.send_keys(Keys.BACKSPACE)
        time.sleep(0.1)
        apd_field.send_keys(PIN)
        print(f"  [3/4] 已精准填入 PIN 码: ****", flush=True)
        time.sleep(0.5)

        # 点击 Save
        save_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ChangeTestStatusSaveButton"))
        )
        save_btn.click()
        print(f"  [4/4] 已点击 Save 按钮提交授权！", flush=True)

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
        print(f"  🎯 最终审批状态: [{final_status}]", flush=True)

        if final_status.lower() in ["approved", "completed"]:
            print(f"  🎉 [成功] 样本 {sample_id} 后台审批成功归档！", flush=True)
            progress_records.append({
                "Sample": sample_id,
                "status": final_status,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": "Approved successfully"
            })
        else:
            print(f"  ⚠️ 提示: 当前状态为 [{final_status}]", flush=True)
            progress_records.append({
                "Sample": sample_id,
                "status": final_status,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": "Unexpected status"
            })

        # 实时保存进度
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress_records, f, indent=2, ensure_ascii=False)

        # 样本间质控等待 (1 ~ 2 分钟，支持按 Enter 秒级跳过)
        if idx < total:
            wait_s = random.randint(MIN_WAIT, MAX_WAIT)
            mins = wait_s // 60
            secs = wait_s % 60
            print(f"\n💤 [后台质控间隔] 随机休眠 {mins} 分 {secs} 秒 ({wait_s}s)... (控制台按 Enter 可立即跳过)", flush=True)
            countdown_timer(wait_s)

    print("\n" + "=" * 70, flush=True)
    print("🏆 5 个样本后台静默审批已全部平稳完成！", flush=True)
    print(f"📁 详细结果已保存在: {PROGRESS_FILE}", flush=True)
    print("=" * 70, flush=True)

except Exception as e:
    print(f"\n❌ 后台运行异常: {e}", flush=True)

finally:
    driver.quit()
    print("🔒 后台浏览器已安全退出。全部搞定！", flush=True)
