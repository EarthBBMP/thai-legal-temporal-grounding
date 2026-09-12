"""Analysis: metrics, Wilson intervals and the poster figure.

    python src/analyze.py

Writes out/metrics.csv, out/summary.txt and out/figure_rscr.png.

Headline metric is RSCR (repealed-statute citation rate): the share of scorable
post-frame responses labelled `repealed`, per model per language. Every
proportion carries a Wilson 95% interval, which holds up at small n and near
0 or 1 where the normal approximation does not.
"""

import csv
import json
import math
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "out"


def wilson(k, n, z=1.96):
    """95% CI for a proportion. Returns (point, low, high)."""
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    # Clamp so the interval contains the point estimate; at k=0 it lands on
    # 6.9e-18 and matplotlib rejects the negative error bar.
    return (p,
            min(p, max(0.0, centre - half)),
            max(p, min(1.0, centre + half)))


def fmt(k, n):
    p, lo, hi = wilson(k, n)
    if n == 0:
        return "n/a"
    return f"{p:.1%} [{lo:.1%}–{hi:.1%}] ({k}/{n})"


def load():
    f = OUT / "labelled.csv"
    if not f.exists():
        raise SystemExit(f"{f} not found — run parse.py first")
    with f.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def excluded_vignettes():
    """Vignettes flagged `excluded_from_analysis`, as {id: reason}.

    Dropped from every metric, still kept in labelled.csv.
    """
    out = {}
    with (ROOT / "data" / "vignettes.json").open(encoding="utf-8") as fh:
        for v in json.load(fh)["vignettes"]:
            if v.get("excluded_from_analysis"):
                reason = v.get("exclusion_reason", "no reason recorded")
                for vid in [v["id"]] + list(v.get("legacy_ids", [])):
                    out[vid] = reason
    return out


SCORABLE = {"correct", "repealed", "over_applied", "wrong_other"}


def rate(rows, numerator_labels, denom=SCORABLE):
    d = [r for r in rows if r["label"] in denom]
    k = sum(1 for r in d if r["label"] in numerator_labels)
    return k, len(d)


def main():
    rows = load()
    OUT.mkdir(exist_ok=True)
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    # Everything below reads `rows`, so dropping them here covers every metric.
    dropped = excluded_vignettes()
    excluded_rows = [r for r in rows if r["vignette_id"] in dropped]
    rows = [r for r in rows if r["vignette_id"] not in dropped]

    base = [r for r in rows if r["condition"] == "baseline"]
    mitig = [r for r in rows if r["condition"] == "mitigation"]
    models = sorted({r["model"] for r in rows})

    say("=" * 74)
    say("TEMPORAL LEGAL GROUNDING — RESULTS")
    say("=" * 74)
    say(f"{len(rows)} responses · {len(base)} baseline · {len(mitig)} mitigation")
    say(f"models: {', '.join(models)}")
    if excluded_rows:
        seen = sorted({r["vignette_id"] for r in excluded_rows})
        say(f"excluded from all metrics: {', '.join(seen)} "
            f"({len(excluded_rows)} responses, still present in labelled.csv)")
        for vid in seen:
            say(f"  {vid}: {dropped[vid]}")
    say()

    # --- headline: RSCR on post-frame items -------------------------------
    say("RSCR — repealed-statute citation rate, post-frame items, baseline")
    say(f"{'model':<14}{'Thai':<30}{'English':<30}")
    metrics = []
    for m in models:
        cells = []
        for lang in ("th", "en"):
            sub = [r for r in base if r["model"] == m and r["language"] == lang
                   and r["frame"] == "post"]
            k, n = rate(sub, {"repealed"})
            cells.append(fmt(k, n))
            p, lo, hi = wilson(k, n)
            metrics.append({"metric": "RSCR", "model": m, "language": lang,
                            "k": k, "n": n, "point": p, "low": lo, "high": hi})
        say(f"{m:<14}{cells[0]:<30}{cells[1]:<30}")
    say()

    # --- control check ----------------------------------------------------
    say("CONTROL accuracy — rules that never changed (groups X, and A15/A16,")
    say("B11/B12, C06). If this is high while RSCR is also high, the failure is")
    say("specific to amended provisions, not general ignorance of Thai law.")
    say(f"{'model':<14}{'Thai':<30}{'English':<30}")
    for m in models:
        cells = []
        for lang in ("th", "en"):
            sub = [r for r in base if r["model"] == m and r["language"] == lang
                   and r["type"] == "control"]
            k, n = rate(sub, {"correct"})
            cells.append(fmt(k, n))
            p, lo, hi = wilson(k, n)
            metrics.append({"metric": "control_accuracy", "model": m, "language": lang,
                            "k": k, "n": n, "point": p, "low": lo, "high": hi})
        say(f"{m:<14}{cells[0]:<30}{cells[1]:<30}")
    say()

    # --- over-application -------------------------------------------------
    say("OVER-APPLIED — current rule used for facts predating the amendment")
    say("(pre-frame items). A distinct failure from anchoring; report separately.")
    for m in models:
        cells = []
        for lang in ("th", "en"):
            sub = [r for r in base if r["model"] == m and r["language"] == lang
                   and r["frame"] == "pre"]
            k, n = rate(sub, {"over_applied"})
            cells.append(fmt(k, n))
        say(f"{m:<14}{cells[0]:<30}{cells[1]:<30}")
    say()

    # --- decay with amendment age ----------------------------------------
    say("RSCR BY AMENDMENT AGE — does anchoring fade as an amendment ages?")
    ages = [("A", "ดอกเบี้ย", "5 yr 4 mo"), ("B", "บริษัท", "3 yr 6 mo"),
            ("C", "ทำโทษบุตร", "17 mo"), ("D", "แรงงาน", "8 mo")]
    say(f"{'group':<8}{'topic':<14}{'age':<12}{'Thai':<26}{'English':<26}")
    for g, topic, age in ages:
        cells = []
        for lang in ("th", "en"):
            sub = [r for r in base if r["group"] == g and r["language"] == lang
                   and r["frame"] == "post"]
            k, n = rate(sub, {"repealed"})
            cells.append(fmt(k, n))
            p, lo, hi = wilson(k, n)
            metrics.append({"metric": "RSCR_by_group", "model": g, "language": lang,
                            "k": k, "n": n, "point": p, "low": lo, "high": hi})
        say(f"{g:<8}{topic:<14}{age:<12}{cells[0]:<26}{cells[1]:<26}")
    say()

    # --- knowledge vs application ----------------------------------------
    say("KNOWLEDGE vs APPLICATION — a model that can state the rule but not")
    say("apply it is the interesting case.")
    for t in ("knowledge", "application"):
        cells = []
        for lang in ("th", "en"):
            sub = [r for r in base if r["type"] == t and r["language"] == lang
                   and r["frame"] == "post"]
            k, n = rate(sub, {"repealed"})
            cells.append(fmt(k, n))
        say(f"{t:<14}{cells[0]:<30}{cells[1]:<30}")
    say()

    # --- mitigation -------------------------------------------------------
    if mitig:
        say("MITIGATION — current statute text pasted into context")
        for m in models:
            b = [r for r in base if r["model"] == m and r["frame"] == "post"]
            g = [r for r in mitig if r["model"] == m and r["frame"] == "post"]
            kb, nb = rate(b, {"repealed"})
            kg, ng = rate(g, {"repealed"})
            pb = kb / nb if nb else float("nan")
            pg = kg / ng if ng else float("nan")
            closed = (1 - pg / pb) if (nb and ng and pb > 0) else float("nan")
            say(f"{m:<14}baseline {fmt(kb, nb):<26} → mitigated {fmt(kg, ng):<26}"
                f" gap closed {closed:.0%}" if closed == closed else
                f"{m:<14}baseline {fmt(kb, nb)} → mitigated {fmt(kg, ng)}")
        say()

    # --- hedging ----------------------------------------------------------
    wrong = [r for r in base if r["label"] in {"repealed", "over_applied", "wrong_other"}]
    k = sum(1 for r in wrong if r["hedged"] == "0")
    say("CONFIDENCE — share of WRONG answers with no expression of uncertainty")
    say(f"  {fmt(k, len(wrong))}")
    echo = [r for r in base if r["group"] == "C"]
    ke = sum(1 for r in echo if r["echo_repealed_wording"] == "1")
    say(f"  group C responses quoting the deleted wording 'ตามสมควร': {fmt(ke, len(echo))}")
    say()

    # --- hygiene ----------------------------------------------------------
    nondet = defaultdict(set)
    for r in base:
        nondet[(r["vignette_id"], r["model"], r["language"])].add(r["label"])
    unstable = sum(1 for v in nondet.values() if len(v) > 1)
    say(f"HYGIENE  non-deterministic cells at temperature 0: {unstable}/{len(nondet)}")
    say(f"         refusals: {sum(1 for r in rows if r['label'] == 'refusal')}")
    say(f"         ambiguous: {sum(1 for r in rows if r['label'] == 'ambiguous')}")
    say(f"         empty (no text returned, excluded from SCORABLE): "
        f"{sum(1 for r in rows if r['label'] == 'empty')}")
    if any("denies_provision" in r for r in rows):
        # Denying a provision is right pre-frame, a factual error post-frame.
        post = [r for r in rows if r.get("denies_provision") == "1"
                and r["frame"] == "post"]
        pre = [r for r in rows if r.get("denies_provision") == "1"
               and r["frame"] == "pre"]
        say(f"         denies the provision exists: {len(post)} post-frame "
            f"(a factual error), {len(pre)} pre-frame (often the correct answer)")
        by_model = defaultdict(int)
        for r in post:
            by_model[r["model"]] += 1
        if by_model:
            worst = ", ".join(f"{m} {n}" for m, n in
                              sorted(by_model.items(), key=lambda kv: -kv[1]))
            say(f"           post-frame denials by model: {worst}")
    for g in ("A", "B", "C", "D", "X"):
        sub = [r for r in rows if r["group"] == g]
        if sub:
            ref = sum(1 for r in sub if r["label"] == "refusal") / len(sub)
            flag = "  <-- check system prompt" if ref > 0.20 else ""
            say(f"         refusal rate group {g}: {ref:.1%}{flag}")

    (OUT / "summary.txt").write_text("\n".join(lines), encoding="utf-8")
    with (OUT / "metrics.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(metrics[0]))
        w.writeheader()
        w.writerows(metrics)
    print(f"\nwrote {OUT/'summary.txt'} and {OUT/'metrics.csv'}")

    # --- figure -----------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        d = [m for m in metrics if m["metric"] == "RSCR"]
        if d and any(m["n"] for m in d):
            th = [m for m in d if m["language"] == "th"]
            en = [m for m in d if m["language"] == "en"]
            x = np.arange(len(th))
            fig, ax = plt.subplots(figsize=(9, 4.5))
            for off, series, label in ((-0.2, th, "Thai prompt"), (0.2, en, "English prompt")):
                vals = [m["point"] for m in series]
                err = [[m["point"] - m["low"] for m in series],
                       [m["high"] - m["point"] for m in series]]
                ax.bar(x + off, vals, 0.4, label=label, yerr=err, capsize=3)
            ax.set_xticks(x)
            ax.set_xticklabels([m["model"] for m in th], rotation=15, ha="right")
            ax.set_ylabel("Repealed-statute citation rate")
            ax.set_title("Anchoring to repealed Thai law, by model and prompt language")
            ax.legend()
            ax.grid(axis="y", alpha=0.3)
            fig.tight_layout()
            fig.savefig(OUT / "figure_rscr.png", dpi=200)
            print(f"wrote {OUT/'figure_rscr.png'}")
    except ImportError:
        print("matplotlib not installed — skipping figure "
              "(pip install matplotlib numpy)")


if __name__ == "__main__":
    main()
