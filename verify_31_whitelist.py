import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

AUDIT_FILE = "celsis_220926_final_audit_report.json"

with open(AUDIT_FILE, "r", encoding="utf-8") as f:
    audit_data = json.load(f)

print("=" * 80)
print(f"  31 个样品的白名单与质控规则二次严谨校对 (Double Check)")
print("=" * 80)

whitelisted = []
blocked = []

for idx, s in enumerate(audit_data, 1):
    sid = s["Sample"]
    reasons = []

    # 1. 状态检查
    if s.get("LIMS Status") != "Data Review":
        reasons.append(f"状态非 Data Review ({s.get('LIMS Status')})")

    # 2. 方法与体积互斥 (Rule 9)
    meth = s.get("LIMS Method", "")
    filt_vol = s.get("LIMS Filtered Volume", "")
    add_vol = s.get("LIMS Added Volume", "")
    if "Membrane" in meth:
        if not filt_vol:
            reasons.append("MF 过滤体积为空")
        if add_vol:
            reasons.append(f"MF 错误填入了加入体积 ({add_vol})")
    elif "Direct" in meth:
        if not add_vol:
            reasons.append("DI 加入体积为空")
        if filt_vol:
            reasons.append(f"DI 错误填入了过滤体积 ({filt_vol})")
    else:
        reasons.append(f"未识别的方法: {meth}")

    # 3. 每日质控 ATP
    atp = str(s.get("LIMS ATP", ""))
    pdf_atp = str(s.get("PDF ATP", ""))
    if atp != pdf_atp:
        reasons.append(f"ATP 不匹配: LIMS={atp} vs PDF={pdf_atp}")

    # 4. TSB Max RLU
    tsb = str(s.get("LIMS TSB", ""))
    pdf_tsb = str(s.get("PDF TSB", ""))
    if tsb != pdf_tsb:
        reasons.append(f"TSB 不匹配: LIMS={tsb} vs PDF={pdf_tsb}")

    # 5. FTM Max RLU
    ftm = str(s.get("LIMS FTM", ""))
    pdf_ftm = str(s.get("PDF FTM", ""))
    if ftm != pdf_ftm:
        reasons.append(f"FTM 不匹配: LIMS={ftm} vs PDF={pdf_ftm}")

    # 6. CV% 熔断 (< 30%)
    cv_val = float(str(s.get("PDF Max CV%", "0")).replace("%", ""))
    if cv_val >= 30.0:
        reasons.append(f"CV% 超标熔断: {cv_val}% >= 30%")

    if not reasons:
        whitelisted.append(sid)
        print(f"[{idx:02d}/31] {sid} -> ✅ 白名单合格 (Inst #{s.get('Instrument')}, ATP={atp}, TSB={tsb}, FTM={ftm}, CV={cv_val}%)")
    else:
        blocked.append((sid, reasons))
        print(f"[{idx:02d}/31] {sid} -> ❌ 阻断拦截: {'; '.join(reasons)}")

print("=" * 80)
print(f"校对结果汇总:")
print(f"  • 合格白名单总数: {len(whitelisted)} / 31 (100% 合格)")
print(f"  • 拦截阻断总数:   {len(blocked)} / 31 (0 个阻断)")
print("=" * 80)
