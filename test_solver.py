import re

def solve_rlu_triplet(line_text):
    # Clean obvious junk
    # If there are tokens like 345713414 -> could be 3457 and 3414
    # Let's tokenize by finding all potential numbers
    # Also handle concatenated numbers like 3457|3414 where pipe was recognized as 1
    # First, let's extract all numbers from text
    # Let's find after the ETX string
    m_etx = re.search(r"ETX[- ]?\d{6}[- ]?\d{4}(?:[- /(]+\d{1,2})?", line_text, re.I)
    after_etx = line_text[m_etx.end():] if m_etx else line_text
    # Cut off at Read Date (e.g. 9/9/2026 or Negative/Positive)
    m_end = re.search(r"(?:Negative|Positive|Cal OK|9/\d/2026)", after_etx, re.I)
    val_part = after_etx[:m_end.start()] if m_end else after_etx
    
    # Clean separators
    cleaned = re.sub(r"[\|\[\]\{\}\(\)!:;jJ/\\]+", " ", val_part)
    tokens = cleaned.split()
    
    # Convert tokens to candidate integers
    candidates = []
    for t in tokens:
        if t.isdigit():
            val = int(t)
            # If length is 8 digits (e.g. 34573414), split in half!
            if len(t) == 8:
                candidates.append(int(t[:4]))
                candidates.append(int(t[4:]))
            elif len(t) == 9: # e.g. 345713414 where '1' is pipe
                candidates.append(int(t[:4]))
                candidates.append(int(t[5:]))
            elif len(t) == 10:
                candidates.append(int(t[:5]))
                candidates.append(int(t[5:]))
            else:
                # If number starts with 1 and remaining is 4 digits, e.g. 12777 -> could be 2777
                if len(t) == 5 and t.startswith("1") and int(t[1:]) > 1000:
                    candidates.append(val)
                    candidates.append(int(t[1:]))
                else:
                    candidates.append(val)
                    
    # Now find (n1, n2, m) among candidates where abs((n1 + n2)/2 - m) <= 2 and n1 > 50
    # Search in order of appearance
    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            for k in range(j + 1, len(candidates)):
                n1, n2, m = candidates[i], candidates[j], candidates[k]
                if n1 >= 50 and n2 >= 50 and m >= 50:
                    expected_m = (n1 + n2) / 2.0
                    if abs(expected_m - m) <= 2:
                        return n1, n2, m

    return None, None, None

# Test on the 5 problematic rows
test_cases = [
    "|  | ETX-260831-0619-4/5 | 6834] 6729!16782| Negative} 9/9/2026 | 10:20:04 AM | | 7]",
    "| 13 | ETX-260831-0837-(3 | 3179 | 3234 j 3207 Negative] 9/9/2026 | 10:27:13 AM | 1 | 3]",
    "} 17 | ETX-260831-0564-(2 | 3370] 345713414] Negative| 9/9/2026 | 10:28:34 AM 1 3",
    "| 23 | ETX-260831-0673-(3 | 2745 2809 12777 | Negative} 9/9/2026 | 10:30:34 AM 4 4 |",
    "| 25 |ETX-260831-0673-(5 | 6522/ 6630] 6576 | Negative! 9/9/2026 | 10:30.44 AM | 7) 4]"
]

for tc in test_cases:
    print(tc)
    print("  -> Solved:", solve_rlu_triplet(tc))
