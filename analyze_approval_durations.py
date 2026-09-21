import os
import sys
import json
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

INPUT_FILE = "celsis_approval_timestamps.json"
OUTPUT_TSV = "celsis_approval_duration_report.tsv"
OUTPUT_JSON = "celsis_approval_duration_analysis.json"

def parse_time(t_str):
    if not t_str:
        return None
    # e.g. "9/4/2026 5:29:45 PM"
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
    return " ".join(parts)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found!")
        sys.exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"Loaded {len(records)} records from {INPUT_FILE}.\n")

    # Group by packet
    packets = {}
    for r in records:
        pkt = r.get("Packet", "Unknown")
        if pkt not in packets:
            packets[pkt] = []
        packets[pkt].append(r)

    packet_summaries = []
    tsv_rows = [
        "Packet\tSample\tCurrent Status\tApproved Time\tInterval from Prev (s)\tApprover\tData Review Time\tReview-to-Approval"
    ]

    all_active_intervals = []

    for pkt_name, items in sorted(packets.items()):
        # Filter items with valid approved_time
        approved_items = []
        for it in items:
            t = parse_time(it.get("approved_time"))
            if t:
                approved_items.append({**it, "_dt": t})

        # Sort by approval time
        approved_items.sort(key=lambda x: x["_dt"])

        total_samples = len(items)
        approved_count = len(approved_items)

        if not approved_items:
            packet_summaries.append({
                "packet": pkt_name,
                "total_samples": total_samples,
                "approved_count": 0,
                "start_time": None,
                "end_time": None,
                "gross_seconds": 0,
                "net_seconds": 0,
                "breaks_count": 0,
                "avg_interval_seconds": 0,
                "approvers": []
            })
            continue

        start_dt = approved_items[0]["_dt"]
        end_dt = approved_items[-1]["_dt"]
        gross_seconds = (end_dt - start_dt).total_seconds()

        # Calculate consecutive intervals
        intervals = []
        break_seconds = 0
        breaks_count = 0
        prev_dt = None

        approvers = set()

        for idx, it in enumerate(approved_items):
            cur_dt = it["_dt"]
            approvers.add(it.get("approved_by") or "Unknown")

            interval_s = None
            if prev_dt:
                interval_s = (cur_dt - prev_dt).total_seconds()
                # If interval > 15 minutes (900 seconds), consider it a break/pause
                if interval_s > 900:
                    break_seconds += (interval_s - 60) # keep 60s as nominal interval
                    breaks_count += 1
                else:
                    intervals.append(interval_s)
                    all_active_intervals.append(interval_s)

            # Check review to approval time if available
            rev_dt = parse_time(it.get("data_review_time"))
            rev_to_app_str = ""
            if rev_dt and cur_dt >= rev_dt:
                rev_to_app_str = format_duration((cur_dt - rev_dt).total_seconds())

            tsv_rows.append(
                f"{pkt_name}\t{it['Sample']}\t{it.get('current_status','')}\t{it.get('approved_time','')}\t{interval_s if interval_s is not None else 0:.0f}\t{it.get('approved_by','')}\t{it.get('data_review_time','')}\t{rev_to_app_str}"
            )

            prev_dt = cur_dt

        net_seconds = max(0, gross_seconds - break_seconds)
        avg_interval = (sum(intervals) / len(intervals)) if intervals else (net_seconds / max(1, approved_count - 1))

        packet_summaries.append({
            "packet": pkt_name,
            "total_samples": total_samples,
            "approved_count": approved_count,
            "start_time": start_dt.strftime("%Y-%m-%d %I:%M:%S %p"),
            "end_time": end_dt.strftime("%Y-%m-%d %I:%M:%S %p"),
            "gross_seconds": gross_seconds,
            "gross_formatted": format_duration(gross_seconds),
            "net_seconds": net_seconds,
            "net_formatted": format_duration(net_seconds),
            "breaks_count": breaks_count,
            "avg_interval_seconds": round(avg_interval, 1),
            "avg_interval_formatted": format_duration(avg_interval),
            "approvers": sorted(list(approvers))
        })

    # Save TSV
    with open(OUTPUT_TSV, "w", encoding="utf-8") as f:
        f.write("\n".join(tsv_rows))

    # Save JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "packet_summaries": packet_summaries,
            "overall_total_samples": sum(p["total_samples"] for p in packet_summaries),
            "overall_approved_samples": sum(p["approved_count"] for p in packet_summaries),
            "overall_gross_seconds": sum(p["gross_seconds"] for p in packet_summaries),
            "overall_net_seconds": sum(p["net_seconds"] for p in packet_summaries),
            "overall_avg_interval_seconds": round((sum(all_active_intervals) / len(all_active_intervals)) if all_active_intervals else 0, 1)
        }, f, indent=2, ensure_ascii=False)

    # Print clean Markdown summary to console
    print("=" * 95)
    print("                      Celsis Approval Duration Statistical Report")
    print("=" * 95)
    print(f"| {'Packet (Date)':<16} | {'Samples':<7} | {'Approved':<8} | {'Start Approval':<22} | {'End Approval':<22} | {'Gross Time':<12} | {'Net Active':<12} | {'Avg/Sample':<10} | {'Approver':<10} |")
    print("|" + "-" * 18 + "|" + "-" * 9 + "|" + "-" * 10 + "|" + "-" * 24 + "|" + "-" * 24 + "|" + "-" * 14 + "|" + "-" * 14 + "|" + "-" * 12 + "|" + "-" * 12 + "|")
    
    for ps in packet_summaries:
        app_names = ", ".join(ps["approvers"]) if ps["approvers"] else "None"
        print(f"| {ps['packet']:<16} | {ps['total_samples']:<7} | {ps['approved_count']:<8} | {ps.get('start_time') or 'N/A':<22} | {ps.get('end_time') or 'N/A':<22} | {ps.get('gross_formatted', 'N/A'):<12} | {ps.get('net_formatted', 'N/A'):<12} | {ps.get('avg_interval_formatted', 'N/A'):<10} | {app_names:<10} |")

    print("=" * 95)
    print(f"\nDetailed report saved to:")
    print(f" - TSV:  {OUTPUT_TSV}")
    print(f" - JSON: {OUTPUT_JSON}\n")

if __name__ == "__main__":
    main()
