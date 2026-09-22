import sys
import json
from datetime import datetime
from collections import defaultdict
import calendar

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

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    records = json.load(f)

# Filter for OAjayi
oajayi_records = []
for r in records:
    app_by = (r.get("approved_by") or "").strip().lower()
    if "oajayi" in app_by:
        dt = parse_time(r.get("approved_time"))
        if dt:
            oajayi_records.append({**r, "_dt": dt})

print(f"Total OAjayi records found: {len(oajayi_records)}")

# Group by actual calendar date of approval (YYYY-MM-DD)
by_date = defaultdict(list)
for r in oajayi_records:
    dt = r["_dt"]
    by_date[dt.strftime('%Y-%m-%d')].append(dt)

daily_stats = []
total_net_seconds_all = 0
total_samples_all = 0

for d in sorted(by_date.keys()):
    times = sorted(by_date[d])
    count = len(times)
    total_samples_all += count
    
    # Calculate net active time for this day:
    # Intervals <= 15 minutes (900s) are continuous work
    # Intervals > 15 minutes are considered breaks/pauses
    net_sec = 0
    breaks = 0
    for i in range(1, len(times)):
        diff = (times[i] - times[i-1]).total_seconds()
        if diff <= 900:
            net_sec += diff
        else:
            breaks += 1
    
    # Baseline for first sample of the day (e.g. 38s median inspection time)
    first_sample_baseline = 38.0
    net_sec += first_sample_baseline
    total_net_seconds_all += net_sec
    
    gross_sec = (times[-1] - times[0]).total_seconds() if count > 1 else first_sample_baseline
    daily_stats.append({
        'date': d,
        'count': count,
        'start': times[0].strftime('%I:%M:%S %p'),
        'end': times[-1].strftime('%I:%M:%S %p'),
        'net_sec': net_sec,
        'gross_sec': gross_sec,
        'breaks': breaks,
        'avg_sec_per_sample': (net_sec / count) if count else 0
    })

print(f"Total active approval days in data: {len(daily_stats)}\n")
print(f"{'Date':<12} | {'Weekday':<9} | {'Samples':<8} | {'Net Active Time':<16} | {'Gross Span':<12} | {'Pace (s/sample)':<16} | {'Active Window':<25} | {'Breaks'}")
print("-" * 115)

for s in daily_stats:
    dt_obj = datetime.strptime(s['date'], '%Y-%m-%d')
    weekday_name = dt_obj.strftime('%a')
    
    net_m = int(s['net_sec'] // 60)
    net_s = int(s['net_sec'] % 60)
    net_fmt = f"{net_m}m {net_s}s"
    
    gross_h = int(s['gross_sec'] // 3600)
    gross_m = int((s['gross_sec'] % 3600) // 60)
    gross_fmt = f"{gross_h}h {gross_m}m" if gross_h > 0 else f"{gross_m}m"
    
    window = f"{s['start']} - {s['end']}"
    print(f"{s['date']:<12} | {weekday_name:<9} | {s['count']:<8} | {net_fmt:<16} | {gross_fmt:<12} | {s['avg_sec_per_sample']:<16.1f} | {window:<25} | {s['breaks']}")

# Summaries
avg_net_per_active_day = total_net_seconds_all / len(daily_stats)
avg_samples_per_active_day = total_samples_all / len(daily_stats)

print("-" * 115)
print(f"Total Samples Approved: {total_samples_all}")
tot_h = int(total_net_seconds_all // 3600)
tot_m = int((total_net_seconds_all % 3600) // 60)
tot_s = int(total_net_seconds_all % 60)
print(f"Total Net Active Time: {tot_h}h {tot_m}m {tot_s}s")
print(f"Average Samples / Active Day: {avg_samples_per_active_day:.1f} samples/day")
print(f"Average Net Time / Active Day (有审批工作的天): {int(avg_net_per_active_day // 60)}m {int(avg_net_per_active_day % 60)}s ({avg_net_per_active_day / 60:.1f} 分钟)")

# Also calculate median daily net time across active days
daily_net_secs = sorted([s['net_sec'] for s in daily_stats])
median_daily_net = daily_net_secs[len(daily_net_secs)//2]
print(f"Median Net Time / Active Day (中位数日耗时): {int(median_daily_net // 60)}m {int(median_daily_net % 60)}s ({median_daily_net / 60:.1f} 分钟)")

# Weekdays in August 2026:
cal = calendar.Calendar()
weekdays_aug = [d for d in cal.itermonthdates(2026, 8) if d.month == 8 and d.weekday() < 5]
print(f"\nAugust 2026 Total Business Days (周一至周五): {len(weekdays_aug)} 天")
avg_net_per_weekday = total_net_seconds_all / len(weekdays_aug)
print(f"Average Net Time / Business Day (按全月21个工作日摊平): {int(avg_net_per_weekday // 60)}m {int(avg_net_per_weekday % 60)}s ({avg_net_per_weekday / 60:.1f} 分钟)")
