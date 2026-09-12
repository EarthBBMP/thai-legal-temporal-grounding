# Group C, second coding pass

## What this measures, and what it cannot

**This is a consistency check, not a validation.** The same coder produced both
passes, with the pass-1 decisions still fresh in mind.
Agreement between the two is therefore inflated by an unknown amount and says
nothing on its own about whether either pass is right. Nothing below should be
read as "the coding is confirmed".

Two things were done to give the second pass a chance to differ. The pass-1 CSV
was not opened until all 74 rows had been recoded. And where pass 1 worked from
windows of 300 characters either side of the matched phrase, pass 2 read every
response in full (66,687 characters) with the `label` column withheld. Several
responses turn out to say things outside the pass-1 window that bear on the
code, which is the one place where a real difference could have surfaced.

One leak to disclose: the protocol section of the pass-1 report ends with the
line "UNCLEAR: 0 rows", which is a result rather than a criterion, and it was
visible when the criteria were copied.

Read-only. No file from the earlier passes was modified; `parse.py` and
`collect.py` were not run; the paper was not touched.

---

## Step 1: the criteria, copied from the pass-1 protocol

1. **Decide from the response text alone.** The rubric label is not displayed
   while coding.
2. **GOLD**: the item is C05, which asks what the wording *was* in June 2024,
   and the response offers the phrase as the wording in force at that date.
   C05's `gold_regex_th` is literally `['ตามสมควร']`, so a hit there is the
   correct answer, not staleness.
3. **ASSERT**: the response presents `ตามสมควร` or `เท่าที่สมควร` as part of the
   wording, limit or standard of s.1567(2) **in force at the date the item
   states**, without marking it as superseded. This holds whether the phrase is
   quoted as the whole provision or retained inside the model's rendition of the
   amended provision.
4. **CONTRAST**: every occurrence in the response is explicitly marked as the
   former text (`เดิม`, `จากเดิม`, `ตัดถ้อยคำเดิม`, `ต่อมาได้มีการแก้ไข`,
   `Historically`, `previously`, `has been replaced`), and the response gives a
   different rule as the current one.
5. **Strongest-claim rule.** If one occurrence asserts and another contrasts, the
   row is ASSERT. CONTRAST requires that no occurrence asserts.
6. **Ordinary-language use does not count.** `ตามสมควร` used as everyday Thai
   rather than offered as statutory wording is not an assertion.
7. **UNCLEAR** where the text does not settle it. No guessing.
8. **CUTOFF_ONLY**: the response states that it cannot give the wording in force
   at the item's date because its knowledge ends earlier, then quotes the phrase
   as the text at *that earlier* date and points the reader to an official
   source. Neither ASSERT nor CONTRAST; "and the item is post-frame, so GOLD
   cannot apply."

The clause in quotation marks at the end of (8) is the one that decided all three
disagreements. See step 4.

---

## Step 2: pass-2 output

`reports/c_group_recode_pass2.csv`, 74 rows, columns `vignette, model, lang, run,
category2, span2, reason`. Distribution: ASSERT 42, GOLD 22, CUTOFF_ONLY 6,
CONTRAST 4, **UNCLEAR 0**.

---

## Step 3: comparison

### 1. Overall agreement

**71 of 74 = 95.9% [88.7-98.6]**, Wilson 95%.

### 2. Confusion matrix, rows = pass 1, columns = pass 2

| | ASSERT | CONTRAST | GOLD | CUTOFF_ONLY | UNCLEAR | total |
|---|---:|---:|---:|---:|---:|---:|
| **ASSERT** | 42 | 0 | 0 | 0 | 0 | 42 |
| **CONTRAST** | 0 | 4 | 0 | 0 | 0 | 4 |
| **GOLD** | 0 | 0 | 22 | **3** | 0 | 25 |
| **CUTOFF_ONLY** | 0 | 0 | 0 | 3 | 0 | 3 |
| **UNCLEAR** | 0 | 0 | 0 | 0 | 0 | 0 |
| **total** | 42 | 4 | 22 | 6 | 0 | 74 |

The only off-diagonal cell is pass-1 GOLD against pass-2 CUTOFF_ONLY, three rows.

### 3. Agreement on the post-frame rows, the set the 34/144 figure uses

**40 of 40 = 100.0% [91.2-100.0].** Every disagreement is on C05, which is
pre-frame and contributes nothing to that denominator.

### 4. Every disagreement

All three are the same model on the same item, and the same reasoning applies to
each.

**C05, gpt-4o, th, r1**: pass 1 GOLD, pass 2 CUTOFF_ONLY
> ...ขออภัยค่ะ ฉันไม่มีข้อมูลเกี่ยวกับกฎหมาย...ในอนาคต (เช่น เดือนมิถุนายน 2567)
> เนื่องจากข้อมูลที่ฉันได้รับการฝึกอบรมมีถึงเดือนตุลาคม 2566 เท่านั้น ... ฉันสามารถให้
> ข้อมูล...ที่ใช้บังคับในปัจจุบัน (ข้อมูลถึงตุลาคม 2566) ได้ดังนี้: ... "(2) ทำโทษบุตรได้
> **ตามสมควร**เพื่อว่ากล่าวสั่งสอน" หากมีการแก้ไขเพิ่มเติมในอนาคต ขอแนะนำให้ตรวจสอบ...

**C05, gpt-4o, th, r2**: pass 1 GOLD, pass 2 CUTOFF_ONLY
> ...ฉันไม่สามารถยืนยันถ้อยคำของ...มาตรา 1567(2) ที่ใช้บังคับในเดือนมิถุนายน 2567 ได้
> อย่างไรก็ตาม ฉบับที่ใช้บังคับถึงปี 2566 ระบุว่า: ... "ว่ากล่าวตักเตือนและทำโทษบุตรได้
> **ตามสมควร**แก่เหตุ" หากต้องการข้อมูลที่แน่นอน...ขอแนะนำให้ตรวจสอบ...

**C05, gpt-4o, th, r3**: pass 1 GOLD, pass 2 CUTOFF_ONLY
> ...ฉันไม่สามารถยืนยันถ้อยคำ...ที่ใช้บังคับในเดือนมิถุนายน 2567 ได้ อย่างไรก็ตาม ฉบับที่
> ใช้บังคับในช่วงก่อนเดือนตุลาคม 2566 มีถ้อยคำดังนี้: "(2) ทำโทษบุตรได้**เท่าที่สมควร**
> แก่เหตุ" หากต้องการข้อมูลที่แน่นอน...ขอแนะนำให้ตรวจสอบ...

**Pass-2 reason, identical for all three:** the response declines to state the
wording at the date the item asks about, then quotes the phrase as the text at
its own cutoff and refers the reader elsewhere. That is the CUTOFF_ONLY
behaviour word for word. GOLD requires the phrase to be offered *as the June 2024
wording*, and none of the three does that; each answers for October 2023 while
saying it cannot answer for June 2024.

**Why pass 1 said GOLD.** The CUTOFF_ONLY definition as written ends with "and
the item is post-frame, so GOLD cannot apply". Read as part of the definition,
that clause makes CUTOFF_ONLY unavailable on a pre-frame item, which forces these
three rows into GOLD. Read as a description of the three rows that happened to be
in the category, it does not. The pass-1 report states it in definitional form.
This is a defect in how the protocol was written, not a difference in reading the
responses: both passes agree on what these three responses say.

Note the direction. October 2023 and June 2024 sit on the same side of the March
2025 amendment, so the wording these three give is in fact the wording that was
in force at the item's date. Whether that is scored GOLD or CUTOFF_ONLY is a
question about what the categories are for, not about whether the model was
right.

### 5. ASSERT on post-frame, both passes

| | k/n | rate | Wilson 95% |
|---|---|---|---|
| pass 1 | 34/144 | 23.6% | [17.4-31.2] |
| **pass 2** | **34/144** | **23.6%** | **[17.4-31.2]** |

Identical. The difference is zero rows, so no alarm is raised.

---

## Step 4: the two straight answers

**The 34/144 = 23.6% [17.4-31.2] figure in the paper stands as published.** Both
passes assign the same category to all 40 post-frame flagged rows, and the three
rows that moved are on the pre-frame item, which that denominator excludes by
construction; if the paper also reports the category counts, the GOLD/CUTOFF_ONLY
split changes from 25/3 to 22/6 and would need updating there.

**Four places where the criteria are genuinely ambiguous, and I would rather name
them than let the agreement number look cleaner than it is.** First, rule 8's
"the item is post-frame" clause, which caused all three disagreements and should
be rewritten as a behavioural test with no frame condition. Second, `C02
claude-5 th r3`, coded ASSERT on a single clause ("เป็นไปเพื่อว่ากล่าวสั่งสอน
บุตรตามสมควรเท่านั้น") inside an answer that is otherwise a clean contrast; only
the strongest-claim rule decides it, and a coder weighting the response as a
whole would say CONTRAST. Third, `C05 claude-5 th r2`, which dates the amendment
to April 2024, marks the true then-current wording as former, and yet keeps the
phrase inside the text it presents as in force in June 2024; it is GOLD on one
occurrence and would be CONTRAST on the other. Fourth, and largest, the nine rows
where the phrase survives inside an otherwise correctly amended provision (most
of the `gpt-5.5` rows, plus `C04 claude-5 th r1` and two C06 rows), which rule 3
makes ASSERT by its second sentence, but which are weaker evidence of staleness
than a wholesale quotation of the repealed text and might deserve a category of
their own.
