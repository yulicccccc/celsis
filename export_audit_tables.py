import json

with open("celsis_100926_final_audit_report.json", "r", encoding="utf-8") as f:
    report = json.load(f)

# Headers
headers = [
    "#", "Sample", "Instrument", "Audit Result", "Method", "Filtered Vol", "Added Vol",
    "Live Status", "PDF ATP", "LIMS ATP", "PDF TSB", "LIMS TSB", "PDF FTM", "LIMS FTM", "Max CV%", "Titan ID", "Discrepancies"
]

tsv_lines = ["\t".join(headers)]
md_lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]

for idx, r in enumerate(report, 1):
    row = [
        str(idx),
        r["Sample"],
        f"#{r.get('Instrument', '')}",
        r.get("Audit Result", ""),
        r.get("LIMS Method", ""),
        str(r.get("LIMS Filtered Volume", "")),
        str(r.get("LIMS Added Volume", "")),
        r.get("LIMS Status", ""),
        str(r.get("PDF ATP", "")),
        str(r.get("LIMS ATP", "")),
        str(r.get("PDF TSB", "")),
        str(r.get("LIMS TSB", "")),
        str(r.get("PDF FTM", "")),
        str(r.get("LIMS FTM", "")),
        str(r.get("PDF Max CV%", "")),
        str(r.get("Titan ID", "")),
        "; ".join(r.get("Discrepancies", [])) if r.get("Discrepancies") else "None"
    ]
    tsv_lines.append("\t".join(row))
    md_lines.append("| " + " | ".join(row) + " |")

with open("celsis_100926_final_audit_table.tsv", "w", encoding="utf-8") as f:
    f.write("\n".join(tsv_lines))

with open("celsis_100926_final_audit_table.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("Generated celsis_100926_final_audit_table.tsv and celsis_100926_final_audit_table.md")
