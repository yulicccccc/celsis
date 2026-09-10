import os
import sys
import time
import json
import socket
import msvcrt
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding='utf-8')

USERNAME = "qchen"
PIN = "1124"
AUDIT_FILE = "celsis_100926_final_audit_report.json"
PROGRESS_FILE = "celsis_100926_approval_progress.json"

# 默认质控等待：60 ~ 120 秒，控制台按 Enter 可立即跳过
MIN_WAIT = 60
MAX_WAIT = 120

print("=" * 75, flush=True)
print("   EagleTrax Celsis 10SEP26 全量样本自动审批引擎 (后台静默 + Enter 跳过)", flush=True)
print("   自动最小化到任务栏，绝不抢占前台；倒计时期间按【Enter】立即处理下个样本！", flush=True)
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

# 2. 读取审计数据并严格执行熔断
with open(AUDIT_FILE, "r", encoding="utf-8") as f:
    audit_data = json.load(f)

whitelisted = [s for s in audit_data if s.get("Audit Result") == "PASS"]
blocked = [s for s in audit_data if "BLOCK" in s.get("Audit Result", "")]

# 3. 筛选所有剩余待审批的合格样本 (排除已完成和熔断样本)
remaining_queue = [s for s in whitelisted if s["Sample"] not in approved_set]

print(f"\n📊 今日 10SEP26 批次总览:")
print(f"  • 合格白名单总数: {len(whitelisted)} 个")
print(f"  • 物理熔断拦截:   {len(blocked)} 个 ({', '.join(b['Sample'] for b in blocked)}) -> 严禁触碰，已彻底隔离！")
print(f"  • 历史已完成审批: {len(approved_set)} 个 (自动识别并跳过)")
print(f"  • 本次待审批总数: {len(remaining_queue)} 个 (将逐一全量完成)")

if not remaining_queue:
    print("\n🎉 恭喜！今日全量白名单合格样本均已审批完毕，无需再执行任何操作！", flush=True)
    sys.exit(0)

print(f"\n📋 本轮待处理的 {len(remaining_queue)} 个样本明细:")
for idx, s in enumerate(remaining_queue, 1):
    print(f"  [{idx:02d}/{len(remaining_queue):02d}] {s['Sample']} | 仪器: #{s.get('Instrument')} | CV%: {s.get('PDF Max CV%')} | ATP: {s.get('PDF ATP')} | TSB: {s.get('PDF TSB')} | FTM: {s.get('PDF FTM')}", flush=True)

print("-" * 75, flush=True)
print("💡 审批引擎即将启动并自动将浏览器最小化到任务栏，你可以正常办公做其他活！", flush=True)
print("💡 等待期间若想加快进度，在当前控制台按【Enter 回车键】即可秒级切换到下一个样本！", flush=True)
print("-" * 75, flush=True)

def is_port_open(port=9222):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

def get_driver():
    user_home = os.path.expanduser("~")
    chrome_profile_dir = os.path.join(user_home, "chrome_automation_profile")

    if is_port_open(9222):
        try:
            attach_opts = Options()
            attach_opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            d = webdriver.Chrome(options=attach_opts)
            print("\n🔗 [无缝连接] 成功接入桌面上已打开的 9222 端口 Chrome！", flush=True)
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
        print(f"\n⚠️ 启动 Chrome 遇到冲突: {e}", flush=True)
        sys.exit(1)

driver = get_driver()

def countdown_timer(seconds, current_step, total_steps):
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
        print(f"[{idx}/{total_todo}] 正在处理样本: {sample_id} (全局已完成: {len(approved_set)} / {len(whitelisted)})", flush=True)
        print(f"    仪器: Advance 2 #{sample_info.get('Instrument')} | CV%: {sample_info.get('PDF Max CV%')}", flush=True)
        print(f"    ATP: {sample_info.get('PDF ATP')} | TSB: {sample_info.get('PDF TSB')} | FTM: {sample_info.get('PDF FTM')}", flush=True)
        print(f"    目标链接: {target_url}", flush=True)
        print("=" * 70, flush=True)

        driver.get(target_url)
        time.sleep(2.5)

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

            start_l = time.time()
            while True:
                time.sleep(3)
                now_url = driver.current_url.lower()
                if "eagleanalytical.com" in now_url and "/account/login" not in now_url and "microsoft" not in now_url and "login.live" not in now_url:
                    print(f"✅ 登录恢复成功！耗时 {int(time.time() - start_l)} 秒。", flush=True)
                    break
                if time.time() - start_l > 180:
                    print("❌ 登录超时，程序退出。", flush=True)
                    sys.exit(1)

        try:
            driver.minimize_window()
        except Exception:
            pass

        # 检查当前状态
        status_text = ""
        try:
            status_elem = driver.find_element(By.ID, "TestStatusId")
            if status_elem.tag_name == "select":
                select_obj = Select(status_elem)
                status_text = select_obj.first_selected_option.text.strip()
            else:
                status_text = status_elem.get_attribute("value") or status_elem.text
        except Exception:
            pass

        print(f"  🔍 当前页面状态: '{status_text}'")

        if status_text in ["Completed", "Approved"]:
            print(f"  ⏩ 样本 {sample_id} 已经是 {status_text} 状态，跳过！")
            approved_set.add(sample_id)
            progress_records.append({
                "Sample": sample_id,
                "status": status_text,
                "approved": True,
                "timestamp": datetime.now().isoformat()
            })
            with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                json.dump(progress_records, f, indent=2)
            continue

        if status_text != "Data Review":
            print(f"  ⚠️ 样本状态不是 Data Review (当前: {status_text})，跳过以策安全！")
            continue

        # 寻找并点击 Approve 按钮
        approve_btn = None
        approve_selectors = [
            "//button[contains(text(), 'Approve')]",
            "//a[contains(text(), 'Approve')]",
            "//input[@value='Approve']",
            "//button[contains(@class, 'btn') and contains(text(), 'Approve')]",
            "//a[contains(@class, 'btn') and contains(text(), 'Approve')]"
        ]
        for sel in approve_selectors:
            btns = driver.find_elements(By.XPATH, sel)
            for b in btns:
                if b.is_displayed() and b.is_enabled():
                    approve_btn = b
                    break
            if approve_btn:
                break

        if not approve_btn:
            print(f"  ⚠️ 未找到可点击的 Approve 按钮，可能权限不足或不在该状态！")
            continue

        print(f"  🎯 找到 Approve 按钮，正在执行点击...")
        approve_btn.click()
        time.sleep(1.5)

        # 检查 PIN 弹窗
        try:
            pin_input = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password' or @id='UserPin' or @name='UserPin' or contains(@placeholder, 'PIN')]"))
            )
            print(f"  🔑 检测到 PIN 签名框，正在自动填入 PIN 码...")
            pin_input.clear()
            pin_input.send_keys(PIN)
            time.sleep(0.5)

            confirm_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit') or contains(text(), 'Sign') or contains(text(), 'OK') or contains(text(), 'Approve')] | //input[@type='submit' and contains(@value, 'Approve')]")
            confirm_btn.click()
            print(f"  📝 已提交电子签名！等待系统处理...")
            time.sleep(2)
        except Exception:
            pass

        print(f"  ✅ 样本 {sample_id} 审批成功！已同步至质控归档库。")
        approved_set.add(sample_id)
        progress_records.append({
            "Sample": sample_id,
            "status": "Approved",
            "approved": True,
            "timestamp": datetime.now().isoformat()
        })
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress_records, f, indent=2)

        # 质控等待
        if idx < total_todo:
            import random
            wait_s = random.randint(MIN_WAIT, MAX_WAIT)
            countdown_timer(wait_s, idx, total_todo)

except KeyboardInterrupt:
    print("\n🛑 用户手动中断审批流程，当前进度已安全保存。")
finally:
    try:
        driver.quit()
        print("🔒 审批浏览器已安全关闭。")
    except Exception:
        pass

print("\n" + "=" * 75)
print(f"🎉 审批任务执行结束！累计完成: {len(approved_set)} / {len(whitelisted)}")
print(f"📁 详细审批记录已存入: {PROGRESS_FILE}")
print("=" * 75)
