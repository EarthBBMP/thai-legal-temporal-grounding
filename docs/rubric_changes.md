# Rubric changes

Every change made to the parser, the normaliser and the matching rules, with
the reason and the effect on labels. Written before the full results were read.

**Provenance.** Every change below was driven by reading raw responses in
`raw/*.json` — never by looking at an aggregate metric and working backwards. The
trigger was an audit of the 44 responses labelled `ambiguous` or `wrong_other`.
Rows are attributed to a single change by re-running `parse.py` after each edit
in isolation and diffing `out/labelled.csv`.

Baseline before any change: **correct 281 · repealed 21 · over_applied 14 ·
wrong_other 23 · ambiguous 21 · refusal 0** (360 responses).

---

## Round 1 — matcher defects

### 1. `src/thai_numbers.py` — read English cardinals

`extract_numbers` handled Thai digits (๓), Arabic digits (3) and Thai number
words ("สาม") but not English words. Asked in English, models answer "at least
three promoters", not "at least 3", so a textbook-correct answer scored as if it
contained no number at all and fell through to `wrong_other`.

Added `one`–`twenty`, the tens `thirty`–`ninety`, `hundred`/`thousand`/`million`,
hyphenated compounds (`ninety-eight`), the hundreds construction (`one hundred
and twenty`) and the half-unit (`seven and a half` = 7.5, matching the existing
Thai `ครึ่ง` handling).

`seventy` and `eighty` are included although the change request omitted them:
X4 grades ร้อยละ 75 and D1 grades 98 วัน, so leaving them out would have
reproduced the same bug one number over.

Three false-positive risks this introduces are pinned by negative self-tests:
a bare "half" is not 0.5; `and` fuses two numerals only after a scale word, so
"paragraphs five and ten" stays 5 and 10, not 15; word boundaries stop "one"
inside "money".

Self-test: 30 positive cases (15 original, all still passing) + 3 negative.

**8 rows changed.** `B02 gpt4o en r1–r3` and `B01 gpt5 en r2` wrong_other →
correct; `B01 gpt4o en r1–r3` wrong_other → repealed; `A13 gpt5 en r1`
wrong_other → correct (a false positive, fixed in round 2 item 6).

### 2. `src/parse.py` — strip markdown before matching

Models emphasise exactly the operative words the rubric looks for. `B03 gpt55 en
r2` wrote "they could **not** register", which does not contain the literal
string `could not`. `**` and `__` are now removed before any pattern runs,
including the `hedged` and `echo_repealed_wording` flags. `response_chars` still
measures the raw text.

**1 row changed.** `B03 gpt55 en r2` ambiguous → correct.

### 3. `src/parse.py` — new `empty` label

Four responses came back with `raw_response: ""`. `collect.py` does not write a
file when the API call raises, so these were successful calls that returned no
text; all four are `gpt5`, the reasoning model. `finish_reason` and `usage` are
not saved, so the cause is not confirmed — recommend saving both.

Counting them as `ambiguous` charged the model for an answer it never gave and
inflated the rubric-miss rate that the 10% threshold watches. `empty` is outside
`analyze.py`'s `SCORABLE` allowlist by construction; a hygiene line in both
scripts reports the count.

**4 rows changed.** `A11 gpt5 en r1`, `A11 gpt5 en r2`, `A11 gpt5 th r2`,
`A16 gpt5 th r2` ambiguous → empty.

### 4. `data/vignettes.json` — A09/A10 anchored guard against negation

`anchored_regex` for A09/A10 (`outstanding balance|entire|whole`) fired on
correct answers that mention the whole balance only to rule it out:

> "...only on the principal amount of the instalment actually in default,
> **not the whole remaining debt**." — `A09 gpt55 en r2`, labelled `repealed`

All eight affected rows were read in full before the change; every one states
the correct base and mentions the whole balance in a negated or conditional
clause. These were false positives inflating the study's headline metric.

Python `re` has no variable-width lookbehind, so `(?<!not the )` cannot cover
the varying gaps. The guard uses `anchored_absent_regex_th`/`_en`, a field
`bucket_hit` already supports and C03 already uses, covering negation ("not the
whole"), and both orders of the conditional ("...only if", "only if...",
"unless...").

**8 rows changed.** `A09 gpt4o en r1–r3`, `A09 gpt55 en r2`, `A09 gpt5 th r1`,
`A10 gpt4o en r1–r2`, `A10 gpt5 en r1` repealed → ambiguous. They became
`correct` in round 2 item 7, once the gold side was widened to match.

### 5. `src/analyze.py` — clamp the Wilson interval

Not requested; fixed because change 4 broke the pipeline. With gpt5/en RSCR now
exactly 0, `centre - half` lands on `6.9e-18` instead of 0, `point - low` goes
negative and matplotlib refuses to draw the figure. Confirmed as a latent bug
rather than a new one by running `analyze.py` against the pre-change labels,
where it completes. The interval is now clamped to contain the point estimate.

**0 rows changed** — plotting only.

---

## Round 2 — matching rules

### 6. A13 — `gold_require_all`

`bucket_hit` treats a number rule and a regex rule as alternatives. A13 asks
three things at once (may the rate be adjusted, by what instrument, reviewed by
whom and how often), so a model that got only the review cycle right scored as
`correct`:

> "...requires the **Cabinet** to review the Section 7 rate at least every
> **three** years and permits adjustment by an **announcement (notification)**
> published in the Government Gazette." — `A13 gpt5 en r1`

Wrong agency, wrong instrument, but "three" satisfied `gold_numbers` on its own.

Added `"gold_require_all": true` to A13 and support for `{prefix}_require_all`
in `bucket_hit`: when set, every rule the vignette defines must fire. The field
is read per bucket for consistency with the rest of the schema, but only A13
sets it. With the field absent the OR behaviour is bit-for-bit unchanged —
verified by diffing all 360 rows.

**2 rows changed, both A13, no row outside A13.** `A13 gpt5 en r1` and
`A13 gpt5 th r3` correct → wrong_other. Both were read and confirmed: each names
a Ministry of Finance notification rather than a royal decree.

### 7. Widening gold and the opposite bucket together

Widening only the gold side would bias every vignette toward `correct`. For each
of the five vignettes the opposite bucket was audited in the same pass, by
checking on which rows its pattern fires and whether the absent guard suppresses
it. Findings per vignette:

**A09** — gold missed "เพียงงวดที่ 5", "จำนวนเงินที่ค้างชำระ", "instalment only",
"overdue amount", and English phrasings where the gap between `only` and
`instal` ran to 94 characters against a 20-character limit. Widened both
languages; `เฉพาะ.{0,20}งวด` → `{0,30}` because "เฉพาะจำนวนเงินที่ค้างชำระ (งวดที่ 5)"
overshoots by two characters.
*Opposite bucket:* the anchored pattern fires on 8 rows and the guard suppresses
all 8. No response in A09 asserts the whole-balance answer, so there is nothing
for a widened anchored pattern to catch. Not widened.

**A10** — gold required the exact phrase "principal of that instalment" while
models write "principal amount of the instalment that is in default"; `only.{0,25}instal`
missed `A10 gpt55 en r1` by 7 characters (gap 32).
*Opposite bucket:* widened. `A10 gpt5 en r3` writes "Only if the creditor validly
accelerates the debt does default interest run on the entire unpaid balance" —
the conditional precedes the phrase, the reverse of the order round 1 handled, so
the guard missed it. It was labelled `correct` only because gold happened to win
first. Added `only if[^.]{0,80}(whole|entire|outstanding|total)` to both A09 and
A10 so the verdict does not depend on evaluation order.

**A12** — gold's `no (specific )?provision` allowed only the word `specific`
between "no" and "provision", so "there was **no CCC provision** voiding such a
term" missed.
*Opposite bucket:* widened. `A12 gpt5 en r2` answers "**Yes.** ... Any agreement
to the contrary **is void**" — a textbook retroactive application, missed because
`over_regex_en` demanded the past tense "was void". Added `^\s*Yes\b`. Separately
tightened `over_regex_th` from `เป็นโมฆะ` to `(?<!ไม่)เป็นโมฆะ`, which was matching
inside `ไม่เป็นโมฆะ` — the opposite answer. That tightening changes no label today
because gold is tested first; it removes a latent misclassification.

**A16** — gold had `may not` but not `must not`, and no `barred`, and did not
accept a leading "No."
*Opposite bucket:* none exists. A16 is a `control` with `frame: none` on a rule
that never changed (the anatocism prohibition), so there is no superseded rule to
be anchored to and no `anchored_*` or `over_*` key in the vignette. Nothing to
widen.

**B03** — gold's `could not` was defeated by markdown (round 1) and by "No."
against a pattern demanding "no,".
*Opposite bucket:* tightened, not widened. `over_regex_th` contained a bare
`สามารถ`, which matches inside `ไม่สามารถ` — the gold answer. Changed to
`(?<!ไม่)สามารถ`. No label changes today (gold wins first); removes a latent
misclassification. No B03 response is over-applied but unmatched, so no widening.

**23 rows changed**, none outside the five vignettes: 22 ambiguous → correct,
and `A12 gpt5 en r2` ambiguous → over_applied.

### 8. `src/check_instruments.py` — instrument citation audit (not merged)

Standalone reporting script. Reads `raw/*.json`, writes nothing, and is not
imported by `parse.py`. Three separate flags: `fabricated`, `misattributed`,
`wrong_instrument_type`. Ground truth is the `instrument` and `section` columns
of `data/law_facts.csv`.

Three precision rules: a citation must carry a number or a year before it can be
called invented or misattributed, because naming an instrument is not citing one;
probes absent from `law_facts.csv` are skipped for want of ground truth; and
`wrong_instrument_type` only runs where the vignette's own `gold_regex` names the
expected instrument class.

A first run produced 36 findings, of which 9 came from `\bact\b` matching the
statute's own words "juristic **act**". Both fixes above — the particulars
requirement and a `(?<!juristic )` guard — were added before the results were
reported. Second run: **25 findings** (19 fabricated, 2 misattributed, 4
wrong_instrument_type). Precision is unverified and awaits manual review.

---

## Round 3 — audit only, no rubric change yet

The dataset grew from 360 to 1931 responses (9 models, `typhoon25` added), and is
still mid-collection — `qwen3` sits at 215 rows against 360 for the fully
collected models, so every count here is a snapshot. This
round is an audit against the original Labour Protection Act B.E. 2541 (เล่ม 115
ตอนที่ 8 ก): ม.41 = 90 days, ม.59 = 45 days, ม.118(5) = 10 years or more = 300
days with no (6). Amendment No. 7/2562 moved ม.41 to 98, kept ม.59 at 45, split
ม.118(5) to 10–20 years = 300 and added (6) 20 years or more = 400.

No vignette or parser file was changed in this round. Three findings are on
record and awaiting a decision.

### 9. Group D anchors three deep, and the rubric only knows two layers

ม.41 has three layers — 90 (2541) → 98 (2562) → 120 (2568) — but every D
vignette encodes only the last two. `typhoon25` answers 90 consistently:

> "ลูกจ้างหญิงมีสิทธิลาเพื่อคลอดบุตรได้ไม่เกิน **90 วัน** และนายจ้างต้องจ่ายค่าจ้างไม่เกิน **45 วัน**"
> — `D01 typhoon25 th r1`, the 2541 text verbatim, currently `wrong_other`

Two options were simulated over all 1836 rows before recommending either.

**Option A — fold 90 into the existing `anchored_numbers`. Rejected.**
`_num_match` requires *every* listed number to be present, so `[98, 45, 90]`
demands all three at once. Simulation: **21 rows correctly labelled `repealed`
become `wrong_other`** (gpt4o and gpt55 on D01/D16, which answer 98/45 and never
say 90) while capturing no new anchoring at all. Strictly worse than doing
nothing, and it would also collapse two legal eras into one bucket, erasing the
distinction the study exists to measure.

**Option B — a separate `anchored_prior_*` bucket, checked after `anchored`.
Recommended.** Reuses the existing `{prefix}_numbers` machinery with no change to
`_num_match`. Simulation: **21 rows move to a prior-layer bucket, and no existing
`repealed` row is disturbed.** It also answers the D02 case correctly: for a
`pre`-frame vignette whose gold is 98, answering 90 is anchoring to a still older
text, not over-application, and a separate bucket says so without contorting
`over_numbers`.

Not recommended for D03/D04. Their 90s are not clean anchoring but a conflation
of ม.41 leave-days with ม.59 paid-days — "90 days paid at 100%" was never the
rule under any version, since 2541 paired 90 days of leave with 45 paid.

**Prerequisite.** D12 must get `gold_require_all` first. It carries both
`gold_numbers: [98]` and a `gold_regex`, so under OR semantics six `typhoon25`
rows answering **90** score `correct` on the strength of the word "prenatal"
alone — the same defect fixed for A13 in item 6. B05, B09, B10, B11 and D08 share
the exposure and have not been reviewed.

### 10. X06 is not a valid control

X06 asks for severance at 20 years or more (400 days). That subsection did not
exist before Amendment No. 7/2562 — 20-year employees fell under ม.118(5) at 300
days — so X06 tests a rule that changed, which is what a control must not do.
`law_facts.csv` already contradicts itself here: X6 is marked `new_rule =
ไม่เปลี่ยน` and `evidence_old = control` while its `instrument` column records
`ฉบับ 7 พศ 2562 ม.15`, the very amendment that created it.

Three rows answer 300, all `typhoon25`, all currently `wrong_other`. They are
anchored to the pre-2562 text, and inside the control group that error is
counted as ordinary noise — which flatters the contrast the control exists to
draw.

X05 survives as a control: the amendment narrowed its bracket from "10 years or
more" to "10–20 years", but for the employee the vignette describes the answer is
300 either way. Recommend moving X06 out of group X, or giving it
`anchored_numbers: [300]` and scoring it as an amended rule.

### 11. `typhoon25` fails 50 of its 60 control responses

Reported in full in the session log; the 50 rows collapse to 30 distinct
responses at temperature 0. Only X06's three 300-answers are anchoring to a prior
version of the same section that the 2541 text can confirm.

A further **10 rows carry three distinct numbers that match a rule in
`law_facts.csv` — but a different provision than the one asked**: 7.5% on X01
(5 rows), 50% on X04 (3 rows), 90 days on X08-en (2 rows). Stated as a numeric
coincidence with a known rule, not as a claim about where the model drew it
from; X01 is the strongest case, since "ร้อยละ 7.5 ต่อปี" is the same repealed
ปพพ ม.7 rate, word for word, that drives the A15 anchoring.

The remainder match no rule in `law_facts.csv` at any date. X10 answers about
ม.124 rather than the ม.151 asked. The 2541 originals for ม.9, ม.34, ม.57/1,
ม.70, ม.75, ม.120 and ม.151 are not available — `sources/statute_texts` is
empty — so none of these can be confirmed as anchoring either way, and they are
reported as unverified rather than counted as random error.

## Round 4 — three-layer anchoring implemented

Decisions taken: Option B, mapped to the existing `repealed` label with a new
`anchor_depth` column; X06 moved out of the control group as D17 with
`anchored_numbers: [300]`; D03/D04 excluded; D12's `gold_require_all` first.

`parse.py` was **not** run — collection for claude/gemini/qwen is still in
flight. Everything below was verified by classifying all 2076 raw records in
memory, writing nothing. `out/labelled.csv` is untouched and still holds the
older 1931-row run.

### 12. `anchored_prior_*` bucket and the `anchor_depth` column

`classify_with_depth` returns `(label, depth)` and is tested in ladder order, so
the nearer layer always wins: `anchored` → depth 1, `anchored_prior` → depth 2,
both labelled `repealed`. `classify` still returns the label alone, unchanged for
any existing caller. `labelled.csv` gains an `anchor_depth` column; `SCORABLE`
and RSCR are untouched, so the headline metric stays comparable with earlier runs
while the deeper layer remains visible.

Vignettes given `anchored_prior_numbers`: D01 `[90, 45]`, D02 `[90, 45]`,
D12 `[90]`, D16 `[90, 45]` with `anchored_prior_absent_numbers: [98, 120]` so a
pair answer that names a later layer is not swept into the older one.

D12 also gained `gold_require_all: true`, without which its six `typhoon25` rows
answering 90 would keep scoring `correct` on the word "prenatal" and never reach
any anchored bucket.

### 13. X06 → D17, and the renaming hazard

Renaming a vignette is not a cosmetic edit: `parse.py` resolves a raw record by
the `vignette_id` stored **inside** it, and `collect.py` builds filenames from
`v["id"]`. A bare rename would therefore have orphaned all 24 `X06__*.json`
records — dropped with an "unknown vignette" warning — and made the next
`collect.py` run re-buy those 24 answers under the new name.

Both scripts now understand `legacy_ids`. D17 declares `["X06"]`; `parse.py`
registers the old id as an alias, and `collect.py` treats an existing
`X06__…json` as already collected. Verified: all 2076 raw records resolve, none
unknown.

`type` and `frame` had to change too, not just `group`. `analyze.py` filters RSCR
on `frame == "post"` (line 91) and the control metric on `type == "control"`
(line 109), so leaving them at `none`/`control` would have kept D17 inside the
control accuracy figure and excluded its anchoring from RSCR — the move would
have had no effect on either metric. D17 is now `knowledge` / `post`.

Under the new rules D17 yields **8 `repealed`** responses (5 `qwen3`, 3
`typhoon25`) that were previously `wrong_other` inside the control group.

**Still inconsistent:** `data/law_facts.csv` row X6 keeps `new_rule = ไม่เปลี่ยน`
and `evidence_old = control` while its `instrument` column names the amendment
that created the subsection. The vignette now says one thing and the fact table
another. Not changed — out of scope for this round.

### Effect, isolated

Old rubric vs new rubric over the identical 2076 raw records:

| label | before | after | delta |
|---|---:|---:|---:|
| correct | 1419 | 1413 | −6 |
| repealed | 180 | 209 | **+29** |
| over_applied | 58 | 58 | 0 |
| wrong_other | 283 | 260 | −23 |
| ambiguous | 113 | 113 | 0 |

29 rows changed — 23 `wrong_other` → `repealed`, 6 `correct` → `repealed` (the
D12 OR-bug) — confined to D01 (8), D02 (6), D12 (6), D16 (1), D17 (8).
`anchor_depth`: 1867 rows at 0, 188 at 1, **21 at 2**.

### 14. OR-bug audit across all dual-rule vignettes — proposal, not applied

Seven vignettes carry both `gold_numbers` and a `gold_regex`. A13 and D12 are
already fixed. The other five were audited in **both** directions, which changed
the recommendation from the one that seemed obvious.

**Safe to flip with `gold_require_all` alone** — every affected row verified wrong:

| vignette | gold | rows | why the regex alone is not evidence |
|---|---|---|---|
| B05 | 1 month | 7 | regex is the bare unit `month`/`เดือน`; answers of "three months" and "six months" contain it |
| B09 | 3 years | 9 | regex `year`/`ปี` is the unit disambiguator — `gold_numbers: [3]` matches the "3" in "three **months**" |
| D08 | 15 days | 8 | `medical certificate` appears in answers giving 30 or 60 days, and in three that deny the right exists at all |

**Needs the regex widened first — flipping alone would create false negatives:**

- **B11** — 5 rows answer correctly with "**1 ใน 4**", which `หนึ่งในสี่|1/4|25`
  does not match. Widen with `[1๑]\s*ใน\s*[4๔]` before requiring both. Simulated
  with the widened pattern: 16 correct / 13 wrong_other, against 22/7 today.
- **B10** — ⚠️ **superseded by item 17 below; the judgment in this paragraph was
  wrong.** Calling the 13 demoted rows incorrect was a misreading: "one company
  absorbs another" *is* ม.1238(2), in different words. Kept here as written so
  the correction is legible.

  B10 scores **29 of 29 correct today**, which is implausible for a
  question this subtle, and the reason is the OR: every answer names "2 forms",
  so `gold_numbers: [2]` alone carries them all. Six rows state the
  surviving-company form correctly as "คงอยู่" or "continues to exist", which
  `คงมีสภาพ|ยังคง.{0,20}นิติบุคคล|คงสภาพ` and `surviv|remains a (legal|juristic)`
  both miss; the rest really are wrong, describing amalgamation plus an
  *acquisition* with both companies ceasing to exist. Adding `คงอยู่|ไม่สิ้นสภาพ`
  and `continues to exist|remains in existence`, then requiring both, gives
  **16 correct / 13 wrong_other**, and all six verified-correct rows survive.

**A blanket flip of the default to AND is *not* recommended**, which reverses the
direction this audit started in. Requiring both rules everywhere changes 56 rows,
but 22 of them are B10 and B11 rows matching the number and missing a narrow
regex — the regexes were written as supplements, and several are too tight to
carry a co-requirement. The per-vignette path with a regex review is the safe one.

## Round 5 — B10 excluded, approved fixes applied

`parse.py` still not run; collection has been static at 2076 raw records across
two rounds. Everything below verified by classifying all 2076 in memory.

### 15. Approved rubric fixes

`gold_require_all: true` on **B05**, **B09**, **D08**. **B11** additionally gains
`[1๑]\s*ใน\s*[4๔]` in `gold_regex_th`, so the five rows answering "1 ใน 4"
correctly are kept before the conjunction is imposed.

**30 rows change, none outside these four, B10 untouched:**

| vignette | rows | transition | after |
|---|---:|---|---|
| B05 | 7 | correct → wrong_other | 24 correct / 12 wrong_other |
| B09 | 9 | correct → wrong_other | 20 / 10 |
| B11 | 6 | correct → wrong_other | 16 / 13 |
| D08 | 8 | 5 → wrong_other, 3 → repealed | 2 correct / 15 wrong_other / 3 repealed / 4 empty |

D08's three `repealed` are right on the merits: "ยังไม่มีบทบัญญัติ" is the
pre-amendment state, which is what its anchored regex is for. D08 keeping only 2
correct is a hard-but-fair result — the question asks for the number of days, the
circumstances and the required document, and almost no model supplies all three.
B11 is `type: control`, so its 16/13 moves the control-accuracy figure.

### 16. law_facts.csv row X6 corrected

Was `new_rule = ไม่เปลี่ยน`, `evidence_old = control` while `instrument` named the
amendment that created the subsection. Now records the real history: `old_rule =
ไม่มีบทบัญญัติ (20 ปีขึ้นไปได้ 300 วันตาม ม.118(5) เดิม)`, `new_rule = 400 วัน`,
group `D`, evidence `ฉบับ 7 พศ 2562 ม.15 เพิ่ม (6)`.

`effective_date` deliberately left blank — it was never supplied and
`sources/statute_texts` is empty, so filling it would be invention. It needs the
gazette date for ฉบับ 7 พ.ศ. 2562. `check_instruments.py` is unaffected: it reads
`instrument` and `probe_id`, both unchanged.

### 17. B10 excluded from analysis instead of regex-tightened

The Round-4 proposal to widen B10's regex and require both rules was **rejected,
correctly**. `qwen3` and `typhoon25` answers of the form "one company absorbs
another" describe exactly what ม.1238(2) permits — one company keeping its legal
personality — in different words. Any regex strict enough to demote the genuinely
wrong answers also demotes these, so the 16/13 split simulated in item 14
contained false negatives. Tightening was the wrong tool.

B10 now carries `excluded_from_analysis: true` with `exclusion_reason`: the "two
forms" answer is reachable from general international M&A knowledge without
knowing ม.1238, so the item does not measure temporal grounding.

`analyze.py` gained `excluded_vignettes()` and filters `rows` once, immediately
after `load()` in `main()` — a single choke point that covers every metric, the
hygiene block and the figure. The exclusion and its reason are printed into
`summary.txt`, so the output documents its own denominator. Verified: 1931 → 1902
rows, B10 appears nowhere except the announcement. `labelled.csv` is untouched —
exclusion is an analysis decision, not a claim the responses are unusable, and
`vignettes.json` stays the single source of truth (no `parse.py` rerun needed).

### 18. Same-criterion audit of the other vignettes — proposal, not applied

Screened *after* the item-15 fixes, so B09's now-removed false-corrects no longer
pollute the list. Criterion: ≥90% correct overall **and** the three weakest models
(gpt4o, qwen3, typhoon25) never missing. Six candidates, in four buckets with
different remedies.

**Exclusion candidates — gold reachable without Thai law:**

- **A09** (54/54, weak 18/18). The prompt states that instalment 5 alone is unpaid
  and every other instalment was paid on time, and mentions no acceleration
  clause. On that fact pattern "interest runs on the 10,000 baht in arrears"
  follows from general contract principles and the prompt's own arithmetic; ม.224/1
  is not needed. The tell: `typhoon25` scores **6/6** here while getting **50 of
  its 60** group-X control responses wrong.
- **C01** (24/24, weak 18/18). Striking an 8-year-old hard enough to leave bruises
  is outside parental authority under the amended text *and* under the repealed
  "ตามสมควร" — and under ordinary child-protection norms. The item cannot separate
  the two eras. Confirmed empirically: **0 of 24** responses quote the deleted
  wording "ตามสมควร", so the anchoring signal it was built to catch cannot appear.

**Rubric artifact, not guessability — regex review, not exclusion:**

- **B07** (36/36). `gold_regex` is the bare topic word `quorum` / `องค์ประชุม`,
  which the question itself uses ("do directors ... count toward the quorum?").
  An answer saying directors do *not* count would still match. The B05 disease.
  **Latent, not yet realised** — 0 of 36 responses actually answer negatively, so
  no row is currently mislabelled; the item simply cannot discriminate if one
  ever does. Recommend replacing the regex with the operative holding.

**Keep — high accuracy is the design working, not a defect:**

- **A07** (54/54). Pre-frame, gold 7.5% / 15,000. Easy precisely *because* an
  anchored model lands on gold: for 2019 the old rate **is** the right answer.
  7.5% is not derivable without Thai knowledge. This is the paired pre/post
  design behaving as intended.
- **C06** (24/24) and **A04** (54/54). Both exist to detect a specific
  over-application — C06 catches over-strict use of the new ม.1567(2), A04 catches
  wrongly applying the ม.7 rate where no interest was agreed. Neither found any,
  which is a valid null result. Their answers are guessable, but that is what a
  control is for.

**Also worth recording:** **A15** (51/54) states the 12% contractual rate in the
prompt, so its gold is embedded in the question. That is deliberate — its own note
calls it a distractor separating models that read the prompt from models that
recite a statutory rate. Recommend keeping.

## Round 6 — A09 and C01 excluded, B07 regex fixed, X6 dated

`parse.py` still not run. Verified in memory over 2142 raw records; collection is
still adding rows.

### 19. Group C is healthy — and the C01 evidence changed

Checked before excluding C01, as asked. The deleted wording "ตามสมควร" is
Thai-only, so an English response can never echo it; counts are over all rows.

| vignette | rows | echo=1 | of which Thai | labels |
|---|---:|---:|---:|---|
| C01 | 30 | **2** | 2 | 29 correct, 1 empty |
| C02 | 27 | **8** | 6 | 8 correct, 5 repealed, 6 refusal, 8 ambiguous |
| C03 | 24 | **1** | 1 | 1 correct, 4 repealed, 19 ambiguous |
| C04 | 24 | 0 | 0 | 11 correct, 13 wrong_other |
| C05 | 24 | **5** | 5 | 11 correct, 1 over_applied, 4 refusal, 8 ambiguous |
| C06 | 24 | 0 | 0 | 24 correct |

**C02 = 8 and C05 = 5, so the answer to the question asked is no — they are not
zero, and group C as a whole is not broken.** The anchoring signal the group was
built to catch is present and detected, most strongly in C02. C03's 19 ambiguous
rows are a separate matter worth a later look.

**The C01 evidence has moved.** Last round's "0 of 24" was measured on a smaller
raw set; C01 now shows **2 of 30**. That does not weaken the case for excluding
it — it strengthens it. Both echoing rows are `gemini25 th r1/r2`:

> ไม่อยู่ในขอบเขต "ว่ากล่าวสั่งสอนบุตรตามสมควร"

The model quotes the **repealed** phrase verbatim and is still scored `correct`,
because striking a child hard enough to bruise is outside scope under the old
text as much as the new. Anchoring is demonstrably occurring and the label cannot
see it. The recorded `exclusion_reason` states this, not the stale 0/24.

### 20. Exclusions applied

- **A09** (54 rows) — the prompt supplies the answer: instalment 5 alone unpaid,
  every other instalment paid on time, no acceleration clause, so 10,000 baht
  follows from general contract principle plus arithmetic. Evidence in the
  reason field: `typhoon25` scores 6/6 here while failing 50 of 60 group-X rows.
- **C01** (30 rows) — as above.

With B10 that is **119 raw responses now outside every metric** and still present
in `labelled.csv`. `analyze.py` prints all three ids and reasons into
`summary.txt`.

### 21. B07 regex replaced with the operative holding

Was the bare topic word `quorum` / `องค์ประชุม`, which the question itself uses,
so an answer denying that electronic attendance counts would still have matched.
Now requires the holding — that participants **count toward** the quorum:

- th `(?:นับ|ถือ)(?:เป็น|รวม|เข้า)?.{0,20}องค์ประชุม|องค์ประชุม.{0,20}(?:นับ|ได้)`
- en `count\w*\s+(?:toward|towards|in|as part of|for)?\s*(?:the\s+)?quorum|…`

Tested against all 36 rows before committing, per the B10 lesson: **36 correct
before, 36 after, zero false negatives.** The item keeps its current labels and
gains the ability to catch a negative answer if one appears.

### 22. law_facts.csv X6 effective_date

Set to **2019-05-05**. Act No. 7 B.E. 2562 was published 5 April 2019 (เล่ม 136
ตอนที่ 43 ก หน้า 21, matching the `gazette` column already recorded) and its s.2
uses "พ้นกำหนดสามสิบวันนับแต่วันประกาศ" — the same commencement convention as the
group D amendment — giving 5 April + 30 days = 5 May 2019. Arithmetic checked.

## Round 7 — C03 matching, and two dataset-wide flags

`parse.py` still not run; collection still adding rows. Verified in memory over
2192 raw records. C03's 22 ambiguous rows were read individually first: 6 were
genuine content failures, 16 were matcher misses.

### 23. C03 anchored side widened (item 1)

`anchored_regex_th` gained `อบรมสั่งสอน|ว่ากล่าวตักเตือน|ตักเตือน`; the literal
`ว่ากล่าวสั่งสอน` matched neither "ว่ากล่าวตักเตือน…อบรมสั่งสอน" (gpt4o) nor
"อบรมสั่งสอนหรือวินัย" (qwen3), although both recite only pre-amendment purposes.
`anchored_regex_en` gained `discipline`. Absent guards kept on both sides.

**`educat` was tested and NOT committed.** It fires on "the duty of parents to
care for, supervise, and **educate** their children" — a description of parental
duty in the chapeau, not a purpose of punishment — in `qwen3 en r1` and `r3`,
both of which explicitly say "does not authorize the punishment of a child for
any purpose". Committing it would have labelled two denials as `repealed` and
inflated the headline metric. Awaiting a decision: drop it, or pair it with a
denial guard so it only fires when the model is actually reciting a purpose.

### 24. C03 gold side fixed (items 2 and 3)

`gold_regex_en` had three defects at once: a 15-character ceiling that `gpt55 en
r1` overshot **by one character** ("modifying the child's behaviour" — gap 16),
and a bare `behavior` alternative that matched the American spelling on its own
while the British "behaviour" needed the prefix. Same answer, different spelling,
different label. Now `(?:modif|correct|adjust|chang)\w*.{0,40}behaviou?r|behaviou?r`,
which also drops the distance requirement as the more permissive fix the ceiling
was reaching for.

`gold_regex_th` is now `พฤติกรรม`, not `ปรับพฤติกรรม`, and
`anchored_absent_regex_th` was widened to match so the two stay symmetric.

**Interpretive decisions, recorded as such:**
- "ควบคุมพฤติกรรม" and "พัฒนาพฤติกรรม" **count as gold**. The 2568 amendment added
  behaviour modification as a distinct purpose; a model naming it with a different
  verb has demonstrated knowledge of the new limb, which is what the item tests.
- "misconduct" does **not** count as gold. Correcting misconduct already sits
  inside the pre-amendment "ว่ากล่าวสั่งสอน", so it is not evidence the model knows
  the new wording. Consequence: `typhoon25 en r1/r3` stay `ambiguous`. By the same
  reasoning they arguably belong in `anchored`, but adding "misconduct" there was
  not approved and is not done.

**15 rows change, every one in C03, nothing outside it:**

| rows | transition | why |
|---:|---|---|
| 9 | ambiguous → repealed | gpt4o en ×3, gpt4o th ×3, qwen3 th ×3 — old purposes only |
| 4 | ambiguous → correct | gpt55 en r1 (the one-character miss), typhoon25 th ×3 |
| 2 | **repealed → correct** | gpt55 th r2/r3 |

The last two were **false `repealed`**, found only because the change was tested
before committing. Both name the old purpose *and* the new one —
"1. ว่ากล่าวสั่งสอน 2. พัฒนาพฤติกรรมของบุตร" — but the old absent guard demanded the
exact string "ปรับพฤติกรรม", so it failed to block and a complete answer was scored
as anchored. Same failure mode as A09/A10 in round 1 and B10 in round 5.

C03 goes from 22 ambiguous / 4 repealed / 1 correct to **9 / 14 / 7**.

### 25. DELETED_WORDING widened (item 4)

`ตามสมควร` → `(?:ตาม|เท่าที่)สมควร`. Models paraphrase the deleted reasonableness
limb as "ทำโทษบุตรเท่าที่สมควรแก่เหตุ" as readily as they quote it. **5 more rows
flagged** — C02 gpt4o th r3, C03 gpt4o th r1/r2, C05 gpt4o th r3, C05 qwen3 th r1
— all confirmed to contain the phrase. Flag only; no label changes.

### 26. `denies_provision` flag (item 5)

New 0/1 column beside `hedged`, not a label, so the rubric ladder is untouched.
It marks a response asserting the provision does not exist, was repealed, or
authorises nothing.

**Read it with `frame`, never alone** — on a pre-frame item "there was no
provision yet" is the *correct* answer, on a post-frame item it is a factual
error. `analyze.py` therefore reports the two separately and breaks the
post-frame count down by model.

**A first draft flagged 75 rows and was wrong.** `do not specify` fired on "the
parties do not specify a rate" — the fact pattern of half of group A — giving 11
false positives on A03 alone. `specify` and `provide` were removed from the verb
list; the pattern now flags **61 rows: 41 pre-frame, 19 post-frame, 1 control**,
with A03 at zero. Post-frame hits concentrate in C03 (7), D08 (3), D09 (3).

## Known limitations not fixed

**The rubric is frozen as of round 7.** Everything below is recorded with
evidence and deliberately left alone. Nothing here should be changed without an
explicit decision — several are judgement calls, not defects.

### Items the rubric cannot currently classify

1. **`qwen3 en r2` on C03 stays `ambiguous`.** `educat` was dropped from
   `anchored_regex_en` because it produced two false positives (round 7, item 23).
   That was the right call for those two, but this row genuinely names the
   pre-amendment purposes and is now uncaptured:
   > "allows for reasonable disciplinary measures solely for the purposes of
   > **education or welfare** of the child … any disciplinary action must be for:
   > - Education - Welfare"

2. **`typhoon25 en r1/r3` on C03 stay `ambiguous`.** By the project's own
   reasoning — recorded in C03's `note` — "correct the child's misconduct" sits
   inside the pre-amendment "ว่ากล่าวสั่งสอน", so these arguably belong in
   `anchored`. Adding "misconduct" to the anchored pattern was never approved and
   was not done.

3. **C03 retains 9 `ambiguous` rows**: the 6 denial responses in (4) below, plus
   the 3 in (2).

4. **No label separates "the model denies the provision exists" from "the rubric
   could not classify".** The `denies_provision` flag now marks these 61 rows
   (19 post-frame), but they still land in `ambiguous`, so a factual error and a
   matcher gap share one bucket. Six C03 rows are of this kind, e.g.:
   > "the former Section 1567(2) … **was repealed** … the Code **no longer
   > specifies any purpose**" — `gemini25 en r2`, factually wrong (amended, not
   > repealed) and citing the wrong amending Act

5. **A15 has no `anchored_numbers`.** Three `gpt4o th` rows answer "ร้อยละ 7.5"
   on a control that states a 12% contractual rate — textbook anchoring to the
   repealed statutory rate, counted as `wrong_other`. Adding the field would
   change the vignette's control design, so it was left out of scope in round 1
   and remains so.

### Coverage gaps in the audits

6. **Only dual-rule vignettes were screened for the topic-word defect.** The
   B05/B09/D08/B11 fix came from a screen over vignettes carrying *both*
   `gold_numbers` and a `gold_regex`. Vignettes with a regex-only gold were never
   screened, and the same failure — a pattern matching the question's own subject
   word rather than the answer — can exist there undetected.

7. **B07's fix is unexercised.** The new pattern requires the holding rather than
   the bare word `quorum`, but all 36 responses answer affirmatively, so no row
   in the current data exercises the negative branch. Verified not to regress;
   not verified to catch anything.

8. **C02 and C05 carry 8 `ambiguous` rows each, unexamined.** Group C was checked
   for the echo signal (round 6, item 19) and C03 was read row by row; the
   ambiguous rows in C02 and C05 were not.

9. **`check_instruments.py` has never had its precision measured.** It reported
   25 findings on 360 responses when written; on the grown dataset it now reports
   **358 findings over 2125 responses**, none hand-checked. It is a standalone
   reporting script, not wired into the rubric, so it affects no label — but its
   output should not be quoted until reviewed.

10. **`denies_provision` may still over-fire.** One draft was corrected after it
    matched "the parties do not specify a rate" (11 false positives on A03). The
    surviving verb list was checked against the current data, not proven safe
    against phrasings that have not appeared yet.

### Provenance and tooling

11. **law_facts X6 `effective_date` = 2019-05-05 is derived, not sourced.**
    Computed from publication on 5 April 2019 plus the "พ้นกำหนดสามสิบวัน"
    commencement rule. `sources/statute_texts` is empty, so it has not been
    checked against the gazette text itself.

12. **`collect.py` records neither `finish_reason` nor `usage`.** The 13 empty
    responses therefore cannot be diagnosed from the saved records; the reasoning
    -model explanation for them remains inference.

13. **`analyze.py` raises `UnicodeEncodeError` on a cp874 console** (the `·` at
    line 74). Pre-existing and unrelated to any change here. Run it as
    `PYTHONIOENCODING=utf-8 python src/analyze.py`.

14. **`anchor_depth` and `denies_provision` are not yet in `labelled.csv`.** Both
    columns appear on the next `parse.py` run. `analyze.py` guards for their
    absence and degrades cleanly against the older file.

## Not done

- **A15** has no `anchored_numbers`, so three `gpt4o th` responses answering
  "ร้อยละ 7.5" on a control that states a 12% contractual rate are counted as
  `wrong_other` rather than as anchoring to the repealed rate. Adding
  `anchored_numbers: [7.5]` would change the vignette's design and was out of
  scope.
- `analyze.py` still raises `UnicodeEncodeError` on a cp874 console (the `·` at
  line 74). Pre-existing and unrelated; workaround is `PYTHONIOENCODING=utf-8`.
- `collect.py` does not record `finish_reason` or `usage`, so the cause of the
  four empty responses cannot be confirmed from the saved records.
