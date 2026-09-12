# Two audits after Round 8

Read-only. No file in `data/`, `src/` or `docs/` was changed and `collect.py` was
not run. Everything below is recomputed from `out/labelled.csv` (3,036 rows,
byte-identical to the 2026-08-28 run) and the raw responses in `raw/`.

Written 2026-09-06.

---

## 1. What the group C deleted-wording flag actually measures

### 1.1 The suspicion, restated

Round 8 reported that `gemini-3.1` (22/30) and `claude-5` (20/30) trip the flag
most often while `qwen3` (1/30) and `typhoon-2.5` (0/30) barely trip it at all.
That is the reverse of their RSCR ordering. If the flag were measuring staleness, the
weakest models should trip it most.

### 1.2 Cross-tab, echo by label, 240 non-excluded group C rows

| echo | correct | repealed | over_applied | wrong_other | refusal | ambiguous | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| **1** | 56 | 14 | 0 | 0 | 2 | 2 | **74** |
| 0 | 79 | 19 | 1 | 27 | 12 | 28 | 166 |

**56 of the 74 flagged rows are labelled `correct`.** Only 14 are `repealed`.

By model, with the label split of the flagged rows:

| model | echo=1 | correct | repealed | refusal | ambiguous |
|---|---|---:|---:|---:|---:|
| gemini-3.1 | 22/30 | 18 | 4 | 0 | 0 |
| claude-5 | 20/30 | 16 | 4 | 0 | 0 |
| gemini-2.5 | 11/30 | 7 | 4 | 0 | 0 |
| gpt-5.5 | 9/30 | 9 | 0 | 0 | 0 |
| gpt-4o | 6/30 | 1 | 2 | 2 | 1 |
| claude-4.5 | 5/30 | 5 | 0 | 0 | 0 |
| qwen3 | 1/30 | 0 | 0 | 0 | 1 |
| typhoon-2.5 | 0/30 | 0 | 0 | 0 | 0 |

By language: Thai 60/120 (45 correct, 11 repealed, 2 refusal, 2 ambiguous),
English 14/120 (11 correct, 3 repealed).

### 1.3 The decisive split is by frame, and it is not visible in the published figure

The flag is applied to **every** group C row regardless of the item's temporal
frame. The five non-excluded vignettes are not asking the same kind of question:

| vignette | frame | rows | echo=1 | what a hit means there |
|---|---|---:|---:|---|
| C02 | post | 48 | 20 | `anchored_regex_th` is the *same string*, so the flag re-tests the label |
| C03 | post | 48 | 11 | independent of the anchored regex (which is `ว่ากล่าวสั่งสอน\|...`) |
| C04 | post | 48 | 9 | vignette has no anchored regex at all |
| **C05** | **pre** | 48 | **25** | **`gold_regex_th` is `['ตามสมควร']`, so a hit *is* the correct answer** |
| C06 | none | 48 | 9 | control item; the yes/no answer is the same under both texts |

Grouped:

| frame | echo=1 | labels of those rows |
|---|---|---|
| post (C02, C03, C04) | 40 / 144 | correct 25, repealed 14, refusal 1 |
| **pre (C05)** | **25 / 48** | **correct 22**, refusal 1, ambiguous 2 |
| control (C06) | 9 / 48 | correct 9 |

C05 asks what the wording *was* in June 2024, nine months before the amendment.
Quoting `ตามสมควร` there is the gold answer by construction: 22 of the 25 flagged
C05 rows are scored `correct` **because** they contain the phrase. Those 25 rows
are one third of the published 74 and they cannot be evidence of staleness under
any reading.

### 1.4 One string, three jobs

```
C05  gold_regex_th     = ['ตามสมควร']          -> a hit means CORRECT
C02  anchored_regex_th = ['ตามสมควร']          -> a hit means REPEALED
parse.py DELETED_WORDING = (?:ตาม|เท่าที่)สมควร -> a hit sets the flag, on every group C row
```

On C02 the flag and the anchored bucket are the same test, so the flag adds no
independent signal: 7 of C02's 20 flagged rows are `repealed` and the flag
column simply restates that. On C05 the same string is the gold answer. The flag
is not frame-aware, so it cannot tell these apart.

A second, smaller contaminant: the still-in-force s.1567(3) reads
`ให้บุตรทำการงานตามสมควรแก่ความสามารถและฐานานุรูป`, so a model that quotes the
whole current section trips the pattern on wording that was never deleted. Only
2 rows (both `gemini-2.5`) match on (3) alone, so this is real but marginal. Of
the 74 rows, 50 do contain the deleted limb of (2) somewhere, 22 match on
wording too loose to attribute, and 2 match only on (3).

### 1.5 Verbatim evidence

Nine excerpts, `<<<...>>>` marks the matched phrase.

**(a) Explaining the old wording as superseded: correct behaviour, flagged**

```
C02 claude-5 th r1  label=correct
... กฎหมายที่แก้ไขใหม่ได้เปลี่ยนแปลงถ้อยคำจากเดิมที่ให้สิทธิ "ทำโทษบุตร<<<ตามสมควร>>>
เพื่อว่ากล่าวสั่งสอน" อย่างกว้างๆ โดยไม่มีข้อจำกัดชัดเจน มาเป็นการจำกัดขอบเขตการทำโทษบุตร
อย่างชัดแจ้ง เพื่อคุ้มครองสิทธิเด็ก ...
```

```
C03 claude-5 th r1  label=correct
... ซึ่งเป็นการเปลี่ยนแปลงจากบทบัญญัติเดิมที่ให้อำนาจ "ทำโทษบุตร<<<ตามสมควร>>>
เพื่อว่ากล่าวสั่งสอน" โดยไม่มีการระบุข้อห้ามเรื่องความทารุณไว้อย่างชัดเจน
```

```
C02 claude-5 th r2  label=repealed
... เดิมมาตรา 1567 (2) ใช้ถ้อยคำว่า "ทำโทษบุตร<<<ตามสมควร>>>เพื่อว่ากล่าวสั่งสอน" ...
ต่อมาได้มีการแก้ไขถ้อยคำเพื่อจำกัดขอบเขตการทำโทษบุตรให้ชัดเจนยิ่งขึ้น
```

The third one is labelled `repealed` even though the prose describes the
amendment correctly; the `anchored` regex fired on the quoted old purpose
wording. The label, not only the flag, is caught by explanatory quotation.

**(b) Asserting the old wording as the rule in force: genuine anchoring**

```
C03 gemini-3.1 en r3  label=repealed
Provision: Section 1567(2) ... What it requires: The provision grants a person
exercising parental power the right to punish a child, requiring that any such
punishment must be carried out in a "reasonable manner" (<<<ตามสมควร>>>).
Purposes for punishment: Under the Thai text of the provision (เพื่อว่ากล่าวสั่งสอน) ...
```

```
C02 gpt-4o th r3  label=refusal
... มาตรา 1567(2) ที่ใช้บังคับอยู่ ณ เดือนตุลาคม 2566 (ข้อมูลล่าสุดที่ฉันมี) มีเนื้อหาดังนี้:
(2) ว่ากล่าวตักเตือนและลงโทษบุตรได้<<<เท่าที่สมควร>>>แก่เหตุ
```

```
C06 gemini-3.1 th r1  label=correct   [control item]
อยู่ในขอบเขต ... มาตรา 1567 (2) สาระสำคัญ: ผู้ใช้อำนาจปกครองมีสิทธิทำโทษบุตร
<<<ตามสมควร>>>เพื่อว่ากล่าวสั่งสอน (ซึ่งการงดเงินค่าขนม ... ถือเป็นการทำโทษ
<<<ตามสมควร>>>ที่อยู่ในขอบเขตของกฎหมาย)
```

The C06 row is the case the flag was built for: the model states the repealed
text as current law, the item is a control whose yes/no answer is unchanged by
the amendment, so the label cannot see it and only the flag does.

**(c) The pre-frame item, where a hit is the right answer**

```
C05 claude-4.5 th r1  label=correct
ตามประมวลกฎหมายแพ่งและพาณิชย์ มาตรา 1567(2) ที่ใช้บังคับในเดือนมิถุนายน 2567
กำหนดขอบเขตการทำโทษบุตรไว้ด้วยถ้อยคำว่า "ทำโทษบุตรได้<<<ตามสมควร>>>"
```

```
C05 claude-5 th r1  label=correct
... บทบัญญัติที่ใช้บังคับอยู่ในขณะนั้นจึงยังเป็นถ้อยคำเดิม ซึ่งบัญญัติไว้ว่า
"ทำโทษบุตร<<<ตามสมควร>>>เพื่อว่ากล่าวสั่งสอน" ...
```

**(d) Mixed, for completeness**

```
C02 gemini-3.1 en r1  label=correct
... (Note on the Thai text: The specific wording for subsection 2 is
"ทำโทษบุตร<<<ตามสมควร>>>เพื่อว่ากล่าวสั่งสอน", which directly translates to punishing
the child as appropriate/reasonable for the purpose of instruction). Important
Context Regarding your "August 2026" Timeframe: While the wording q...
```

Present tense "is", followed by a hedge about the timeframe. This is the class
the flag cannot resolve without reading further.

### 1.6 Verdict

**The flag does not separate the two behaviours.** It is a substring test with no
awareness of the item's frame, of who is asserting what, or of the tense the
phrase is embedded in. Three distinct populations sit inside the published 74:

| population | rows | can it evidence anchoring? |
|---|---:|---|
| C05, pre-frame, phrase is the gold answer | 25 | no, never |
| C02/C03/C04/C06 with explicit contrast framing nearby | 20 | no, the model is describing the change |
| C02/C03/C04/C06 with the phrase presented flat | 29 | yes, candidate anchoring |

The contrast test used here is a marker within 150 characters of the match:
`เดิม`, `ก่อนแก้ไข`, `ยกเลิก`, `แก้ไขเพิ่มเติม`, `ต่อมา`, `ในอดีต`, `former`,
`previously`, `historically`, `traditionally`, `used to`, `prior to`, `repealed`,
`replaced`, `no longer`. It is a heuristic and the 29 have not been hand-read.

Three defensible denominators, for comparison:

| framing | figure |
|---|---|
| as published | 74/240 = 30.8% |
| dropping the pre-frame item C05 | 49/192 = 25.5% |
| also dropping explicit contrast framing | 29/192 = 15.1% |

The model ordering explains itself once the split is applied: `claude-5` and
`gemini-3.1` trip the flag mostly by *narrating the amendment* (`claude-5` has 10
of the 17 post-frame contrast-framed rows), while `typhoon-2.5` and `qwen3` never
quote statutory wording at all; their group C answers are short and give no text
to match. The flag is partly measuring verbosity and willingness to quote Thai
statute, not staleness.

### 1.7 Proposed discriminator, not implemented

No code was written. A future version would need all three of these, and the
first is the one that matters:

1. **Make the flag frame-aware.** Compute it only on `frame in {post, none}`
   items, or emit it as `echo_on_post_frame` alongside the raw count. This alone
   removes the 25 C05 rows, which is the largest single defect.
2. **Add a negative guard for contrast framing.** The match is not evidence if a
   superseded-marker appears within a window of it. The marker list above is the
   starting point; the window needs tuning because `claude-5` sometimes places
   the marker two sentences away.
3. **Guard the still-in-force limb.** Require that the match is not part of
   `(?:ทำการงาน|การงาน)\s*ตามสมควร`, which is s.1567(3) and was never deleted.
   Worth 2 rows today but it is a correctness bug regardless.

A fourth, optional: on C02 the flag is redundant with `anchored_regex_th`, so
either the flag or that regex should be dropped for that vignette to stop one
signal being counted twice.

---

## 2. `anchor_depth = 2`, re-cut by filter

Round 8 recorded that a vignette with `anchored_prior_numbers` but no
`anchored_numbers` sends a one-amendment-back answer straight to depth 2. This
section applies the filter rather than changing the rubric.

### 2.1 Genuine two-amendments-back rows: 10

Vignettes where a third layer really exists: **D01** (post-frame, asks about
August 2026 when 120/60 is in force, so 90/45 is two amendments back through
98/45) and **D16** (the matched pair, same ladder).

| model | th | en | total |
|---|---:|---:|---:|
| typhoon-2.5 | 3 | 3 | 6 |
| qwen3 | 3 | 0 | 3 |
| claude-4.5 | 0 | 1 | 1 |
| **total** | **6** | **4** | **10** |

By vignette: D01 9, D16 1. Denominator, scorable rows on D01 and D16 combined:
96. No other model produces a genuine depth-2 answer.

### 2.2 Mis-assigned rows: 15, one amendment back, not two

| model | th | en | total |
|---|---:|---:|---:|
| typhoon-2.5 | 6 | 5 | 11 |
| claude-4.5 | 0 | 3 | 3 |
| qwen3 | 1 | 0 | 1 |
| **total** | **7** | **8** | **15** |

By vignette: D02 9, D12 6. Both are **pre-frame** items dated before the December
2025 amendment, so the rule in force at the date in the question is 98 days
(D02 also 45 paid) and an answer of 90 is exactly one amendment behind. They
receive depth 2 only because neither vignette defines `anchored_numbers`, so the
`anchored_prior` bucket is the first anchored bucket the ladder reaches.

Correct reading of the 25: **10 genuinely two back, 15 one back.**

### 2.3 Vignettes carrying `anchored_prior_*`

| vignette | group | frame | fields |
|---|---|---|---|
| D01 | D | post | `anchored_prior_numbers: [90, 45]` |
| D02 | D | pre | `anchored_prior_numbers: [90, 45]` |
| D12 | D | pre | `anchored_prior_numbers: [90]` |
| D16 | D | pair | `anchored_prior_numbers: [90, 45]`, `anchored_prior_absent_numbers: [98, 120]` |

**No vignette outside group D carries any `anchored_prior_*` field**, so no other
group can produce a depth-2 row and the defect is confined to D02 and D12.

### 2.4 Full text of all ten genuine depth-2 rows

All are `label=repealed`. D01 gold `[120, 60]`, anchored `[98, 45]`,
anchored_prior `[90, 45]`. D16 gold `[98, 45, 120, 60]`.

**D01, claude-4.5, en, r3**
> Under Thai law, specifically the Labour Protection Act B.E. 2541 (1998) as
> amended: 90 days of maternity leave per pregnancy. 45 days must be paid by the
> employer (at the employee's regular wage rate). The pregnant employee is
> entitled to take up to 90 days of maternity leave total, but the employer is
> only required to pay wages for 45 of those days. The remaining 45 days are
> unpaid leave (though the employee may be eligible for social security benefits
> during this period).

**D01, qwen3, th, r1**
> 90 วัน และ 45 วัน

**D01, qwen3, th, r2**
> 90 วัน, 45 วัน

**D01, qwen3, th, r3**
> 90 วัน และ 45 วัน

**D01, typhoon-2.5, en, r1**
> As of August 2026, a pregnant employee in the Thai private sector is entitled
> to 90 days of maternity leave per pregnancy, and the employer must pay wages
> for 45 of those days.

**D01, typhoon-2.5, en, r2**
> As of August 2026, a pregnant employee in the Thai private sector is entitled
> to 90 days of maternity leave per pregnancy, and the employer must pay wages
> for 45 of those days.

**D01, typhoon-2.5, th, r1**
> ลูกจ้างหญิงมีสิทธิลาเพื่อคลอดบุตรได้ไม่เกิน 90 วัน และนายจ้างต้องจ่ายค่าจ้างไม่เกิน 45 วัน

**D01, typhoon-2.5, th, r2**
> ลูกจ้างหญิงมีสิทธิลาเพื่อคลอดบุตรได้ไม่เกิน 90 วัน และนายจ้างต้องจ่ายค่าจ้างไม่เกิน 45 วัน

**D01, typhoon-2.5, th, r3**
> ลูกจ้างหญิงมีสิทธิลาเพื่อคลอดบุตรได้ไม่เกิน 90 วัน และนายจ้างต้องจ่ายค่าจ้างไม่เกิน 45 วัน

**D16, typhoon-2.5, en, r3**
> Under Thailand's Labor Protection Act (as amended), Kanokwan (born 1 October
> 2025) was entitled to 90 days of maternity leave, with the employer required to
> pay her for 45 days. Kwanruethai (born 1 May 2026) was also entitled to 90 days
> of maternity leave, with the employer required to pay her for 45 days. Both
> were entitled to the same benefits under current law.

Three of the ten cite the 1998 Act by name while answering a question dated
August 2026. The D16 row is the strongest single case in the dataset: it gives
one answer for two dates that the law treats differently, and the answer is the
1998 rule.

---

## Bottom line

**Topic 1: the sentence must be rewritten.** The paper's line "30.8%
[25.3--36.9] (74/240) of group C responses in both languages still quote the
deleted phrase", offered as "the cleanest single piece of evidence", cannot carry
that weight: one third of the 74 come from the pre-frame item C05 where quoting
the phrase is the gold answer, and another 20 are models explicitly narrating
that the wording was replaced.

**Topic 2: no published sentence is affected.** `anchor_depth` appears nowhere
in the paper, and the corrected split is 10 genuine two-amendments-back rows on
D01 and D16 against 15 one-back rows mis-assigned on D02 and D12; no vignette
outside group D can produce the defect.
