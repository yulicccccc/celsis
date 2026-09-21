import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

opts = Options()
opts.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
driver = webdriver.Chrome(options=opts)

with open('celsis_approval_timestamps.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
harvested = {d['Sample']: d for d in data}

to_retry = [
    ('ETX-260824-0077', '01SEP26.pdf'),
    ('ETX-260826-0368', '04SEP26.pdf')
]

for sid, pkt in to_retry:
    print(f'Retrying {sid}...')
    driver.get('https://etrax.eagleanalytical.com/Submission')
    time.sleep(1.5)
    try:
        driver.find_element(By.ID, 'ClearButton').click()
        time.sleep(0.5)
    except Exception:
        pass
    srch = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'srchCriteria')))
    srch.clear()
    srch.send_keys(sid)
    time.sleep(0.2)
    driver.find_element(By.ID, 'FindButton').click()
    time.sleep(2)
    try:
        driver.find_element(By.XPATH, "//a[@href='#SubmissionTests' or contains(text(), 'Tests')]").click()
        time.sleep(1.5)
    except Exception:
        pass
    links = driver.find_elements(By.XPATH, "//a[contains(@href, '/SubmissionTest/Details/')]")
    details_url = None
    for l in links:
        if 'celsis' in l.text.lower():
            details_url = l.get_attribute('href')
            break
    if not details_url and links:
        details_url = links[0].get_attribute('href')
    if details_url:
        driver.get(details_url)
        time.sleep(2)
        status_elem = driver.find_element(By.ID, 'TestStatusId')
        c_status = Select(status_elem).first_selected_option.text.strip()
        app_time, app_by, rev_time, rev_by = None, None, None, None
        rows = driver.find_elements(By.XPATH, "//table[contains(., 'Date Performed') or contains(., 'Event')]//tbody//tr")
        for tr in rows:
            cols = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, 'td')]
            if len(cols) >= 3:
                ev_name = cols[0].lower()
                if 'status changed - approved' in ev_name and not app_time:
                    app_time, app_by = cols[1], cols[2]
                elif 'status changed - data review' in ev_name and not rev_time:
                    rev_time, rev_by = cols[1], cols[2]
        entry = {
            'Sample': sid,
            'Packet': pkt,
            'found': True,
            'url': details_url,
            'current_status': c_status,
            'approved_time': app_time,
            'approved_by': app_by,
            'data_review_time': rev_time,
            'data_review_by': rev_by,
            'total_events_count': len(rows)
        }
        harvested[sid] = entry
        print(f'  Successfully harvested {sid}: Approved={app_time} by {app_by}')

with open('celsis_approval_timestamps.json', 'w', encoding='utf-8') as f:
    json.dump(list(harvested.values()), f, indent=2, ensure_ascii=False)

print("Retry completed.")
