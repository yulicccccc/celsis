import sys
import json
import re

sys.stdout.reconfigure(encoding="utf-8")

# 1. 仪器每日 ATP 对照 (锁定自 39 页 PDF 质控页)
DAILY_ATP = {
    "2222": 92047, # Page 3
    "2011": 95167  # Page 28
}

# 2. 读取 15 个新样本的检索链接
with open("celsis_090926_new_links.json", "r", encoding="utf-8") as f:
    new_links = json.load(f)
new_links_map = {item["Sample"]: item["url"] for item in new_links}

# 3. 读取已验证的历史链接 (包含前 39 个样本)
with open("celsis_090926_links_verified.json", "r", encoding="utf-8") as f:
    old_links = json.load(f)
for item in old_links:
    if item.get("etx_id") and item.get("url"):
        new_links_map[item["etx_id"]] = item["url"]

# 4. 提取 15 个新样本的真实读数
with open("celsis_090926_full_rows_extracted.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

NEW_SAMPLES_LIST = [
    # Advance 2 #2222
    "ETX-260831-0737", "ETX-260831-0557", "ETX-260901-0375", 
    "ETX-260901-0673", "ETX-260901-0423", "ETX-260901-0376",
    # Advance 2 #2011
    "ETX-260901-0075", "ETX-260901-0265", "ETX-260901-0283", 
    "ETX-260901-0365", "ETX-260901-0398", "ETX-260901-0469", 
    "ETX-260901-0649", "ETX-260901-0666", "ETX-260901-0681"
]

sample_stats = {}
for sid in NEW_SAMPLES_LIST:
    sample_stats[sid] = {
        "TSB": [],
        "FTM": [],
        "CVs": [],
        "inst": "2222" if sid in ["ETX-260831-0737", "ETX-260831-0557", "ETX-260901-0375", "ETX-260901-0673", "ETX-260901-0423", "ETX-260901-0376"] else "2011",
        "results": []
    }

PAGE_MEDIA = {
    20: "TSB", 21: "FTM",
    22: "TSB", 23: "FTM",
    24: "TSB", 25: "FTM",
    38: "TSB", 39: "FTM"
}

for p in pages:
    pnum = p["page_num"]
    media = PAGE_MEDIA.get(pnum)
    if not media:
        continue
    for r in p["rows"]:
        txt = r["raw_text"]
        for sid in NEW_SAMPLES_LIST:
            core_pattern = sid[4:]
            pattern_regex = core_pattern.replace("260901", r"260[09]01")
            if re.search(pattern_regex, txt, re.I):
                m_neg = re.search(r"(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*Negative", txt, re.I)
                if m_neg:
                    r1 = int(m_neg.group(1))
                    r2 = int(m_neg.group(2))
                    rlu = int(m_neg.group(3))
                    mean = (r1 + r2) / 2.0
                    std = abs(r1 - r2) / (2 ** 0.5)
                    cv = (std / mean) * 100.0 if mean > 0 else 0.0
                    sample_stats[sid]["CVs"].append(cv)
                    sample_stats[sid][media].append(rlu)
                    sample_stats[sid]["results"].append("Negative")
                else:
                    m_single = re.search(r"(\d{2,5})\s*\|\s*Negative", txt, re.I)
                    if m_single:
                        rlu = int(m_single.group(1))
                        sample_stats[sid][media].append(rlu)
                        sample_stats[sid]["results"].append("Negative")

print("=== 15 个新样本数据汇总 ===")
new_audit_entries = []
for sid in NEW_SAMPLES_LIST:
    info = sample_stats[sid]
    inst = info["inst"]
    atp = DAILY_ATP[inst]
    max_tsb = max(info["TSB"]) if info["TSB"] else "N/A"
    max_ftm = max(info["FTM"]) if info["FTM"] else "N/A"
    max_cv = max(info["CVs"]) if info["CVs"] else 0.0
    url = new_links_map.get(sid)
    
    is_blocked = (max_cv >= 30.0)
    audit_res = "BLOCK (CV >= 30%)" if is_blocked else "PASS & 100% MATCH"
    
    entry = {
        "Sample": sid,
        "Instrument": inst,
        "EagleTrax URL": url,
        "PDF ATP": atp,
        "PDF TSB": max_tsb,
        "PDF FTM": max_ftm,
        "Max CV%": f"{max_cv:.1f}%",
        "Audit Result": audit_res
    }
    new_audit_entries.append(entry)
    print(f"  {sid} | #{inst} | ATP: {atp} | TSB: {max_tsb} | FTM: {max_ftm} | CV: {max_cv:.1f}% | {audit_res}")

with open("celsis_090926_final_audit_report.json", "r", encoding="utf-8") as f:
    old_audit = json.load(f)

master_audit_map = {item["Sample"]: item for item in old_audit}
for entry in new_audit_entries:
    master_audit_map[entry["Sample"]] = entry

master_audit_list = sorted(list(master_audit_map.values()), key=lambda x: x["Sample"])

with open("celsis_090926_final_audit_report.json", "w", encoding="utf-8") as f:
    json.dump(master_audit_list, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 70)
print(f"🎉 成功更新最终审计报告: celsis_090926_final_audit_report.json")
print(f"   总计样本数: {len(master_audit_list)}")
print(f"   合格可审批: {sum(1 for x in master_audit_list if 'PASS' in x['Audit Result'])}")
print(f"   熔断隔离:   {sum(1 for x in master_audit_list if 'BLOCK' in x['Audit Result'])}")
print("=" * 70)
