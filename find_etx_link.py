import os
import time
import json
from playwright.sync_api import sync_playwright

ETX_ID = "ETX-260826-0374"
user_data_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'pastdue_playwright_session')

print("====================================================")
print(f"  EagleTrax Link Finder: {ETX_ID}")
print("====================================================")

def run():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=False,
            viewport={'width': 1366, 'height': 850}
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        
        print(" -> Navigating to: https://etrax.eagleanalytical.com/Submission")
        page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="domcontentloaded")
        
        # 稳健判定：等待 4 秒观察是否触发微软 SSO 重定向
        print(" -> Checking authentication status...")
        time.sleep(3)
        
        url_now = page.url.lower()
        needs_login = (
            "/account/login" in url_now
            or "microsoft" in url_now
            or "login.live" in url_now
            or page.locator("input[name='Username'], input[name='loginfmt'], #i0116").count() > 0
        )
        
        if needs_login:
            print("\n====================================================")
            print("[ACTION REQUIRED] Please complete SSO/MFA in Chrome window...")
            print("====================================================")
            
            # 自动预填账号
            try:
                u_input = page.locator("input[name='Username'], input[name='loginfmt'], #i0116").first
                if u_input.count() > 0 and not u_input.input_value():
                    u_input.fill("qchen")
                    print(" -> Auto-filled 'qchen'")
                    time.sleep(0.5)
                    nxt = page.locator("#idSIButton9, input[type='submit'], button[type='submit']").first
                    if nxt.count() > 0:
                        nxt.click()
            except Exception:
                pass
                
            # 等待登录成功（直到离开登录域且回到 etrax 域名）
            start_t = time.time()
            while time.time() - start_t < 300:
                time.sleep(3)
                u = page.url.lower()
                if "etrax.eagleanalytical.com" in u and "/account/login" not in u and "microsoft" not in u:
                    print("\n[SUCCESS] Login detected! Re-entering /Submission...")
                    page.goto("https://etrax.eagleanalytical.com/Submission", wait_until="networkidle")
                    time.sleep(2)
                    break
                print(".", end="", flush=True)
            else:
                print("\n[TIMEOUT] Login timeout.")
                ctx.close()
                return
        else:
            print(" -> Session Cookie valid, authenticated directly!")

        # 等待搜索输入框渲染完成
        print(" -> Waiting for search box (#srchCriteria)...")
        search_box = page.wait_for_selector("#srchCriteria", timeout=30000)
        time.sleep(1)

        # 4. 清除已有过滤条件
        print(" -> Clearing search box...")
        try:
            clear_btn = page.locator("#ClearButton, button[title='Clear'], input[value='Clear']").first
            if clear_btn.count() > 0:
                clear_btn.click()
                time.sleep(1.5)
        except Exception as e:
            print(f" -> Info clearing: {e}")

        # 5. 输入目标样本号
        print(f" -> Entering ETX ID: {ETX_ID}")
        search_box.fill("")
        search_box.fill(ETX_ID)
        time.sleep(0.5)

        # 6. 点击 Find
        print(" -> Clicking Find button...")
        find_btn = page.locator("#FindButton, button:has-text('Find'), input[value='Find']").first
        find_btn.click()

        # 等待结果加载
        print(" -> Waiting for results...")
        try:
            page.wait_for_load_state("networkidle", timeout=12000)
        except Exception:
            pass
        time.sleep(3)

        # 7. 切换 Tests 标签页
        print(" -> Switching to 'Tests' tab...")
        try:
            tests_tab = page.locator("a[href='#SubmissionTests'], a:has-text('Tests')").first
            if tests_tab.count() > 0:
                tests_tab.click()
                time.sleep(2)
        except Exception as e:
            print(f" -> Tab info: {e}")

        # 8. 抓取表格行并定位 Celsis Sterility Test
        print(" -> Parsing results table...")
        rows = page.locator("#SubmissionTestList table tbody tr, table tbody tr").all()
        print(f" -> Found {len(rows)} rows.")

        found_result = None
        for idx, r in enumerate(rows):
            r_text = r.inner_text().strip()
            print(f"    Row {idx+1}: {r_text[:70]}...")
            
            links = r.locator("a").all()
            for l in links:
                href = l.get_attribute("href") or ""
                txt = l.inner_text().strip()
                if "/SubmissionTest/Details/" in href:
                    full_url = href if href.startswith("http") else f"https://etrax.eagleanalytical.com{href}"
                    if "celsis" in txt.lower() or "celsis" in r_text.lower():
                        found_result = {
                            "etx_id": ETX_ID,
                            "test_name": txt or "Celsis Sterility Test",
                            "url": full_url,
                            "row_text": r_text
                        }
                        break
            if found_result:
                break

        # 兜底：直接扫描整个页面内符合条件的详情链接
        if not found_result:
            all_links = page.locator("a[href*='/SubmissionTest/Details/']").all()
            for l in all_links:
                href = l.get_attribute("href") or ""
                txt = l.inner_text().strip()
                full_url = href if href.startswith("http") else f"https://etrax.eagleanalytical.com{href}"
                if "celsis" in txt.lower() or len(all_links) == 1:
                    found_result = {
                        "etx_id": ETX_ID,
                        "test_name": txt or "Celsis Sterility Test",
                        "url": full_url,
                        "row_text": "Found via direct scan"
                    }
                    break

        page.screenshot(path="find_etx_link_screenshot.png")
        
        if found_result:
            print("\n" + "="*60)
            print(f"  TARGET LINK RESOLVED SUCCESSFULLY!")
            print(f"  ETX ID:    {found_result['etx_id']}")
            print(f"  Test Name: {found_result['test_name']}")
            print(f"  URL:       {found_result['url']}")
            print("="*60 + "\n")
            with open("etx_link_result.json", "w", encoding="utf-8") as f:
                json.dump(found_result, f, indent=2)
        else:
            print(f"\n[FAILED] Could not locate link for {ETX_ID}")

        print("Finished! Closing browser in 3 seconds...")
        time.sleep(3)
        ctx.close()

if __name__ == '__main__':
    run()
