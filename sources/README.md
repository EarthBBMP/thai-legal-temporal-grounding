# Sources for the statutory text

**Do not use annotated copies.** Files downloaded from some mirrors carry a text
box stamped into the first page that is not part of the Royal Gazette. Download
again from ratchakitcha.soc.go.th directly.

## Instruments

Six instruments fix the gold labels. Four supply the amended rule; two supply
the rule that preceded it, which is needed to tell anchoring apart from any
other kind of wrong answer. Citations here match the paper's Table 1 and
bibliography exactly.

| File | Instrument | Gazette | Published | Retrieved |
|---|---|---|---|---|
| `A_interest_138-26A_2564.pdf` | Emergency Decree Amending the Civil and Commercial Code, B.E. 2564 | vol. 138, pt. 26a, p. 1 | 10 Apr 2021 | 2026-08-27 |
| `B_company_139-69A_2565.pdf` | Act Amending the Civil and Commercial Code (No. 23), B.E. 2565 | vol. 139, pt. 69a, p. 1 | 8 Nov 2022 | 2026-08-27 |
| `C_child_142-14A_2568.pdf` | Act Amending the Civil and Commercial Code (No. 25), B.E. 2568 | vol. 142, pt. 14a, p. 1 | 24 Mar 2025 | 2026-08-27 |
| `D_labour9_142-74A_2568.pdf` | Labour Protection Act (No. 9), B.E. 2568 | vol. 142, pt. 74a, p. 41 | 7 Nov 2025 | 2026-08-27 |
| `D_labour7_136-43A_2562.pdf` | Labour Protection Act (No. 7), B.E. 2562 | vol. 136, pt. 43a, p. 21 | 5 Apr 2019 | 2026-08-27 |
| `D_labour_115-8A_2541.pdf` | Labour Protection Act, B.E. 2541 | vol. 115, pt. 8a, p. 1 | 20 Feb 1998 | 2026-08-27 |

The last two matter for group D specifically. Maternity leave has been set three
times — 90 days under the 2541 Act, 98 under No. 7, and 120 under No. 9 — so a
model can be anchored one amendment back or two, and both prior instruments are
needed to tell which.

All six were retrieved on 27 August 2026, and every gold label in
`data/law_facts.csv` was checked against them on that date. The paper measures
correctness as of a point in time, so this date is part of the methodology, not
housekeeping: it is the date on which the gold answers were fixed against the
law.

## statute_texts/

**This directory is empty, deliberately.** It was intended to hold the current
text of each cited section, one file per section, for the retrieval-augmented
condition. That condition is described in the paper as future work and was not
run, so the section texts were never extracted. The convention below is recorded
for whoever runs it next.

Source the text from the consolidated Civil and Commercial Code published by the
Office of Legal Affairs, Court of Justice (jla.coj.go.th), as amended through Act
No. 25, B.E. 2568, and the consolidated Labour Protection Act as amended through
Act No. 9, B.E. 2568.

File names must match the values in the `sections` field of `vignettes.json`,
with spaces replaced by `_`, dots dropped, and `/` replaced by `-`:

    "ปพพ ม.7"      -> ปพพ_ม7.txt
    "ปพพ ม.224/1"  -> ปพพ_ม224-1.txt
    "คร ม.41"      -> คร_ม41.txt

Twenty-seven files are required. Check the set with:

    python src/check_statutes.py

If a file is missing, `collect.py` falls back to the unaugmented prompt for that
vignette and prints a warning. Running the mitigation condition against an
incomplete set silently measures the baseline instead, so check before running.
