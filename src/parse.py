"""Script B: applies the rubric to saved raw responses.

Reads raw/*.json, writes out/labelled.csv. Cheap to re-run, so fix the rubric
and run it again rather than re-collecting.

Labels, tested in this order:

    empty         provider returned no text
    refusal       model declined to answer
    correct       the rule in force on the vignette's date
    repealed      the superseded rule, when the current one was asked
    over_applied  the current rule, when the historical one was asked
    wrong_other   some third answer
    ambiguous     nothing matched

Some provisions were amended twice, so `anchor_depth` (1 or 2) says how many
amendments behind a `repealed` answer is.

Per-response flags:

    hedged                 any expression of uncertainty
    denies_provision       claims the provision does not exist or was repealed
    echo_repealed_wording  contains wording deleted from the statute
"""

import csv
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from thai_numbers import extract_numbers  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
OUT = ROOT / "out"

REFUSAL = re.compile(
    r"ไม่สามารถให้คำแนะนำ|ไม่สามารถตอบ|ขออภัย.{0,30}ไม่|ควรปรึกษาทนาย|ไม่ใช่ที่ปรึกษากฎหมาย"
    r"|I can(?:'|no)t (?:help|provide|answer)|I'm not able to|consult (?:a|with a) (?:lawyer|attorney|legal)"
    r"|cannot provide legal advice", re.I)

HEDGE = re.compile(
    r"ไม่แน่ใจ|อาจมีการ|อาจจะ|โปรดตรวจสอบ|ควรตรวจสอบ|เท่าที่ทราบ|ข้อมูล.{0,10}อาจ|ณ เวลาที่|อาจไม่เป็นปัจจุบัน"
    r"|not (?:entirely )?(?:certain|sure)|may have (?:since )?(?:changed|been amended)|please (?:verify|check)"
    r"|to my knowledge|as of my|might be outdated|I believe", re.I)

# Wording deleted from the statute. Quoting it points at the old text.
DELETED_WORDING = {"C": [re.compile("(?:ตาม|เท่าที่)สมควร")]}

# A flag, not a label: right answer pre-frame, factual error post-frame.
DENIES_PROVISION = re.compile(
    r"ไม่มีบทบัญญัติ|ยังไม่มีบทบัญญัติ|ไม่ได้บัญญัติ|ไม่มีกฎหมาย(?:ใด)?(?:กำหนด|บัญญัติ)"
    r"|ถูกยกเลิก|ได้ถูกยกเลิก|ไม่ได้กล่าวถึง|มิได้บัญญัติ"
    r"|no (?:such )?provision|no provision(?:s)? (?:in|of|under)"
    # No "specify"/"provide": that phrasing is a fact pattern, not a denial.
    r"|does not (?:address|authori[sz]e|prescribe|permit|contain|exist)"
    r"|no longer (?:specif|provid|exist|in force|permit)"
    r"|(?:was|has been|were) repealed|there (?:are|is) no (?:purpose|provision)", re.I)

# Strip bold so "could **not** register" still matches "could not".
MARKDOWN = re.compile(r"\*+|__")


def strip_markdown(text):
    return MARKDOWN.sub("", text or "")


def _num_match(text, needed, absent=None):
    if not needed:
        return False
    found = extract_numbers(text)
    if not all(any(abs(f - n) < 1e-6 for f in found) for n in needed):
        return False
    for n in (absent or []):
        if any(abs(f - n) < 1e-6 for f in found):
            return False
    return True


def _re_match(text, patterns, absent=None):
    if not patterns:
        return False
    if not all(re.search(p, text, re.I) for p in patterns):
        return False
    for p in (absent or []):
        if re.search(p, text, re.I):
            return False
    return True


def bucket_hit(v, text, prefix, lang):
    """True if the response matches the named bucket.

    Number and regex rules are alternatives by default; `{prefix}_require_all`
    makes every rule the vignette defines mandatory.
    """
    nums = v.get(f"{prefix}_numbers")
    absent_n = v.get(f"{prefix}_absent_numbers")
    rx = v.get(f"{prefix}_regex_{lang}") or v.get(f"{prefix}_regex")
    absent_r = v.get(f"{prefix}_absent_regex_{lang}") or v.get(f"{prefix}_absent_regex")

    num_hit = bool(nums) and _num_match(text, nums, absent_n)
    re_hit = bool(rx) and _re_match(text, rx, absent_r)

    if v.get(f"{prefix}_require_all"):
        defined = [hit for hit, rule in ((num_hit, nums), (re_hit, rx)) if rule]
        return bool(defined) and all(defined)
    return num_hit or re_hit


def classify_with_depth(v, text, lang):
    """(label, anchor_depth) for one response."""
    if not text or not text.strip():
        return "empty", 0
    text = strip_markdown(text)
    if REFUSAL.search(text):
        return "refusal", 0
    if bucket_hit(v, text, "gold", lang):
        return "correct", 0
    if bucket_hit(v, text, "anchored", lang):
        return "repealed", 1
    if bucket_hit(v, text, "anchored_prior", lang):
        return "repealed", 2
    if bucket_hit(v, text, "over", lang):
        return "over_applied", 0
    if bucket_hit(v, text, "wrong", lang):
        return "wrong_other", 0
    # A numeric item that produced numbers, none of which were ours.
    if v.get("gold_numbers") and extract_numbers(text):
        return "wrong_other", 0
    return "ambiguous", 0


def classify(v, text, lang):
    return classify_with_depth(v, text, lang)[0]


def main():
    vignettes = {}
    for v in json.load(
            open(ROOT / "data" / "vignettes.json", encoding="utf-8"))["vignettes"]:
        vignettes[v["id"]] = v
        # Raw files saved under an old id still have to resolve. D17 was X06.
        for old in v.get("legacy_ids", []):
            vignettes[old] = v

    files = sorted(RAW.glob("*.json"))
    if not files:
        sys.exit(f"no raw responses in {RAW} — run collect.py first")

    OUT.mkdir(exist_ok=True)
    rows, counts = [], {}
    for f in files:
        rec = json.loads(f.read_text(encoding="utf-8"))
        v = vignettes.get(rec["vignette_id"])
        if v is None:
            print(f"  ! unknown vignette {rec['vignette_id']} in {f.name}", file=sys.stderr)
            continue
        text = rec.get("raw_response") or ""
        clean = strip_markdown(text)
        label, depth = classify_with_depth(v, text, rec["language"])
        counts[label] = counts.get(label, 0) + 1
        rows.append({
            "vignette_id": v["id"], "group": v["group"], "probe_id": v.get("probe_id") or "",
            "type": v["type"], "frame": v["frame"],
            "model": rec["model"], "model_version": rec.get("model_version", ""),
            "language": rec["language"], "condition": rec["condition"],
            "run_index": rec["run_index"], "label": label, "anchor_depth": depth,
            "hedged": int(bool(HEDGE.search(clean))),
            "denies_provision": int(bool(DENIES_PROVISION.search(clean))),
            "echo_repealed_wording": int(any(
                p.search(clean) for p in DELETED_WORDING.get(v["group"], []))),
            "manual_review": int(bool(v.get("manual_review"))),
            "response_chars": len(text),
        })

    out = OUT / "labelled.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print(f"{len(rows)} responses labelled -> {out}")
    for k in ("correct", "repealed", "over_applied", "wrong_other", "refusal",
              "ambiguous", "empty"):
        n = counts.get(k, 0)
        print(f"  {k:14s} {n:5d}  {n / len(rows):6.1%}")

    deep = sum(1 for r in rows if r["anchor_depth"] == 2)
    if deep:
        print(f"  {'of which depth 2':14s} {deep:5d}  anchored two amendments back")
    if counts.get("empty"):
        print(f"\n! {counts['empty']} responses came back with no text. These are "
              f"collection failures, not model errors — they are excluded from "
              f"SCORABLE. Re-run collect.py for those cells.")
    amb = counts.get("ambiguous", 0) / len(rows)
    if amb > 0.10:
        print(f"\n! ambiguous is {amb:.0%} — over 10% means the rubric is missing "
              f"common phrasings. Read 20 ambiguous responses and widen the patterns "
              f"BEFORE looking at any results, then re-run this script.")
    man = sum(r["manual_review"] for r in rows)
    if man:
        print(f"! {man} responses are on manual-review items (A08, B04, D16) — "
              f"hand-check these, the automatic label is indicative only")


if __name__ == "__main__":
    main()
