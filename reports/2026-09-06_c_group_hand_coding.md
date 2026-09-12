# Group C: choosing a denominator and hand-coding all 74 flagged responses

Follows `reports/2026-09-06_echo_flag_and_anchor_depth.md`. Read-only: no rubric
file, no vignette and no label was changed, and `collect.py` was not run. The
coding output is `reports/c_group_echo_coded.csv`.

---

## 1. Which denominator

| framing | rows flagged | Wilson 95% |
|---|---|---|
| (a) every group C row in the analysis set, as published | 74/240 = 30.8% | [25.3-36.9] |
| (b) minus C05, the pre-frame item | 49/192 = 25.5% | [19.9-32.1] |
| (c) post-frame only: C02 + C03 + C04 | **40/144 = 27.8%** | [21.1-35.6] |

**C06 is `frame: none` and `type: control`.** Its question is dated August 2026
and asks about s.1567(2) "as currently in force", so a model that quotes the
repealed wording there is genuinely stale, and the label cannot see it because
the yes-or-no answer is the same under both texts. That makes C06 real evidence,
but it is the control item for the accuracy metric, and putting it inside an
anchoring denominator would make one item serve two metrics at once.

**Recommendation: framing (c), post-frame only.** RSCR, the paper's headline
anchoring measure, is defined on post-frame items, so the deleted-wording
measure has to share that denominator for the two to be read side by side; C06's
eight rows are reported separately below as a supplementary observation.

---

## 2. Coding protocol, fixed before any row was read

The unit is one response. Categories were applied in this order.

1. **Decide from the response text alone.** The rubric label was not displayed
   while coding; labels were joined to the codes afterwards.
2. **GOLD**: the item is C05, which asks what the wording *was* in June 2024,
   and the response offers the phrase as the wording in force at that date. C05's
   `gold_regex_th` is literally `['ตามสมควร']`, so a hit there is the correct
   answer, not staleness.
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
   ("a reasonable disciplinary measure") rather than offered as statutory wording
   is not an assertion; only occurrences presented as the text or the legal
   standard of s.1567(2) are scored.
7. **UNCLEAR** where the text does not settle it. No guessing.
8. A fourth value was opened when rows fitted none of the three, per instruction.

**`CUTOFF_ONLY`, the fourth value.** Three responses state that they cannot give
the wording in force at the item's date because their knowledge ends earlier,
then quote the phrase as the text at *that earlier* date and tell the reader to
check an official source. They do not assert it for the item's date and do not
mark it superseded, so they are neither ASSERT nor CONTRAST; and the item is
post-frame, so GOLD cannot apply. They are best read as a refusal that leaks the
stale text, and they should not be counted either as anchoring or as clean
behaviour.

**UNCLEAR: 0 rows.** Every one of the 74 was decidable.

---

## 3. Results

### category by label

| category | correct | repealed | over_applied | wrong_other | refusal | ambiguous | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| ASSERT | 31 | 11 | 0 | 0 | 0 | 0 | **42** |
| CONTRAST | 3 | 1 | 0 | 0 | 0 | 0 | 4 |
| GOLD | 22 | 0 | 0 | 0 | 1 | 2 | 25 |
| CUTOFF_ONLY | 0 | 2 | 0 | 0 | 1 | 0 | 3 |
| UNCLEAR | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**Only 11 of the 42 ASSERT rows carry the label `repealed`.** Thirty-one are
scored `correct`. The rubric ladder tests the gold bucket before the anchored
bucket, so a response that names the current rule anywhere and also states the
repealed wording as current is scored `correct` and never reaches the anchored
test. On the post-frame denominator this is 23 rows of 34.

### category by frame

| category | post | pre | none (control) | total |
|---|---:|---:|---:|---:|
| ASSERT | 34 | 0 | 8 | 42 |
| CONTRAST | 3 | 0 | 1 | 4 |
| GOLD | 0 | 25 | 0 | 25 |
| CUTOFF_ONLY | 3 | 0 | 0 | 3 |

### category by vignette and by model

| vignette | ASSERT | CONTRAST | GOLD | CUTOFF_ONLY |
|---|---:|---:|---:|---:|
| C02 (post) | 15 | 2 | 0 | 3 |
| C03 (post) | 10 | 1 | 0 | 0 |
| C04 (post) | 9 | 0 | 0 | 0 |
| C05 (pre) | 0 | 0 | 25 | 0 |
| C06 (control) | 8 | 1 | 0 | 0 |

| model | ASSERT | CONTRAST | GOLD | CUTOFF_ONLY |
|---|---:|---:|---:|---:|
| gemini-3.1 | 16 | 0 | 6 | 0 |
| claude-5 | 8 | 4 | 6 | 2 |
| gemini-2.5 | 8 | 0 | 3 | 0 |
| gpt-5.5 | 6 | 0 | 3 | 0 |
| gpt-4o | 2 | 0 | 3 | 1 |
| claude-4.5 | 2 | 0 | 3 | 0 |
| qwen3 | 0 | 0 | 1 | 0 |
| typhoon-2.5 | 0 | 0 | 0 | 0 |

---

## 4. The number for the paper

**On the recommended denominator, 34 of 144 post-frame group C responses assert
the repealed wording as the rule in force: 23.6% [17.4-31.2].**

For comparison on the other two framings: 42/240 = 17.5% [13.2-22.8] over all
group C, and 42/192 = 21.9% [16.6-28.2] excluding C05.

By model, on the post-frame denominator of 18 rows each:

| model | ASSERT | Wilson 95% |
|---|---|---|
| gemini-3.1 | 13/18 = 72.2% | [49.1-87.5] |
| gemini-2.5 | 7/18 = 38.9% | [20.3-61.4] |
| claude-5 | 6/18 = 33.3% | [16.3-56.3] |
| gpt-5.5 | 6/18 = 33.3% | [16.3-56.3] |
| gpt-4o | 2/18 = 11.1% | [3.1-32.8] |
| claude-4.5 | 0/18 = 0.0% | [0.0-17.6] |
| qwen3 | 0/18 = 0.0% | [0.0-17.6] |
| typhoon-2.5 | 0/18 = 0.0% | [0.0-17.6] |

By language: Thai 28/72 = 38.9% [28.5-50.4], English 6/72 = 8.3% [3.9-17.0].

Two things follow, and the first corrects an explanation offered in the previous
report. **The model ordering survives hand-coding.** `gemini-3.1` really does
assert the repealed wording most often; verbosity explains why it trips the raw
flag on C05 and C06 as well, but it does not explain away 13 of 18 post-frame
assertions. **The signal is largely invisible to RSCR**, because 23 of these 34
rows are scored `correct`.

**Side finding, needs its own audit.** C02's `gold_regex_th` is the single word
`ทารุณกรรม`, which models also use when citing the Child Protection Act rather
than the amended s.1567(2). In the C02 rows coded ASSERT and labelled `correct`,
six of the eight occurrences examined sit next to `พ.ร.บ.คุ้มครองเด็ก`, not next
to s.1567. Example, `gemini-3.1 th r1`, which quotes the repealed text as current
and is still scored `correct`:

> แม้ ป.พ.พ. จะอนุญาตให้ทำโทษ "ตามสมควร" แต่ในทางปฏิบัติจะต้องไม่ขัดต่อ
> พ.ร.บ.คุ้มครองเด็กฯ มาตรา 26 (1) ที่ห้ามมิให้ผู้ใดกระทำการ**ทารุณกรรม**ต่อร่างกาย
> หรือจิตใจของเด็ก

That is a candidate false-`correct` mechanism in the label itself, not only in
the flag. It is recorded, not fixed.

---

## 5. One sentence for the paper

> A response was coded as still asserting the repealed wording when it presented
> *tam samkhuan* as part of s.1567(2) as in force at the date stated in the item,
> rather than marking it as the former text or declining to give the current one.

---

## 6. Two clearest examples per category

**ASSERT**

```
C02 gemini-3.1 th r1   [label=correct]
ถ้อยคำจากตัวบทที่ใช้บังคับ ปัจจุบัน (อ้างอิงตามสถานะกฎหมายที่ประกาศใช้บังคับล่าสุด)
... > "(2) ทำโทษบุตร<<<ตามสมควร>>>เพื่อว่ากล่าวสั่งสอน"
```

```
C03 gemini-3.1 th r2   [label=repealed]   (full response)
บทบัญญัติที่ใช้บังคับ: ประมวลกฎหมายแพ่งและพาณิชย์ มาตรา 1567 (2) สาระสำคัญและ
วัตถุประสงค์: กฎหมายกำหนดให้ผู้ใช้อำนาจปกครองมีสิทธิทำโทษบุตรได้<<<ตามสมควร>>>
โดยมีวัตถุประสงค์เพื่อ "ว่ากล่าวสั่งสอน" เท่านั้น
```

**CONTRAST**

```
C03 claude-5 th r1   [label=correct]
... ซึ่งเป็นการเปลี่ยนแปลงจากบทบัญญัติเดิมที่ให้อำนาจ "ทำโทษบุตร<<<ตามสมควร>>>
เพื่อว่ากล่าวสั่งสอน" โดยไม่มีการระบุข้อห้ามเรื่องความทารุณไว้อย่างชัดเจน
```

```
C02 claude-5 th r2   [label=repealed]
เดิมมาตรา 1567 (2) ใช้ถ้อยคำว่า "ทำโทษบุตร<<<ตามสมควร>>>เพื่อว่ากล่าวสั่งสอน" ...
ต่อมาได้มีการแก้ไขถ้อยคำเพื่อจำกัดขอบเขตการทำโทษบุตรให้ชัดเจนยิ่งขึ้น
```

**GOLD**

```
C05 claude-4.5 th r1   [label=correct]
ตามประมวลกฎหมายแพ่งและพาณิชย์ มาตรา 1567(2) ที่ใช้บังคับในเดือนมิถุนายน 2567
กำหนดขอบเขตการทำโทษบุตรไว้ด้วยถ้อยคำว่า "ทำโทษบุตรได้<<<ตามสมควร>>>"
```

```
C05 claude-5 en r2   [label=correct]
Wording in force as of June 2024 (before the later 2024 amendment that removed
this clause): Thai text: > "(๒) ทำโทษบุตร<<<ตามสมควร>>>เพื่อว่ากล่าวสั่งสอน"
```

**CUTOFF_ONLY**

```
C02 gpt-4o th r3   [label=refusal]
ขออภัยค่ะ ฉันไม่สามารถให้ข้อมูลเกี่ยวกับกฎหมายที่อาจมีการแก้ไข ... หลังจากเดือน
ตุลาคม 2566 ได้ ... หากคุณต้องการทราบถ้อยคำ ... ที่ใช้บังคับอยู่ ณ เดือนตุลาคม 2566
(ข้อมูลล่าสุดที่ฉันมี) ... (2) ว่ากล่าวตักเตือนและลงโทษบุตรได้<<<เท่าที่สมควร>>>แก่เหตุ
```

```
C02 claude-5 en r1   [label=repealed]
I don't have verified access to the current text of Section 1567(2) ... as it
stands "as of August 2026" ... Historically, Section 1567(2) has been understood
to permit parents to "punish the child in a reasonable manner for disciplinary
purposes" (ทำโทษบุตร<<<ตามสมควร>>>เพื่อการอบรม). Important caveat — recent legal
reform ... I am not certain whether an amendment has actually been enacted.
```

---

## Files

- `reports/c_group_echo_coded.csv`: 74 rows, columns `vignette, model, lang,
  run, label, frame, category, evidence_span`. Spans run 80 characters either side of
  the occurrence the code was decided on. UTF-8 with BOM so Excel opens the Thai
  correctly.
