import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding="utf-8")

NEW_15_SAMPLES = [
    "ETX-260831-0737",
    "ETX-260831-0557",
    "ETX-260901-0375",
    "ETX-260901-0673",
    "ETX-260901-0423",
    "ETX-260901-0376",
    "ETX-260901-0075",
    "ETX-260901-0265",
    "ETX-260901-0283",
    "ETX-260901-0365",
    "ETX-260901-0398",
    "ETX-260901-0469",
    "ETX-260901-0649",
    "ETX-260901-0666",
    "ETX-260901-0681"
]

OUTPUT_FILE = "celsis_090926_new_links.json"

chrome_profile_dir = os.path.join(os.path.expanduser("~"), "chrome_automation_profile")
opts = Options()
opts.add_argument(f"--user-data-dir={chrome_profile_dir}")
opts.add_argument("--profile-directory=Default")
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_argument("--window-size=1366,900")
driver = webdriver.Chrome(options=opts)

results = []

try:
    print(f"🚀 开始极速直连检索 {len(NEW_15_SAMPLES)} 个新样本链接...", flush=True)
    for idx, sid in enumerate(NEW_15_SAMPLES, 1):
        target_url = f"https://etrax.eagleanalytical.com/Submission/Details/{sid}"
        print(f"[{idx:02d}/{len(NEW_15_SAMPLES):02d}] 正在获取: {sid} ...", flush=True)
        try:
            driver.get(target_url)
            time.sleep(1.5)

            # 点击 Tests 选项卡
            try:
                tab = driver.find_element(By.XPATH, "//a[contains(text(), 'Tests') or @href='#Tests']")
                tab.click()
                time.sleep(0.8)
            except Exception:
                pass

            # 提取 Celsis Sterility Test 链接与状态
            links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Celsis')]")
            found_url = None
            for l in links:
                href = l.get_attribute("href") or ""
                if "/SubmissionTest/Details/" in href:
                    found_url = href if href.startswith("http") else f"https://etrax.eagleanalytical.com{href}"
                    break

            # 提取行状态
            status_text = "Data Review"
            try:
                rows = driver.find_elements(By.XPATH, "//table//tr[contains(., 'Celsis')]")
                if rows:
                    cols = rows[0].find_elements(By.TAG_NAME, "td")
                    # 查找包含 status select 或文本的列
                    for c in cols:
                        t = c.text.strip()
                        if t in ["Data Review", "Completed", "Approved", "Pending", "Cancelled"]:
                            status_text = t
                            break
            except Exception:
                pass

            if found_url:
                print(f"  ✅ 成功获取: {sid} -> {found_url} (状态: {status_text})", flush=True)
                results.append({
                    "Sample": sid,
                    "url": found_url,
                    "test_name": "Celsis Sterility Test",
                    "status": status_text
                })
            else:
                print(f"  ⚠️ 未找到 Celsis 链接: {sid}", flush=True)
                results.append({
                    "Sample": sid,
                    "url": None,
                    "status": "Not Found"
                })

            # 实时写入文件
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"  ❌ 出错 {sid}: {e}", flush=True)

    print("\n" + "=" * 70, flush=True)
    success_count = sum(1 for r in results if r.get("url"))
    print(f"🎉 直连检索全部完成！成功: {success_count} / {len(NEW_15_SAMPLES)} 个！", flush=True)
    print("=" * 70, flush=True)

finally:
    driver.quit()
