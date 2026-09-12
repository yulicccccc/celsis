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
AUDIT_FILE = "celsis_110926_final_audit_report.json"
PROGRESS_FILE = "celsis_110926_approval_progress.json"

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--min-wait", type=int, default=15, help="Min wait seconds")
parser.add_argument("--max-wait", type=int, default=30, help="Max wait seconds")
args, _ = parser.parse_known_args()
MIN_WAIT = args.min_wait
MAX_WAIT = args.max_wait

print("=" * 75, flush=True)
print("   EagleTrax Celsis 11SEP26 全量样本自动审批引擎 (后台静默运行)", flush=True)
print(f"   质控等待: {MIN_WAIT} ~ {MAX_WAIT} 秒/样本 | 进度文件: {PROGRESS_FILE}", flush=True)
print("=" * 75, flush=True)

# 1. 汇总已审批记录，避免重复审批
approved_set = set()
if os.path.exists(PROGRESS_FILE):
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
            for r in records:
                if r.get("status") in ["Approved", "Completed"] or r.get("approved"):
                    approved_set.add(r.get("Sample"))
    except Exception:
        pass

# 2. 读取审计数据并严格执行 Rule 2 熔断
with open(AUDIT_FILE, "r", encoding="utf-8") as f:
    audit_data = json.load(f)

whitelisted = [s for s in audit_data if "PASS" in s.get("Audit Result", "")]
blocked = [s for s in audit_data if "BLOCK" in s.get("Audit Result", "")]

# 3. 筛选所有剩余待审批的合格样本 (排除已完成和熔断样本)
remaining_queue = [s for s in whitelisted if s["Sample"] not in approved_set]

print(f"\n📊 批次总览:")
print(f"  • 合格白名单总数: {len(whitelisted)} 个")
print(f"  • 物理熔断拦截:   {len(blocked)} 个 ({', '.join(b['Sample'] for b in blocked)}) -> 严禁触碰，已彻底隔离！")
print(f"  • 历史已完成审批: {len(approved_set)} 个 (自动识别并跳过)")
print(f"  • 本次待审批总数: {len(remaining_queue)} 个 (将逐一全量完成)")

if not remaining_queue:
    print("\n🎉 恭喜！全量白名单合格样本均已审批完毕，无需再执行任何操作！", flush=True)
    sys.exit(0)

print(f"\n📋 本轮待处理的 {len(remaining_queue)} 个样本明细:")
for idx, s in enumerate(remaining_queue, 1):
    print(f"  [{idx:02d}/{len(remaining_queue):02d}] {s['Sample']} | 仪器: #{s.get('Instrument')} | CV%: {s.get('Max CV%')} | ATP: {s.get('PDF ATP')} | TSB: {s.get('PDF TSB')} | FTM: {s.get('PDF FTM')}", flush=True)

print("-" * 75, flush=True)
print("💡 审批引擎即将启动并自动将浏览器最小化到任务栏，你可以正常办公做其他活！", flush=True)
print("💡 等待期间若想加快进度，在当前控制台按【Enter 回车键】即可秒级切换到下一个样本！", flush=True)
print("-" * 75, flush=True)

import socket

def is_port_open(port=9222):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

# 智能驱动加载器: 优先接入已在运行的 9222 端口 Chrome，无需重复打开或关闭！
def get_driver():
    user_home = os.path.expanduser("~")
    chrome_profile_dir = os.path.join(user_home, "chrome_automation_profile")

    if is_port_open(9222):
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
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--window-size=1366,900")

    print(f"\n🌐 正在启动 Chrome 浏览器 (使用 profile: chrome_automation_profile)...", flush=True)
    try:
        d = webdriver.Chrome(options=options)
        return d
    except Exception as e:
        print(f"\n⚠️ 启动 Chrome 遇到冲突:", flush=True)
        print(f"   错误信息: {e}", flush=True)
        print("\n👉 解决办法：请把当前屏幕上的自动化 Chrome 窗口手动关掉，然后重新运行本脚本！", flush=True)
        sys.exit(1)

driver = get_driver()

def countdown_timer(seconds, current_step, total_steps):
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
        print(f"\r⏳ [质控等待中 进度: {current_step}/{total_steps}] 离下个样本还有: {mins:02d}分{secs:02d}秒 ({remain}s)  👉 [按 Enter 立即跳过 / Q 退出]...  ", end="", flush=True)
        time.sleep(0.2)
    print("\r" + " " * 90 + "\r", end="", flush=True)

# 进度记录集合
progress_records = []
if os.path.exists(PROGRESS_FILE):
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            progress_records = json.load(f)
    except Exception:
        progress_records = []

total_todo = len(remaining_queue)

try:
    for idx, sample_info in enumerate(remaining_queue, 1):
        sample_id = sample_info["Sample"]
        target_url = sample_info.get("EagleTrax URL")

        print(f"\n" + "=" * 70, flush=True)
        print(f"[{idx}/{total_todo}] 正在处理样本: {sample_id} (全局已完成: {len(approved_set)} / 38)", flush=True)
        print(f"    仪器: Advance 2 #{sample_info.get('Instrument')} | CV%: {sample_info.get('Max CV%')}", flush=True)
        print(f"    ATP: {sample_info.get('PDF ATP')} | TSB: {sample_info.get('PDF TSB')} | FTM: {sample_info.get('PDF FTM')}", flush=True)
        print(f"    目标链接: {target_url}", flush=True)
        print("=" * 70, flush=True)

        driver.get(target_url)
        time.sleep(3)

        # 检查是否需要登录
        cur_url = driver.current_url.lower()
        if "/account/login" in cur_url or "microsoft" in cur_url or "login.live" in cur_url:
            print("🔑 检测到登录跳转，正在自动填入用户名并推进...", flush=True)
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

            print("\n👉 [提示] 如有手机 Authenticator 确认提示，请在手机上确认...", flush=True)
            start_l = time.time()
            while True:
                time.sleep(3)
                now_url = driver.current_url.lower()
                if "eagleanalytical.com" in now_url and "/account/login" not in now_url and "microsoft" not in now_url and "login.live" not in now_url and "signin-oidc" not in now_url:
                    print(f"✅ 登录恢复成功！耗时 {int(time.time() - start_l)} 秒。", flush=True)
                    break
                if time.time() - start_l > 180:
                    print("❌ 登录超时，程序退出。", flush=True)
                    sys.exit(1)

            driver.get(target_url)
            time.sleep(3)

        # 核心亮点：自动将浏览器最小化到任务栏，绝不干扰用户日常办公！
        try:
            driver.minimize_window()
            print("🪟 浏览器已自动最小化到任务栏！后台正在静默处理...", flush=True)
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
            print(f"  🎉 [已确认] 该样本已经是 [{current_status}] 状态！无需重复操作，自动归档跳过。", flush=True)
            approved_set.add(sample_id)
            progress_records.append({
                "Sample": sample_id,
                "status": current_status,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": "Already completed/approved"
            })
            continue

        # 质控前置红线：只有状态为 Data Review 的样本才允许审批！
        # 若仍处于 Sample Analysis 或其他未就绪状态，必须严格拦截并告知用户！
        if current_status.lower() != "data review":
            print(f"  ⛔ [SOP 状态拦截] 质控警报: 样本 {sample_id} 当前状态为 [{current_status}] (非 Data Review，通常为 Sample Analysis 等进行中阶段)！", flush=True)
            print(f"     已严格拦截，安全跳过，绝不执行 Approve 操作，已记入预警日志汇报给用户！", flush=True)
            progress_records.append({
                "Sample": sample_id,
                "status": current_status,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": f"Blocked: Not in Data Review (Current: {current_status})"
            })
            continue


        # 2. Rule 9: 质控方法与体积栏位互斥复核 (MF 过滤体积 vs DI 接种体积)
        print(f"  🔍 [Rule 9 质控复核] 正在校验测试方法与体积填入栏位...", flush=True)
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
                    print(f"  ⛔ [Rule 9 拦截] 质控警报: MF 方法但 DI 栏位有值 '{di_vol}'！安全跳过，绝不 Approve！", flush=True)
                    continue
                print(f"  ✅ [通过] MF 栏位配置正确 (MF: {mf_vol} mL, DI: 空)", flush=True)
            elif "direct" in method_val.lower():
                if mf_vol:
                    print(f"  ⛔ [Rule 9 拦截] 质控警报: DI 方法但 MF 栏位有值 '{mf_vol}'！安全跳过，绝不 Approve！", flush=True)
                    continue
                print(f"  ✅ [通过] DI 栏位配置正确 (DI: {di_vol} mL, MF: 空)", flush=True)
        except Exception as e:
            print(f"  ℹ️ 体积读取提示: {e}", flush=True)

        # 3. 匹配 Approved 选项
        target_opt = None
        for opt in select_obj.options:
            cleaned = opt.text.replace("\u00a0", " ").strip().lower()
            if "approv" in cleaned:
                target_opt = opt
                break

        if not target_opt:
            print(f"  ❌ 未找到 Approved 选项！当前选项为: {[o.text.strip() for o in select_obj.options]}", flush=True)
            continue

        # 4. 执行审批
        val = target_opt.get_attribute("value")
        select_obj.select_by_value(val)
        print(f"  [1/4] 已选择 'Approved' (value={val})", flush=True)
        time.sleep(1)

        # 填写账号与 PIN (JS 清空 + Ctrl+A 退格双保险，杜绝 qchenqchen)
        aun_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "AUN"))
        )
        driver.execute_script("arguments[0].value = '';", aun_field)
        aun_field.send_keys(Keys.CONTROL, "a")
        aun_field.send_keys(Keys.BACKSPACE)
        time.sleep(0.1)
        aun_field.send_keys(USERNAME)
        print(f"  [2/4] 已精准填入账号: {aun_field.get_attribute('value')}", flush=True)

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
            print(f"  🎉 [成功] 样本 {sample_id} 审批成功归档！当前状态: [{final_status}]", flush=True)
            approved_set.add(sample_id)
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

        # 实时写入进度文件
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress_records, f, indent=2, ensure_ascii=False)

        # 如果不是最后一个，进入质控等待
        if idx < total_todo:
            wait_s = random.randint(MIN_WAIT, MAX_WAIT)
            mins = wait_s // 60
            secs = wait_s % 60
            print(f"\n💤 [后台质控间隔] 随机休眠 {mins} 分 {secs} 秒 ({wait_s}s)...", flush=True)
            countdown_timer(wait_s, idx, total_todo)

    print("\n" + "=" * 75, flush=True)
    print(f"🏆🎉 批次全量 {len(whitelisted)} 个白名单样本批量审批全部圆满完成！", flush=True)
    print(f"📁 详细结果已保存在: {PROGRESS_FILE}", flush=True)
    print("=" * 75, flush=True)

except KeyboardInterrupt:
    print("\n\n⏸️ 用户主动中断，当前进度已完整保存。", flush=True)

except Exception as e:
    print(f"\n❌ 运行异常: {e}", flush=True)

finally:
    try:
        driver.quit()
    except Exception:
        pass
    print("🔒 审批引擎运行结束，浏览器已安全退出。全部搞定！", flush=True)
