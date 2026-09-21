import os
import sys
import json
import statistics
from datetime import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

INPUT_FILE = "august_oajayi_approval_timestamps.json"
OUTPUT_TSV = "oajayi_august_approval_report.tsv"
OUTPUT_JSON = "oajayi_august_analysis.json"

def parse_time(t_str):
    if not t_str:
        return None
    for fmt in ["%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
        try:
            return datetime.strptime(t_str.strip(), fmt)
        except Exception:
            continue
    return None

def format_duration(seconds):
    if seconds is None or seconds < 0:
        return "N/A"
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    parts = []
    if hrs > 0:
        parts.append(f"{hrs}h")
    if mins > 0 or hrs > 0:
        parts.append(f"{mins}m")
    parts.append(f"{secs}s")
    return " ".join(parts) if parts else "0s"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found!")
        sys.exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"Loaded {len(records)} total records from {INPUT_FILE}.")

    # STRICT FILTER: ONLY OAjayi!
    oajayi_records = []
    for r in records:
        app_by = (r.get("approved_by") or "").strip().lower()
        if "oajayi" in app_by:
            dt = parse_time(r.get("approved_time"))
            if dt:
                oajayi_records.append({**r, "_dt": dt})

    print(f"Filtered for OAjayi: {len(oajayi_records)} approved samples.")

    if not oajayi_records:
        print("No records found for OAjayi.")
        return

    # Group by packet
    packets = defaultdict(list)
    for r in oajayi_records:
        pkt = r.get("Packet", "Unknown")
        packets[pkt].append(r)

    packet_summaries = []
    tsv_rows = [
        "Packet\tSample\tApproved Time\tInterval from Prev (s)\tApprover\tHour of Day\tDay of Week"
    ]

    all_active_intervals = []
    hour_distribution = defaultdict(int)

    for pkt_name, items in sorted(packets.items()):
        items.sort(key=lambda x: x["_dt"])
        count = len(items)

        start_dt = items[0]["_dt"]
        end_dt = items[-1]["_dt"]
        gross_seconds = (end_dt - start_dt).total_seconds()

        intervals = []
        break_seconds = 0
        breaks_count = 0
        prev_dt = None

        for it in items:
            cur_dt = it["_dt"]
            hour_distribution[cur_dt.hour] += 1

            interval_s = None
            if prev_dt:
                interval_s = (cur_dt - prev_dt).total_seconds()
                if interval_s > 900:  # > 15 min gap is considered a break/interruption
                    break_seconds += (interval_s - 60)
                    breaks_count += 1
                else:
                    intervals.append(interval_s)
                    all_active_intervals.append(interval_s)

            tsv_rows.append(
                f"{pkt_name}\t{it['Sample']}\t{it.get('approved_time','')}\t{interval_s if interval_s is not None else 0:.0f}\t{it.get('approved_by','')}\t{cur_dt.strftime('%H:00')}\t{cur_dt.strftime('%A')}"
            )
            prev_dt = cur_dt

        net_seconds = max(0, gross_seconds - break_seconds)
        avg_interval = (sum(intervals) / len(intervals)) if intervals else (net_seconds / max(1, count - 1))
        med_interval = statistics.median(intervals) if intervals else avg_interval

        packet_summaries.append({
            "packet": pkt_name,
            "approved_count": count,
            "start_time": start_dt.strftime("%Y-%m-%d %I:%M:%S %p"),
            "end_time": end_dt.strftime("%Y-%m-%d %I:%M:%S %p"),
            "gross_seconds": gross_seconds,
            "gross_formatted": format_duration(gross_seconds),
            "net_seconds": net_seconds,
            "net_formatted": format_duration(net_seconds),
            "breaks_count": breaks_count,
            "avg_interval_seconds": round(avg_interval, 1),
            "avg_interval_formatted": format_duration(avg_interval),
            "median_interval_seconds": round(med_interval, 1),
            "median_interval_formatted": format_duration(med_interval)
        })

    # Cadence Distribution
    fast_sprints = sum(1 for i in all_active_intervals if i < 45)
    routine_pace = sum(1 for i in all_active_intervals if 45 <= i <= 60)
    deliberate_pace = sum(1 for i in all_active_intervals if 60 < i <= 90)
    extended_pace = sum(1 for i in all_active_intervals if i > 90)
    total_intervals = len(all_active_intervals)

    cadence_dist = {
        "fast_sprint_under_45s": {"count": fast_sprints, "pct": round(fast_sprints / total_intervals * 100, 1) if total_intervals else 0},
        "routine_45_to_60s": {"count": routine_pace, "pct": round(routine_pace / total_intervals * 100, 1) if total_intervals else 0},
        "deliberate_60_to_90s": {"count": deliberate_pace, "pct": round(deliberate_pace / total_intervals * 100, 1) if total_intervals else 0},
        "extended_over_90s": {"count": extended_pace, "pct": round(extended_pace / total_intervals * 100, 1) if total_intervals else 0}
    }

    # Global Stats
    global_avg = sum(all_active_intervals) / len(all_active_intervals) if all_active_intervals else 0
    global_med = statistics.median(all_active_intervals) if all_active_intervals else 0
    global_min = min(all_active_intervals) if all_active_intervals else 0
    global_max = max(all_active_intervals) if all_active_intervals else 0

    analysis_data = {
        "approver": "OAjayi",
        "scope": "August 2026 (08-2026)",
        "total_packets_audited": len(packet_summaries),
        "total_samples_approved": len(oajayi_records),
        "total_net_active_seconds": sum(p["net_seconds"] for p in packet_summaries),
        "total_net_active_formatted": format_duration(sum(p["net_seconds"] for p in packet_summaries)),
        "global_average_pace_seconds": round(global_avg, 1),
        "global_average_pace_formatted": format_duration(global_avg),
        "global_median_pace_seconds": round(global_med, 1),
        "global_median_pace_formatted": format_duration(global_med),
        "global_min_interval_seconds": round(global_min, 1),
        "global_max_interval_seconds": round(global_max, 1),
        "cadence_distribution": cadence_dist,
        "hourly_distribution": dict(sorted(hour_distribution.items())),
        "packet_summaries": packet_summaries
    }

    # Save TSV
    with open(OUTPUT_TSV, "w", encoding="utf-8") as f:
        f.write("\n".join(tsv_rows))

    # Save JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 105)
    print("                OAjayi Celsis Approval Duration Report (August 2026 Full Month)")
    print("=" * 105)
    print(f"| {'Packet (Date)':<22} | {'Approved':<8} | {'Start Time':<22} | {'End Time':<22} | {'Net Active':<12} | {'Avg Pace':<10} | {'Median':<8} |")
    print("|" + "-" * 24 + "|" + "-" * 10 + "|" + "-" * 24 + "|" + "-" * 24 + "|" + "-" * 14 + "|" + "-" * 12 + "|" + "-" * 10 + "|")

    for ps in packet_summaries:
        print(f"| {ps['packet']:<22} | {ps['approved_count']:<8} | {ps['start_time']:<22} | {ps['end_time']:<22} | {ps['net_formatted']:<12} | {ps['avg_interval_formatted']:<10} | {ps['median_interval_formatted']:<8} |")

    print("=" * 105)
    print(f"\n📊 Global OAjayi August 2026 Summary:")
    print(f"  • Total Approved Samples:   {len(oajayi_records)} samples across {len(packet_summaries)} packets")
    print(f"  • Total Net Active Time:    {format_duration(sum(p['net_seconds'] for p in packet_summaries))}")
    print(f"  • Overall Average Cadence:  {round(global_avg, 1)}s ({format_duration(global_avg)} / sample)")
    print(f"  • Overall Median Cadence:   {round(global_med, 1)}s ({format_duration(global_med)} / sample)")
    print(f"  • Cadence Breakdown:        <45s: {cadence_dist['fast_sprint_under_45s']['pct']}% | 45-60s: {cadence_dist['routine_45_to_60s']['pct']}% | 60-90s: {cadence_dist['deliberate_60_to_90s']['pct']}% | >90s: {cadence_dist['extended_over_90s']['pct']}%")
    print(f"\nDetailed exports:")
    print(f"  - TSV:  {OUTPUT_TSV}")
    print(f"  - JSON: {OUTPUT_JSON}\n")

if __name__ == "__main__":
    main()
