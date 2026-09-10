import json
import re

with open("celsis_090926_rows_extracted.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

# Let's inspect Page 11 row 5 (0413)
print("Page 11 Rows:")
for r in pages[10]["rows"]:
    if "041" in r["raw_text"]:
        print("  ", r["raw_text"])

# Page 10 row 13 (0837)
print("Page 10 Rows:")
for r in pages[9]["rows"]:
    if "0837" in r["raw_text"]:
        print("  ", r["raw_text"])

# Page 13 (0310)
print("Page 13 Rows for 0310 count:")
cnt = 0
for r in pages[12]["rows"]:
    if "0310" in r["raw_text"]:
        cnt += 1
print(f"Total 0310 rows found on Page 13: {cnt}")
for r in pages[12]["rows"]:
    print("  ", r["raw_text"])

# Page 19 (0411)
print("Page 19 Rows for 0411 count:")
for r in pages[18]["rows"]:
    print("  ", r["raw_text"])
