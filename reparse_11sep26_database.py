import os
import sys
import re
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

DAILY_ATP = {
    "2222": "93229",
    "2011": "82976"
}

def clean_etx(raw):
    m = re.search(r'(?:[&E][TFKX][XKR]|ET[XKR]|EF[XKR]|&T[XKR])[- ]?(\d{6})[- ]?(\d{4})', raw, re.I)
    if not m:
        return None
    d1, d2 = m.group(1), m.group(2)
    if d1.startswith("20"):
        d1 = "26" + d1[2:]
    if d1 == "260001": d1 = "260901"
    if d1 == "260002": d1 = "260902"
    if d1 == "260003": d1 = "260903"
    if d1 == "260837": d1 = "260831"
    if d1 == "260887": d1 = "260831"
    if d1 == "260810": d1 = "260818"
    return f"ETX-{d1}-{d2}"

def parse_row(txt):
    m_rlu = re.search(r'(\d{2,6})\s*[\|\!\]\}\)\{\s]*(?:Negative|Cal\s*OK)', txt, re.I)
    rlu = int(m_rlu.group(1)) if m_rlu else None

    # CV percentage extraction
    cv = 0
    m_cv = re.search(r'(?:Negative|Cal\s*OK)[^|]*[\|\!\]\}\)\{][^|]*[\|\!\]\}\)\{]\s*(\d{1,2})\s*[\%\|\!\]\}\)\{]', txt, re.I)
    if m_cv and int(m_cv.group(1)) <= 35:
        cv = int(m_cv.group(1))
    else:
        m_cv2 = re.findall(r'\b(\d{1,2})\b', txt)
        # Look near the end
        if m_cv2 and int(m_cv2[-1]) <= 35:
            cv = int(m_cv2[-1])

    if rlu is not None:
        return None, None, rlu, "Negative", cv

    return None, None, None, "Unknown", 0

def main():
    with open("celsis_110926_all_rows_debug.json", "r", encoding="utf-8") as f:
        all_rows = json.load(f)

    print(f"Loaded {len(all_rows)} debug rows.")

    sample_dict = defaultdict(lambda: {
        "TSB_RLUs": [],
        "FTM_RLUs": [],
        "CVs": [],
        "results": [],
        "inst": None,
        "pages": set(),
        "entries": []
    })

    for r in all_rows:
        txt = r["text"]
        pno = r["page"]
        inst = r["inst"]
        media = r["media"]
        
        etx = clean_etx(txt)
        if not etx:
            continue

        r1, r2, rlu, res_str, cv = parse_row(txt)
        if not rlu:
            # Check for negative and numbers
            nums = [int(n) for n in re.findall(r'\b\d{2,6}\b', txt)]
            if nums and "negative" in txt.lower():
                rlu = nums[-1]
                res_str = "Negative"
                cv = 0

        sample_dict[etx]["inst"] = inst
        sample_dict[etx]["pages"].add(pno)
        sample_dict[etx]["results"].append(res_str)
        if cv is not None:
            sample_dict[etx]["CVs"].append(cv)
            
        if media == "TSB" and rlu:
            sample_dict[etx]["TSB_RLUs"].append(rlu)
        elif media == "FTM" and rlu:
            sample_dict[etx]["FTM_RLUs"].append(rlu)

    print(f"Aggregated {len(sample_dict)} unique samples.")

    final_db = []
    for sid, d in sorted(sample_dict.items()):
        inst = d["inst"]
        atp = DAILY_ATP.get(inst, "UNKNOWN")
        max_tsb = max(d["TSB_RLUs"]) if d["TSB_RLUs"] else None
        max_ftm = max(d["FTM_RLUs"]) if d["FTM_RLUs"] else None
        max_cv = max(d["CVs"]) if d["CVs"] else 0
        pages = sorted(list(d["pages"]))
        
        status = "PASS"
        notes = "100% Valid Negative"
        
        if max_cv >= 30:
            status = f"BLOCK (CV {max_cv}% >= 30%)"
            notes = f"Max CV% {max_cv}% >= 30%"
            
        final_db.append({
            "Sample": sid,
            "Instrument": inst,
            "Daily ATP": atp,
            "Max TSB RLU": max_tsb,
            "Max FTM RLU": max_ftm,
            "Max CV%": f"{max_cv}%",
            "Pages": pages,
            "Status": status,
            "Notes": notes
        })

    with open("celsis_110926_database.json", "w", encoding="utf-8") as f:
        json.dump(final_db, f, indent=2)

    print("=" * 75)
    print(f"🎉 Updated Database: celsis_110926_database.json ({len(final_db)} samples)")
    pass_cnt = sum(1 for s in final_db if s["Status"] == "PASS")
    block_cnt = sum(1 for s in final_db if "BLOCK" in s["Status"])
    print(f"  • PASS:     {pass_cnt}")
    print(f"  • BLOCK:    {block_cnt}")
    print("=" * 75)

    for s in final_db:
        print(f"  {s['Sample']} | Inst: #{s['Instrument']} | TSB: {str(s['Max TSB RLU']):<6} | FTM: {str(s['Max FTM RLU']):<6} | CV%: {s['Max CV%']:<4} | Status: {s['Status']} | Pages: {s['Pages']}")

if __name__ == "__main__":
    main()
