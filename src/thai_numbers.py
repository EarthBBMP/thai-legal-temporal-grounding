"""Turn Thai numerals and Thai/English number words into plain numbers.

The same quantity shows up three ways (๙๘, 98, เก้าสิบแปด) and the statutes
use words, so matching digits alone would miss most of them.
"""

import re

THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")

_UNITS = {
    "ศูนย์": 0, "หนึ่ง": 1, "เอ็ด": 1, "สอง": 2, "ยี่": 2, "สาม": 3, "สี่": 4,
    "ห้า": 5, "หก": 6, "เจ็ด": 7, "แปด": 8, "เก้า": 9,
}
_SCALES = {"สิบ": 10, "ร้อย": 100, "พัน": 1000, "หมื่น": 10000, "แสน": 100000, "ล้าน": 1000000}

# Longest first so "เก้าสิบแปด" is not eaten as "เก้า" + leftovers.
_WORD_RE = re.compile("(" + "|".join(sorted(
    list(_UNITS) + list(_SCALES) + ["ครึ่ง"], key=len, reverse=True)) + ")+")

_EN_UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
}
_EN_SCALES = {"hundred": 100, "thousand": 1000, "million": 1000000}

# Longest first too, so "sixty" is not read as "six" plus a stray "ty".
_EN_TOKEN = re.compile(r"\b(?:" + "|".join(sorted(
    list(_EN_UNITS) + list(_EN_SCALES) + ["half"], key=len, reverse=True)) + r")\b", re.I)

# Whitespace and hyphens always join; "and" joins only after a scale word, so
# "one hundred and twenty" is 120 but "five and ten" is not 15.
_EN_JOIN_PLAIN = re.compile(r"^[\s\-]+$")
_EN_JOIN_AND = re.compile(r"^[\s\-]+and[\s\-]+$", re.I)
_EN_JOIN_HALF = re.compile(r"^[\s\-]*(?:and[\s\-]+)?a[\s\-]+$", re.I)


def _en_runs(text: str):
    """Split the English number words in `text` into runs, one number each."""
    runs, cur, prev_end, seen_scale = [], [], 0, False
    for m in _EN_TOKEN.finditer(text):
        tok = m.group(0).lower()
        if cur:
            gap = text[prev_end:m.start()]
            joined = (_EN_JOIN_HALF.match(gap) if tok == "half"
                      else _EN_JOIN_PLAIN.match(gap)
                      or (seen_scale and _EN_JOIN_AND.match(gap)))
            if not joined:
                runs.append(cur)
                cur, seen_scale = [], False
        cur.append(tok)
        seen_scale = seen_scale or tok in _EN_SCALES
        prev_end = m.end()
    if cur:
        runs.append(cur)
    return runs


def _parse_en_run(tokens):
    """Value of one run of English number words. Returns float or None."""
    total, current, half, has_number = 0, 0, False, False
    for tok in tokens:
        if tok == "half":
            half = True
            continue
        has_number = True
        if tok in _EN_UNITS:
            current += _EN_UNITS[tok]
        elif _EN_SCALES[tok] == 100:
            current = (current or 1) * 100
        else:
            total += (current or 1) * _EN_SCALES[tok]
            current = 0
    # A bare "half" is ordinary prose ("half the debt"), not a quantity.
    if not has_number:
        return None
    return float(total + current) + (0.5 if half else 0.0)


def thai_digits_to_arabic(text: str) -> str:
    return text.translate(THAI_DIGITS)


def _parse_word_number(s: str):
    """Value of one run of Thai number words. Returns float or None.

    Handles สิบ/ร้อย/พัน multipliers, ยี่สิบ, trailing เอ็ด, and ครึ่ง (+0.5).
    """
    total, current, half = 0, 0, False
    i = 0
    while i < len(s):
        for token in sorted(list(_UNITS) + list(_SCALES) + ["ครึ่ง"], key=len, reverse=True):
            if s.startswith(token, i):
                if token == "ครึ่ง":
                    half = True
                elif token in _UNITS:
                    current = _UNITS[token]
                else:
                    scale = _SCALES[token]
                    if scale >= 1000:
                        total = (total + (current or 1)) * scale
                        current = 0
                    else:
                        total += (current or 1) * scale
                        current = 0
                i += len(token)
                break
        else:
            return None
    value = total + current
    if half:
        value += 0.5
    return float(value) if (value or half) else None


def extract_numbers(text: str) -> set:
    """Every number in the text, written as digits or as words."""
    if not text:
        return set()
    found = set()
    norm = thai_digits_to_arabic(text)

    for m in re.finditer(r"\d[\d,]*(?:\.\d+)?", norm):
        try:
            found.add(float(m.group(0).replace(",", "")))
        except ValueError:
            pass

    for m in _WORD_RE.finditer(text):
        run = m.group(0)
        # Short runs are usually ordinary prose, not numbers.
        if len(run) < 3:
            continue
        v = _parse_word_number(run)
        if v is not None:
            found.add(v)

    for tokens in _en_runs(text):
        v = _parse_en_run(tokens)
        if v is not None:
            found.add(v)
    return found


def contains_number(text: str, target: float, tol: float = 1e-6) -> bool:
    return any(abs(n - target) < tol for n in extract_numbers(text))


if __name__ == "__main__":
    cases = [
        ("ร้อยละเจ็ดครึ่งต่อปี", 7.5),
        ("ร้อยละสามต่อปี", 3),
        ("ไม่เกินเก้าสิบแปดวัน", 98),
        ("ไม่เกินหนึ่งร้อยยี่สิบวัน", 120),
        ("ไม่เกินสี่สิบห้าวัน", 45),
        ("ไม่เกินหกสิบวัน", 60),
        ("ไม่เกินสิบห้าวัน", 15),
        ("ร้อยละเจ็ดสิบห้า", 75),
        ("สามร้อยวัน", 300),
        ("สี่ร้อยวัน", 400),
        ("ปรับไม่เกินสองหมื่นบาท", 20000),
        ("ภายในเก้าสิบวัน", 90),
        ("๙๘ วัน", 98),
        ("120 days", 120),
        ("5,000 บาท", 5000),
        # English cardinals: the same quantities the vignettes grade on.
        ("at least three promoters", 3),
        ("Two.", 2),
        ("the minimum number was three", 3),
        ("ninety-eight days", 98),
        ("one hundred and twenty days", 120),
        ("three hundred days", 300),
        ("four hundred days", 400),
        ("not less than seventy-five per cent", 75),
        ("seven and a half per cent per annum", 7.5),
        ("fifteen days", 15),
        ("sixty days", 60),
        ("forty-five days", 45),
        ("twenty-four instalments", 24),
        ("twelve per cent per year", 12),
        ("a fine not exceeding twenty thousand baht", 20000),
    ]
    # Prose that must NOT produce these values.
    not_cases = [
        ("half the outstanding debt", 0.5),
        ("paragraphs five and ten", 15),
        ("money owed to one creditor", 98),
    ]
    bad = [(t, want, sorted(extract_numbers(t))) for t, want in cases
           if not contains_number(t, want)]
    bad += [(t, f"NOT {want}", sorted(extract_numbers(t))) for t, want in not_cases
            if contains_number(t, want)]
    if bad:
        for t, want, got in bad:
            print(f"FAIL {t!r} expected {want} got {got}")
        raise SystemExit(1)
    print(f"all {len(cases)} normaliser cases + {len(not_cases)} negative cases pass")
