# Paper tables

Generated 2026-08-28 from `out/metrics.csv` (produced by `src/analyze.py` over `out/labelled.csv`, 3,036 responses).

A09, B10 and C01 are excluded from every metric; their exclusion reasons are recorded in `data/vignettes.json` and echoed into `out/summary.txt`.

All intervals are 95% Wilson score intervals. `k/n` is successes over the scorable denominator.

`gpt5` was collected only partially (156 responses against roughly 360 for the other models), so its denominators are much smaller and its intervals correspondingly wide; it is absent from D16 entirely.


## Table 1: Control accuracy, descending

Control items test rules that did not change. One row per model and language, sorted by point estimate.


| Rank | Model | Language | Accuracy | 95% CI | k/n |
|---:|---|---|---:|---|---:|
| 1 | gpt55 | th | 100.0% | [91.6-100.0] | 42/42 |
| 2 | gpt55 | en | 100.0% | [91.6-100.0] | 42/42 |
| 3 | gemini31 | th | 100.0% | [91.6-100.0] | 42/42 |
| 4 | gemini25 | th | 100.0% | [91.6-100.0] | 42/42 |
| 5 | gemini31 | en | 95.2% | [84.2-98.7] | 40/42 |
| 6 | claude5 | th | 95.2% | [84.2-98.7] | 40/42 |
| 7 | claude5 | en | 92.9% | [81.0-97.5] | 39/42 |
| 8 | gemini25 | en | 92.7% | [80.6-97.5] | 38/41 |
| 9 | claude45 | th | 92.5% | [80.1-97.4] | 37/40 |
| 10 | gpt4o | en | 90.5% | [77.9-96.2] | 38/42 |
| 11 | gpt5 | en | 88.9% | [56.5-98.0] | 8/9 |
| 12 | gpt5 | th | 85.7% | [48.7-97.4] | 6/7 |
| 13 | claude45 | en | 85.7% | [72.2-93.3] | 36/42 |
| 14 | gpt4o | th | 75.6% | [60.7-86.2] | 31/41 |
| 15 | qwen3 | th | 65.9% | [50.5-78.4] | 27/41 |
| 16 | qwen3 | en | 64.3% | [49.2-77.0] | 27/42 |
| 17 | typhoon25 | th | 40.5% | [26.3-56.5] | 15/37 |
| 18 | typhoon25 | en | 31.0% | [19.1-46.0] | 13/42 |

## Table 2: RSCR (repealed-statute citation rate), post-frame baseline items


| Model | Thai | English |
|---|---|---|
| claude45 | 17.3% [10.4-27.4] (13/75) | 40.0% [29.7-51.3] (30/75) |
| claude5 | 10.3% [5.3-19.0] (8/78) | 13.9% [8.0-23.2] (11/79) |
| gemini25 | 20.8% [13.2-31.1] (16/77) | 13.3% [7.4-22.8] (10/75) |
| gemini31 | 17.1% [10.3-27.1] (13/76) | 14.8% [8.7-24.1] (12/81) |
| gpt4o | 26.8% [17.9-38.1] (19/71) | 23.1% [15.1-33.6] (18/78) |
| gpt5 | 4.9% [1.3-16.1] (2/41) | 0.0% [0.0-8.8] (0/40) |
| gpt55 | 7.6% [3.5-15.6] (6/79) | 14.8% [8.7-24.1] (12/81) |
| qwen3 | 30.7% [21.4-41.8] (23/75) | 40.8% [30.4-52.0] (31/76) |
| typhoon25 | 21.8% [14.1-32.2] (17/78) | 27.0% [18.2-38.1] (20/74) |

## Table 3: Old/new model pairs, RSCR

Difference is new minus old in percentage points; a negative value means the newer model cited the repealed rule less often. No significance test is applied; the two intervals are given so overlap can be judged directly.


| Pair | Language | Older model | Newer model | Difference (pp) |
|---|---|---|---|---:|
| gpt4o to gpt55 | th | 26.8% [17.9-38.1] (19/71) | 7.6% [3.5-15.6] (6/79) | -19.2 |
| gpt4o to gpt55 | en | 23.1% [15.1-33.6] (18/78) | 14.8% [8.7-24.1] (12/81) | -8.3 |
| claude45 to claude5 | th | 17.3% [10.4-27.4] (13/75) | 10.3% [5.3-19.0] (8/78) | -7.1 |
| claude45 to claude5 | en | 40.0% [29.7-51.3] (30/75) | 13.9% [8.0-23.2] (11/79) | -26.1 |
| gemini25 to gemini31 | th | 20.8% [13.2-31.1] (16/77) | 17.1% [10.3-27.1] (13/76) | -3.7 |
| gemini25 to gemini31 | en | 13.3% [7.4-22.8] (10/75) | 14.8% [8.7-24.1] (12/81) | +1.5 |

## Table 4: Manual review of the three flagged items

Every response to A08, B04 and D16 was read and the automatic label judged against the item's criterion. A08 must split 7.5% before 11 April 2021 from 5% on and after; B04 must rule the December 2022 application impermissible and the March 2023 one permissible; D16 must give 98/45 days for the October 2025 birth and 120/60 for the May 2026 birth.


| Item | n | Label agrees | Disagrees | Agreement | 95% CI |
|---|---:|---:|---:|---:|---|
| A08 | 54 | 49 | 5 | 90.7% | [80.1-96.0] |
| B04 | 54 | 39 | 15 | 72.2% | [59.1-82.4] |
| D16 | 48 | 48 | 0 | 100.0% | [92.6-100.0] |
| **All three** | **156** | **136** | **20** | **87.2%** | **[81.0-91.5]** |

| Disagreement type | n | Share of 156 | 95% CI |
|---|---:|---:|---|
| False `correct`: label says correct, response is wrong | 11 | 7.1% | [4.0-12.2] |
| Wrong error type: label names the wrong failure | 1 | 0.6% | [0.1-3.5] |
| Under-classified `ambiguous`: response is wrong but unlabelled | 8 | 5.1% | [2.6-9.8] |

Counting only positive mislabels (that is, treating a conservative `ambiguous` on a wrong response as acceptable): **92.3% [87.0-95.5] (144/156)**.