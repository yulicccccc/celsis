import sys
import json
from datetime import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

INPUT_FILE = "august_oajayi_approval_timestamps.json"

def parse_time(t_str):
    if not t_str:
        return None
    for fmt in ["%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
        try:
            return datetime.strptime(t_str.strip(), fmt)
        except Exception:
            continue
    return None

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    records = json.load(f)

oajayi_records = []
for r in records:
    app_by = (r.get("approved_by") or "").strip().lower()
    if "oajayi" in app_by:
        dt = parse_time(r.get("approved_time"))
        if dt:
            oajayi_records.append({**r, "_dt": dt})

by_date = defaultdict(list)
for r in oajayi_records:
    dt = r["_dt"]
    by_date[dt.strftime("%Y-%m-%d")].append(dt)

daily_list = []
for d, times in by_date.items():
    times = sorted(times)
    count = len(times)
    net_sec = 0
    for i in range(1, len(times)):
        diff = (times[i] - times[i-1]).total_seconds()
        if diff <= 900:
            net_sec += diff
    net_sec += 38.0  # first sample baseline
    daily_list.append({
        "date": d,
        "count": count,
        "net_sec": net_sec
    })

# Sort by net_sec ascending
daily_list_sorted = sorted(daily_list, key=lambda x: x["net_sec"])

print("=== ALL 25 DAYS SORTED BY NET TIME ===")
for d in daily_list_sorted:
    m = int(d["net_sec"] // 60)
    s = int(d["net_sec"] % 60)
    print(f"{d['date']}: {d['count']} samples, {m}m {s:02d}s ({d['net_sec']:.0f}s)")

# ----------------------------------------------------
# 方案 A: 严格去掉绝对最小值与绝对最大值 (25天去掉两头)
# ----------------------------------------------------
sA_min = daily_list_sorted[0]
sA_max = daily_list_sorted[-1]
sA_trimmed = daily_list_sorted[1:-1]
sA_avg = sum(x["net_sec"] for x in sA_trimmed) / len(sA_trimmed)
sA_samples_avg = sum(x["count"] for x in sA_trimmed) / len(sA_trimmed)

print("\n----------------------------------------------------")
print(f"方案 A (全量25天，去掉绝对最小值和绝对最大值):")
print(f"  去掉最小值: {sA_min['date']} ({sA_min['count']} 样, {sA_min['net_sec']:.0f}s)")
print(f"  去掉最大值: {sA_max['date']} ({sA_max['count']} 样, {int(sA_max['net_sec']//60)}m {int(sA_max['net_sec']%60)}s)")
print(f"  剩余天数: {len(sA_trimmed)} 天")
print(f"  每天平均净用时: {int(sA_avg // 60)}分 {int(sA_avg % 60):02d}秒 ({sA_avg / 60:.1f} 分钟)")
print(f"  每天平均样本量: {sA_samples_avg:.1f} 个")

# ----------------------------------------------------
# 方案 B: 先排除零星单样(<=1样)复测日，再在23个正常工作日中去掉最小值和最大值
# ----------------------------------------------------
regular_days = [d for d in daily_list_sorted if d["count"] > 1]
reg_min = regular_days[0]
reg_max = regular_days[-1]
sB_trimmed = regular_days[1:-1]
sB_avg = sum(x["net_sec"] for x in sB_trimmed) / len(sB_trimmed)
sB_samples_avg = sum(x["count"] for x in sB_trimmed) / len(sB_trimmed)

print("\n----------------------------------------------------")
print(f"方案 B (常规批次日共23天，去掉日常最小值和最大值):")
print(f"  去掉日常最小值: {reg_min['date']} ({reg_min['count']} 样, {int(reg_min['net_sec']//60)}m {int(reg_min['net_sec']%60)}s)")
print(f"  去掉日常最大值: {reg_max['date']} ({reg_max['count']} 样, {int(reg_max['net_sec']//60)}m {int(reg_max['net_sec']%60)}s)")
print(f"  剩余天数: {len(sB_trimmed)} 天")
print(f"  每天平均净用时: {int(sB_avg // 60)}分 {int(sB_avg % 60):02d}秒 ({sB_avg / 60:.1f} 分钟)")
print(f"  每天平均样本量: {sB_samples_avg:.1f} 个")

# ----------------------------------------------------
# 方案 C: 常规批次日去掉前2高和前2低 (截断平均 10% Trimmed Mean)
# ----------------------------------------------------
sC_trimmed = regular_days[2:-2]
sC_avg = sum(x["net_sec"] for x in sC_trimmed) / len(sC_trimmed)
sC_samples_avg = sum(x["count"] for x in sC_trimmed) / len(sC_trimmed)

print("\n----------------------------------------------------")
print(f"方案 C (常规批次日23天，去掉最高的2天和最低的2天):")
print(f"  去掉最低的2天: {regular_days[0]['date']} ({int(regular_days[0]['net_sec']//60)}m), {regular_days[1]['date']} ({int(regular_days[1]['net_sec']//60)}m)")
print(f"  去掉最高的2天: {regular_days[-1]['date']} ({int(regular_days[-1]['net_sec']//60)}m), {regular_days[-2]['date']} ({int(regular_days[-2]['net_sec']//60)}m)")
print(f"  剩余天数: {len(sC_trimmed)} 天")
print(f"  每天平均净用时: {int(sC_avg // 60)}分 {int(sC_avg % 60):02d}秒 ({sC_avg / 60:.1f} 分钟)")
print(f"  每天平均样本量: {sC_samples_avg:.1f} 个")
