# How far the gold-before-anchored ordering reaches

Counting exercise, no judgement calls. For every row in the 2,881-row analysis
set the vignette's gold bucket and its anchored bucket were evaluated
**independently**, using `parse.py`'s own `bucket_hit` and `strip_markdown` so the
matching is identical to the grader, but without the ladder that stops at the
first hit. Read-only: no rubric file, no vignette, no label changed, `parse.py`
was not re-run and `collect.py` was not run. Published numbers are untouched.

Follows `reports/2026-09-06_c_group_hand_coding.md`.

---

## 5. The real denominator

A vignette that defines no anchored pattern can never produce a double hit, so it
cannot be in the denominator. **Thirty-two of the fifty-seven non-excluded
vignettes define no anchored bucket in either language**, covering 1,594 rows:

| group | vignettes with no anchored pattern |
|---|---|
| A | A02, A07, A12, A15, A16 |
| B | B02, B03, B04, B08, B11, B12 |
| C | C04, C05, C06 |
| D | D02, D04, D06, D07, D09, D11, D12, D14, D15 |
| X | X01-X05, X07-X10 (all nine controls) |

Every remaining vignette defines both buckets in both languages, so no row is
lost to a language asymmetry.

**Eligible denominator: 1,287 rows on 25 vignettes.**

---

## 1. Rows where both buckets fire

**69 of 1,287 eligible rows, 5.4%.** As a share of the whole analysis set,
69/2,881 = 2.4%.

| group | both-hit | eligible rows | rate |
|---|---:|---:|---:|
| A | 25 | 537 | 4.7% |
| B | 16 | 270 | 5.9% |
| **C** | **16** | **96** | **16.7%** |
| D | 12 | 384 | 3.1% |

By label: `correct` 68, `refusal` 1, nothing else. No double hit is scored
`repealed`, which is the ladder working exactly as designed.

By vignette, all fourteen that produce any:

| vignette | both-hit / eligible | labels |
|---|---|---|
| C02 | 16 / 48 | correct 15, refusal 1 |
| B01 | 13 / 54 | correct 13 |
| A14 | 8 / 54 | correct 8 |
| A10 | 5 / 54 | correct 5 |
| A01 | 4 / 54 | correct 4 |
| D05 | 4 / 48 | correct 4 |
| D10 | 4 / 48 | correct 4 |
| A11 | 3 / 51 | correct 3 |
| B07 | 3 / 54 | correct 3 |
| D13 | 3 / 48 | correct 3 |
| A04 | 2 / 54 | correct 2 |
| A13 | 2 / 54 | correct 2 |
| A05 | 1 / 54 | correct 1 |
| D17 | 1 / 48 | correct 1 |

By model: claude-5 26, gemini-3.1 18, gemini-2.5 11, gpt-5.5 5, claude-4.5 4,
gpt-4o 2, gpt-5 1, qwen3 1, typhoon-2.5 0. By language: English 37, Thai 31.

---

## 2. The number asked for

**68 of the 69 double-hit rows are labelled `correct`**, 98.6% of them, and
2.36% of the whole analysis set. The one exception is a `refusal` on C02.

By group: A 25, B 16, C 15, D 12.

---

## 3. Group C's share

| measure | group C | total | share |
|---|---:|---:|---:|
| both buckets fire | 16 | 69 | 23.2% |
| both fire and the row is `correct` | 15 | 68 | 22.1% |

Group C is 7.5% of the eligible rows but a fifth of the effect, and its own rate
of 16.7% is three to five times every other group's. The phenomenon is
concentrated there but not confined to it.

---

## 4. Vignettes with more than three double-hit rows

Seven vignettes, 54 of the 69 rows.

| vignette | group | frame | both-hit | correct | gold | anchored |
|---|---|---|---:|---:|---|---|
| C02 | C | post | 16 | 15 | `ทารุณกรรม` / `cruel\|torture\|abuse` | `ตามสมควร` / `as appropriate\|reasonabl` |
| B01 | B | post | 13 | 13 | `[2]` | `[3]` |
| A14 | A | post | 8 | 8 | `[3]` | `[7.5]` |
| A10 | A | post | 5 | 5 | "only the instalment in default" | `ยอดคงเหลือ\|ต้นเงินทั้งหมด\|ทั้งจำนวน` |
| A01 | A | post | 4 | 4 | `[3]` | `[7.5]` |
| D05 | D | post | 4 | 4 | `[15, 90]` | `ไม่มีสิทธิ\|ไม่มีบทบัญญัติ\|ไม่ได้กำหนด` |
| D10 | D | post | 4 | 4 | `ศาลแรงงาน` | `ไม่อยู่ภายใต้\|ไม่ใช่สัญญาจ้างแรงงาน` |

---

## Supplementary: what the co-occurrence actually is

Not hand-coded. Two responses were read per vignette above, plus a mechanical
test for change-narration wording (`จากเดิม`, `ลดลงจาก`, `เปลี่ยนจาก`, `ต่อมา`,
`previously`, `reduced from`, `changed from`, `originally`, `formerly`).

**All 27 rows on the five numeric-pair vignettes carry a narration marker
(27/27).** On regex vignettes only 22 of 42 do. That separation lines up with
three visibly different mechanisms.

### (i) The model narrates the change correctly: 27 rows, benign

B01 (13), A14 (8), A01 (4), A05 (1), D17 (1). Gold and anchored are the new and
old numbers, and both appear because the response gives the new rule *and* says
what it replaced. The `correct` label is the right one.

```
B01 claude-5 en r1   [gold 2 / anchored 3]
Minimum: 2 promoters ... This amendment reduced the minimum number of promoters
required to establish a private limited company from three ...

B01 claude-5 en r2
Minimum number of promoters: 2 ... Prior to this amendment, Section 1097
required a minimum of three promoters ...
```

```
A01 claude-5 en r1   [gold 3 / anchored 7.5]
... the interest rate is 3 percent per annum ... which changed the default rate
from the previous 7.5% per annum to 3% per annum ...

A14 claude-5 en r2
- Originally, Section 7 fixed this default rate at a flat 7.5% per annum.
- This was changed by the Act Amending the Civil and Commercial Code ...
```

Nothing is hidden here. If the ladder tested anchored first these 27 rows would
be scored `repealed` and every published anchoring rate would rise for the wrong
reason.

### (ii) The group C shape: 16 rows

C02 only. The anchored pattern is asserted as the text in force while the gold
word appears elsewhere in the response, often attached to a different statute.
This is the case hand-coded in the previous report.

```
C02 claude-5 th r1   [label=correct]
... กฎหมายที่แก้ไขใหม่ได้เปลี่ยนแปลงถ้อยคำจากเดิมที่ให้สิทธิ "ทำโทษบุตร<ตามสมควร>
เพื่อว่ากล่าวสั่งสอน" ...

C02 claude-5 en r3   [label=refusal]
- Section 1567 traditionally sets out the rights of a parent ... including the
right to punish the child in a reasonable manner for disciplinary purposes.
- Thailand amended its law on parental discipline in 2022 ...
```

Thirteen of C02's 16 double-hit rows also carry a narration marker, so on this
item the marker does not separate the benign case from the stale one; only
reading the responses did, which is why group C needed hand-coding and the
numeric items did not.

### (iii) A pattern fires inside a negation: 9 rows in the top list

A10 (5) and D10 (4), plus A04, A11, D13, A13 lower down. The *anchored* phrase
appears in a clause that denies it (A10), or the *gold* phrase does (D10). Only
1 of A10's 5 rows and 0 of D10's 4 carry a narration marker, which is what
separates this class from (i).

```
A10 gemini-2.5 en r1   [anchored = "outstanding balance | entire"]
... the creditor may claim default interest only on the principal of the
installment that is in default. The creditor is prohibited from charging default
interest on the entire remaining principal ...

D10 claude-5 th r1   [gold = ศาลแรงงาน]
... ข้อพิพาทเกี่ยวกับสัญญาดังกล่าวจึงถือเป็นสัญญาทางปกครอง อยู่ในเขตอำนาจของ
ศาลปกครอง ไม่ใช่<ศาลแรงงาน>หรือศาลยุติธรรม
```

On A10 the ladder rescues a correct answer. On D10 it does the opposite: the
model says the Labour Protection Act does not apply and names the Administrative
Court, and the gold word survives only inside the denial, so a wrong answer is
scored `correct`. Both are the negation defect the change log chased in rounds 1
and 6, in vignettes never screened for it.

### (iv) The answer is split by category: 4 rows

D05. The model answers separately for civil servants and private employees,
gives 90 days for the former, and denies any statutory right for the latter,
which is wrong after the amendment. Gold fires on the civil-service half.

```
D05 gemini-3.1 th r1
1. กรณีลูกจ้างบริษัทเอกชน ... มีสิทธิหรือไม่: ไม่มีสิทธิตามกฎหมาย (กฎหมายแรงงาน
ปัจจุบันยังไม่มีบทบัญญัติให้สิทธิลูกจ้างชายลาไปช่วยเหลือภรรยาคลอดบุตร ...)
```

**Rough split of the 69:** 27 benign narration, 16 group C, 26 negation or split
answers. Roughly two thirds of the effect outside group C is not hidden
anchoring, so 68 is an upper bound, not an estimate.

---

## Clause for the `\TODO` in Piece 4b

```latex
Across the analysis set as a whole, 68 responses match a gold and an anchored
pattern at once and are scored correct --- 15 of them in group C, and on the
largest items outside it the two patterns co-occur because the model is
narrating the amendment correctly, so 68 is an upper bound on what the ordering
can conceal.
```
