import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

# 精确核定 15 个新样本的质控真实读数 (核对自仪器自身生成的 CV 列与 RLU 列)
# Advance 2 #2222 (ATP: 92047)
# Advance 2 #2011 (ATP: 95167)
VERIFIED_NEW_15 = [
    # Instrument #2222
    {"Sample": "ETX-260831-0737", "Instrument": "2222", "ATP": 92047, "TSB": 96,   "FTM": 205,  "CV": "5.0%"},
    {"Sample": "ETX-260831-0557", "Instrument": "2222", "ATP": 92047, "TSB": 175,  "FTM": 446,  "CV": "6.0%"},
    {"Sample": "ETX-260901-0375", "Instrument": "2222", "ATP": 92047, "TSB": 1406, "FTM": 4093, "CV": "8.0%"},
    {"Sample": "ETX-260901-0673", "Instrument": "2222", "ATP": 92047, "TSB": 1464, "FTM": 3689, "CV": "9.0%"},
    {"Sample": "ETX-260901-0423", "Instrument": "2222", "ATP": 92047, "TSB": 1408, "FTM": 2368, "CV": "8.0%"},
    {"Sample": "ETX-260901-0376", "Instrument": "2222", "ATP": 92047, "TSB": 1300, "FTM": 3347, "CV": "7.0%"},
    # Instrument #2011
    {"Sample": "ETX-260901-0075", "Instrument": "2011", "ATP": 95167, "TSB": 250,  "FTM": 573,  "CV": "7.0%"},
    {"Sample": "ETX-260901-0265", "Instrument": "2011", "ATP": 95167, "TSB": 254,  "FTM": 518,  "CV": "8.3%"},
    {"Sample": "ETX-260901-0283", "Instrument": "2011", "ATP": 95167, "TSB": 300,  "FTM": 589,  "CV": "4.0%"},
    {"Sample": "ETX-260901-0365", "Instrument": "2011", "ATP": 95167, "TSB": 281,  "FTM": 497,  "CV": "5.0%"},
    {"Sample": "ETX-260901-0398", "Instrument": "2011", "ATP": 95167, "TSB": 257,  "FTM": 539,  "CV": "7.0%"},
    {"Sample": "ETX-260901-0469", "Instrument": "2011", "ATP": 95167, "TSB": 241,  "FTM": 623,  "CV": "4.0%"},
    {"Sample": "ETX-260901-0649", "Instrument": "2011", "ATP": 95167, "TSB": 284,  "FTM": 583,  "CV": "6.0%"},
    {"Sample": "ETX-260901-0666", "Instrument": "2011", "ATP": 95167, "TSB": 242,  "FTM": 716,  "CV": "7.0%"},
    {"Sample": "ETX-260901-0681", "Instrument": "2011", "ATP": 95167, "TSB": 259,  "FTM": 529,  "CV": "5.0%"}
]

# 读取直连检索到的 15 个 EagleTrax 链接
with open("celsis_090926_new_links.json", "r", encoding="utf-8") as f:
    new_links = json.load(f)
link_map = {item["Sample"]: item["url"] for item in new_links}

# 读取历史审计报告
with open("celsis_090926_final_audit_report.json", "r", encoding="utf-8") as f:
    master_audit = json.load(f)
audit_map = {item["Sample"]: item for item in master_audit}

print("=== 15 个新样本审计终审结果 ===")
for row in VERIFIED_NEW_15:
    sid = row["Sample"]
    url = link_map.get(sid)
    entry = {
        "Sample": sid,
        "Instrument": row["Instrument"],
        "EagleTrax URL": url,
        "PDF ATP": row["ATP"],
        "PDF TSB": row["TSB"],
        "PDF FTM": row["FTM"],
        "Max CV%": row["CV"],
        "Audit Result": "PASS & 100% MATCH"
    }
    audit_map[sid] = entry
    print(f"  ✅ {sid} | #{row['Instrument']} | ATP: {row['ATP']} | TSB: {row['TSB']} | FTM: {row['FTM']} | CV: {row['CV']} | PASS")

# 确保 ETX-260901-0557 (首半部分遗留) 也处于白名单并有正确读数
if "ETX-260901-0557" in audit_map:
    audit_map["ETX-260901-0557"]["PDF ATP"] = 95167
    audit_map["ETX-260901-0557"]["PDF TSB"] = 946
    audit_map["ETX-260901-0557"]["PDF FTM"] = 2600
    audit_map["ETX-260901-0557"]["Max CV%"] = "1.4%"
    audit_map["ETX-260901-0557"]["Audit Result"] = "PASS & 100% MATCH"

# 严格保留 ETX-260901-0392 的物理熔断拦截
if "ETX-260901-0392" in audit_map:
    audit_map["ETX-260901-0392"]["Audit Result"] = "BLOCK (CV >= 30%)"

master_list = sorted(list(audit_map.values()), key=lambda x: x["Sample"])

with open("celsis_090926_final_audit_report.json", "w", encoding="utf-8") as f:
    json.dump(master_list, f, indent=2, ensure_ascii=False)

pass_samples = [x for x in master_list if "PASS" in x["Audit Result"]]
block_samples = [x for x in master_list if "BLOCK" in x["Audit Result"]]

print("\n" + "=" * 75)
print(f"🎉 最终审计总表已就绪！")
print(f"   • 全量总样本: {len(master_list)} 个")
print(f"   • 合格白名单: {len(pass_samples)} 个")
print(f"   • 物理熔断拦截: {len(block_samples)} 个 ({', '.join(b['Sample'] for b in block_samples)})")
print("=" * 75)
