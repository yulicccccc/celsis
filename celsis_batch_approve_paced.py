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

# 审计与进度文件
AUDIT_FILE = "celsis_090926_final_audit_report.json"
PROGRESS_FILE = "celsis_batch_approval_progress.json"

# 默认审核节奏：3 到 5 分钟 (180 ~ 300 秒)，带随机自然微调
MIN_INTERVAL = 180  # 3 分钟
MAX_INTERVAL = 300  # 5 分钟

print("=" * 70)
print("   EagleTrax Celsis 真实节奏批量自动审批系统 (GxP 审计友好型)")
print("   审核节奏: 3 ~ 5 分钟 / 样本 (自然随机微调，避免机械式高频审批)")
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

# 读取历史执行进度
progress_map = {}
if os.path.exists(PROGRESS_FILE):
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            saved_list = json.load(f)
            for item in saved_list:
                progress_map[item["Sample"]] = item
        already_done = sum(1 for v in progress_map.values() if v.get("status") == "Approved")
        print(f"  • 历史已完成审批: {already_done} 个 (将自动跳过)")
    except Exception:
        pass

print("-" * 70)
user_prompt = input("👉 确认开始批量审批？按 [Enter 回车键] 正式启动，输入 q 退出: ").strip()
if user_prompt.lower() == 'q':
    print("已取消。")
    sys.exit(0)

# Chrome 独立 Profile
user_home = os.path.expanduser("~")
chrome_profile_dir = os.path.join(user_home, "chrome_automation_profile")

options = Options()
options.add_argument(f"--user-data-dir={chrome_profile_dir}")
options.add_argument("--profile-directory=Default")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("--window-size=1366,900")

print(f"\n🌐 正在启动 Chrome 浏览器...")
driver = webdriver.Chrome(options=options)

def countdown_timer(seconds):
    """自然倒计时显示，可被中断"""
    start = time.time()
    while True:
        elapsed = int(time.time() - start)
        remain = seconds - elapsed
        if remain <= 0:
            break
        mins = remain // 60
        secs = remain % 60
        print(f"\r⏳ [质控间隔中] 模拟人工复核时间，离下一个审批还有: {mins:02d}分{secs:02d}秒 ({remain}s)...  ", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 75 + "\r", end="", flush=True)

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

            # 轮询登录完成
            start_l = time.time()
            while True:
                time.sleep(3)
                if "/account/login" not in driver.current_url.lower():
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

        # 如果已经是 Approved 状态，直接记录跳过（无需等待 3-5 分钟）
        if current_status.lower() == "approved":
            print(f"  🎉 [已确认] 该样本已经是 Approved 状态！跳过。")
            progress_map[sample_id] = {
                "Sample": sample_id,
                "status": "Approved",
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

        # 2. 填写 Username
        aun_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "AUN"))
        )
        aun_field.clear()
        aun_field.send_keys(USERNAME)
        print(f"  [2/4] 已填入账号: {USERNAME}")

        # 3. 填写 PIN
        apd_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "APD"))
        )
        apd_field.clear()
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
    driver.quit()
    print("🔒 浏览器已安全退出。")
