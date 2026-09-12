"""Script A: calls the models and writes raw responses to disk.

Collection only, no parsing or scoring, so a rubric bug costs a re-run of the
parser instead of 2,880 API calls. Resumable: one file per call, existing files
are skipped, so interrupt it freely.

    python src/collect.py --models gpt,claude --condition baseline --limit 20
    python src/collect.py --all
"""

import argparse
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
STATUTES = ROOT / "sources" / "statute_texts"

SYSTEM_PROMPTS = {
    "th": ("คุณกำลังช่วยตอบคำถามเชิงข้อมูลเกี่ยวกับกฎหมายไทย "
           "ให้ระบุบทบัญญัติที่ใช้บังคับและสาระสำคัญของบทบัญญัตินั้น ตอบเป็นภาษาไทย"),
    "en": ("You are assisting with a factual question about Thai law. "
           "State which provision applies and what it requires. Answer in English."),
}

# Edit to match what you actually have keys for. `api` selects the wire format.
# MODELS = {
#     "gpt":        {"api": "openai",    "model": "gpt-5",                    "base": "https://api.openai.com/v1",       "key_env": "OPENAI_API_KEY"},
#     "claude":     {"api": "anthropic", "model": "claude-sonnet-4-6",        "base": "https://api.anthropic.com/v1",    "key_env": "ANTHROPIC_API_KEY"},
#     "gemini":     {"api": "openai",    "model": "gemini-2.5-pro",           "base": "https://generativelanguage.googleapis.com/v1beta/openai", "key_env": "GEMINI_API_KEY"},
#     "typhoon":    {"api": "openai",    "model": "scb10x/llama3.1-typhoon2-70b-instruct", "base": "https://openrouter.ai/api/v1", "key_env": "OPENROUTER_API_KEY"},
#     "openthaigpt":{"api": "openai",    "model": "openthaigpt/openthaigpt-1.5-72b-instruct", "base": "https://openrouter.ai/api/v1", "key_env": "OPENROUTER_API_KEY"},
#     "qwen":       {"api": "openai",    "model": "qwen/qwen-2.5-72b-instruct", "base": "https://openrouter.ai/api/v1",  "key_env": "OPENROUTER_API_KEY"},
# }
MODELS = {
    # --- OpenAI โดยตรง ---
    "gpt4o":    {"api": "openai", "model": "gpt-4o-2024-11-20",
                 "base": "https://api.openai.com/v1", "key_env": "OPENAI_API_KEY",
                 "params": {"temperature": 0, "max_tokens": 1000}},
    "gpt5":     {"api": "openai", "model": "gpt-5-2025-08-07",
                 "base": "https://api.openai.com/v1", "key_env": "OPENAI_API_KEY",
                 "params": {"max_completion_tokens": 4000}},
    "gpt55": {"api": "openai", "model": "gpt-5.5-2026-04-23",
          "base": "https://api.openai.com/v1", "key_env": "OPENAI_API_KEY",
          "params": {"max_completion_tokens": 8000}},

    # --- ผ่าน OpenRouter, คู่เก่า-ใหม่ คร่อม ธ.ค. 2568 ---
    "claude45": {"api": "openai", "model": "anthropic/claude-sonnet-4.5",
                 "base": "https://openrouter.ai/api/v1", "key_env": "OPENROUTER_API_KEY",
                 "params": {"temperature": 0, "max_tokens": 1000}},
    "claude5":  {"api": "openai", "model": "anthropic/claude-sonnet-5",
                 "base": "https://openrouter.ai/api/v1", "key_env": "OPENROUTER_API_KEY",
                 "params": {"temperature": 0, "max_tokens": 4000}},
    "gemini25": {"api": "openai", "model": "google/gemini-2.5-pro",
                 "base": "https://openrouter.ai/api/v1", "key_env": "OPENROUTER_API_KEY",
                 "params": {"temperature": 0, "max_tokens": 4000}},
    "gemini31": {"api": "openai", "model": "google/gemini-3.1-pro-preview",
                 "base": "https://openrouter.ai/api/v1", "key_env": "OPENROUTER_API_KEY",
                 "params": {"temperature": 0, "max_tokens": 4000}},
    "qwen3":    {"api": "openai", "model": "qwen/qwen3-235b-a22b-2507",
                 "base": "https://openrouter.ai/api/v1", "key_env": "OPENROUTER_API_KEY",
                 "params": {"temperature": 0, "max_tokens": 1000}},
    "qwen35":  {"api": "openai", "model": "qwen/qwen3.5-27b",
            "base": "https://openrouter.ai/api/v1", "key_env": "OPENROUTER_API_KEY",
            "params": {"temperature": 0, "max_tokens": 1000}},

    "typhoon21": {"api": "openai", "model": "typhoon-v2.1-12b-instruct",
              "base": "https://api.opentyphoon.ai/v1", "key_env": "TYPHOON_API_KEY",
              "params": {"temperature": 0, "max_tokens": 2000}},
    "typhoon25": {"api": "openai", "model": "typhoon-v2.5-30b-a3b-instruct",
              "base": "https://api.opentyphoon.ai/v1", "key_env": "TYPHOON_API_KEY",
              "params": {"temperature": 0, "max_tokens": 2000}},
}


class ApiError(Exception):
    """Carries the provider's actual error message, not just the HTTP code."""

    def __init__(self, status, body):
        self.status, self.body = status, body
        super().__init__(f"HTTP {status}: {body[:400]}")


def _post(url, payload, headers, timeout=300):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        # Keep the body, or every failure just reads "400 Bad Request".
        raise ApiError(e.code, e.read().decode("utf-8", "replace")) from None


def call_model(spec, system, user):
    """Returns (text, version_string). Raises on transport failure."""
    key = os.environ.get(spec["key_env"])
    if not key:
        raise RuntimeError(f"missing env var {spec['key_env']}")

    if spec["api"] == "anthropic":
        body = _post(f"{spec['base']}/messages",
                     {"model": spec["model"], "max_tokens": 1000, "temperature": 0,
                      "system": system, "messages": [{"role": "user", "content": user}]},
                     {"x-api-key": key, "anthropic-version": "2023-06-01"})
        text = "".join(b.get("text", "") for b in body.get("content", [])
                       if b.get("type") == "text")
        return text, body.get("model", spec["model"])

    msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    payload = {"model": spec["model"], "messages": msgs,
           **spec.get("params", {"temperature": 0, "max_tokens": 1000})}

    # Newer reasoning models reject max_tokens/temperature, so drop and retry.
    for _ in range(3):
        try:
            body = _post(f"{spec['base']}/chat/completions", payload,
                         {"Authorization": f"Bearer {key}"})
            break
        except ApiError as e:
            if e.status != 400:
                raise
            low = e.body.lower()
            if "max_tokens" in low and "max_tokens" in payload:
                payload["max_completion_tokens"] = payload.pop("max_tokens")
            elif "temperature" in low and "temperature" in payload:
                payload.pop("temperature")
            else:
                raise
    else:
        raise ApiError(400, "could not find an accepted parameter combination")

    return body["choices"][0]["message"]["content"], body.get("model", spec["model"])


def load_statutes(sections):
    """Current statute text for the mitigation condition."""
    parts = []
    for s in sections or []:
        f = STATUTES / (s.replace(" ", "_").replace(".", "").replace("/", "-") + ".txt")
        if f.exists():
            parts.append(f.read_text(encoding="utf-8").strip())
        else:
            print(f"  ! missing statute text: {f.name}", file=sys.stderr)
    return parts


def build_prompt(v, lang, condition):
    text = v["text_th"] if lang == "th" else v["text_en"]
    if condition == "baseline":
        return text
    statutes = load_statutes(v.get("sections"))
    if not statutes:
        return text
    header = ("ตัวบทที่เกี่ยวข้องซึ่งใช้บังคับอยู่ในปัจจุบัน:" if lang == "th"
              else "Relevant provisions currently in force:")
    return f"{header}\n\n" + "\n\n".join(statutes) + "\n\n---\n\n" + text


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--models", default="", help="comma separated keys from MODELS")
    p.add_argument("--languages", default="th,en")
    p.add_argument("--condition", default="baseline", choices=["baseline", "mitigation"])
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--limit", type=int, default=0, help="first N vignettes only (pilot)")
    p.add_argument("--ids", default="", help="comma separated vignette ids only")
    p.add_argument("--all", action="store_true", help="every model in MODELS")
    p.add_argument("--sleep", type=float, default=0.4)
    args = p.parse_args()

    models = list(MODELS) if args.all else [m for m in args.models.split(",") if m]
    if not models:
        p.error("give --models or --all")
    unknown = [m for m in models if m not in MODELS]
    if unknown:
        p.error(f"unknown models: {unknown}")

    vignettes = json.load(open(ROOT / "data" / "vignettes.json", encoding="utf-8"))["vignettes"]
    if args.ids:
        want = set(args.ids.split(","))
        vignettes = [v for v in vignettes if v["id"] in want]
    if args.limit:
        vignettes = vignettes[:args.limit]

    runs = 1 if args.condition == "mitigation" else args.runs
    langs = args.languages.split(",")
    total = len(vignettes) * len(langs) * len(models) * runs
    print(f"{total} calls · {len(vignettes)} vignettes × {len(langs)} lang "
          f"× {len(models)} models × {runs} runs · condition={args.condition}")

    done = failed = skipped = 0
    for mkey in models:
        spec = MODELS[mkey]
        for v in vignettes:
            for lang in langs:
                for run in range(1, runs + 1):
                    out = RAW / f"{v['id']}__{mkey}__{lang}__{args.condition}__r{run}.json"
                    stem = f"__{mkey}__{lang}__{args.condition}__r{run}.json"
                    # Don't re-buy answers already collected under an old id.
                    if out.exists() or any((RAW / (old + stem)).exists()
                                           for old in v.get("legacy_ids", [])):
                        skipped += 1
                        continue
                    out.parent.mkdir(parents=True, exist_ok=True)
                    system = SYSTEM_PROMPTS[lang]
                    user = build_prompt(v, lang, args.condition)
                    try:
                        text, version = call_model(spec, system, user)
                    except Exception as e:  # noqa: BLE001 - log and continue
                        failed += 1
                        print(f"  FAIL {out.stem}: {type(e).__name__}: {e}", file=sys.stderr)
                        time.sleep(2)
                        continue
                    out.write_text(json.dumps({
                        "vignette_id": v["id"], "model": mkey, "model_version": version,
                        "language": lang, "condition": args.condition, "run_index": run,
                        "system_prompt": system, "prompt": user, "raw_response": text,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    }, ensure_ascii=False, indent=1), encoding="utf-8")
                    done += 1
                    if done % 25 == 0:
                        print(f"  {done} written, {skipped} skipped, {failed} failed")
                    time.sleep(args.sleep)

    print(f"done: {done} written · {skipped} already present · {failed} failed")
    if failed:
        print("re-run the same command to retry only the failures")


if __name__ == "__main__":
    main()
