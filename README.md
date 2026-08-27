# Temporal grounding in Thai statutory law

Thai law changed underneath the models. Between 2021 and 2025 four amendments
rewrote provisions that any Thai legal assistant would be asked about — the
statutory interest rate, the minimum number of company promoters, the limits on
parental discipline, and maternity leave. This repository asks nine language
models 60 vignettes about those provisions, in Thai and in English, and scores
whether each answer reflects the rule in force on the date the question names.
The headline measure is RSCR, the rate at which a model states the superseded
rule when asked about the current one. Vignettes come in pre/post pairs so that
anchoring to an old rule can be told apart from applying a new rule
retroactively, and a control group of unamended provisions separates temporal
error from ordinary error.

## The four amendments

| Group | Provision | Change | Gazette | In force |
|---|---|---|---|---|
| A | CCC s.7, s.224, s.224/1 | Statutory interest 7.5% → 3%; default interest → s.7 rate + 2% = 5%; new s.224/1 limits default interest on instalment debt | 138/26ก/1 | 2021-04-11 |
| B | CCC s.1097, s.1201, s.1162/1, s.1099, s.1238 | Promoters ≥3 → ≥2; dividend payable within one month; board meetings by electronic means; merger may leave one company surviving | 139/69ก/1 | 2023-02-07 |
| C | CCC s.1567(2) | Parental punishment "as is reasonable" replaced by discipline **or behaviour modification**, with cruelty expressly excluded | 142/14ก/1 | 2025-03-25 |
| D | LPA s.41, s.59, s.41/1, s.59/1, s.59/2, s.4/1 | Maternity leave 98 → 120 days; paid days 45 → 60; new childcare and spousal leave | 142/74ก/41 | 2025-12-07 |

Group D reaches back one amendment further: LPA s.41 ran 90 days before Act
No. 7 B.E. 2562 (136/43ก/21, in force 2019-05-05) raised it to 98, so a model can
be one amendment behind or two. The `anchor_depth` column in `out/labelled.csv`
records which.

Group X holds unamended provisions as controls. `sources/README.md` lists the
gazette citation for every instrument; the PDFs are not redistributed here.

## Running it

Collection costs money and is resumable — one file per call, existing files are
skipped, so an interrupted run picks up where it stopped. Parsing and analysis
are free and can be re-run over the saved JSON as often as the rubric changes.

    export OPENAI_API_KEY=... OPENROUTER_API_KEY=... TYPHOON_API_KEY=...
    python src/collect.py --all              # writes raw/*.json
    python src/parse.py                      # writes out/labelled.csv
    python src/analyze.py                    # writes out/summary.txt, metrics.csv, figure_rscr.png

`src/anonymise_timestamps.py` reduces the collection timestamps in `raw/*.json`
to a UTC date; it has already been run over the data here.

On a console that is not UTF-8, prefix the analysis step with
`PYTHONIOENCODING=utf-8`.

## Excluded vignettes

Three vignettes are kept in `out/labelled.csv` but dropped from every metric,
because their gold answer can be reached without knowing the Thai provision and
so they measure general knowledge rather than temporal grounding:

- **A09** — the prompt states that instalment 5 alone is unpaid and names no
  acceleration clause, so "interest runs on the 10,000 baht in arrears" follows
  from ordinary contract principles and the arithmetic in the question.
- **B10** — "two forms of merger" is standard M&A knowledge; answers describing
  one company absorbing another are s.1238(2) in different words, and no pattern
  strict enough to reject the wrong answers keeps the right ones.
- **C01** — striking a child hard enough to bruise falls outside parental
  authority under the repealed wording as much as the current one, so the item
  cannot separate the two eras. Two responses quote the deleted phrase verbatim
  and still score correct.

`src/analyze.py` prints the exclusions and their reasons into `out/summary.txt`,
so any table generated from these numbers carries its own denominator.

## Layout

    data/vignettes.json      60 vignettes with the matching rules for each label
    data/law_facts.csv       one row per amended provision: old rule, new rule, gazette
    sources/                 gazette citations, and current statute text for the
                             mitigation condition
    src/                     collect → parse → analyze, plus helpers
    raw/                     one JSON file per model call
    out/                     labelled.csv, metrics.csv, summary.txt, the figure
    docs/rubric_changes.md   every change to the grading rubric, with evidence

## Grading

Labels are `correct`, `repealed`, `over_applied`, `wrong_other`, `refusal`,
`ambiguous` and `empty`, assigned by pattern matching in `src/parse.py` against
rules stored per vignette. The rubric went through seven rounds of correction,
all of them driven by reading raw responses rather than by looking at aggregate
numbers. [`docs/rubric_changes.md`](docs/rubric_changes.md) records what changed,
why, which rows moved, and a closing section of known limitations that were left
alone. A manual review of the three vignettes flagged `manual_review` put
agreement between the automatic label and a human reading at 87.2% (136/156).
