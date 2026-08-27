"""Check which models your keys can actually reach, before spending anything.

    python src/list_models.py            # list what each key can see
    python src/list_models.py --test     # also make one real call per configured model

Run this before collect.py. A wrong model string is the most common reason for
a 400, and the error text that comes back is usually explicit about it.
"""

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from collect import MODELS, SYSTEM_PROMPTS, call_model, ApiError  # noqa: E402

PROVIDERS = {
    "OPENAI_API_KEY": "https://api.openai.com/v1/models",
    "OPENROUTER_API_KEY": "https://openrouter.ai/api/v1/models",
    "GEMINI_API_KEY": "https://generativelanguage.googleapis.com/v1beta/openai/models",
}


def list_provider(env, url, filter_str=""):
    key = os.environ.get(env)
    if not key:
        print(f"\n{env}: not set")
        return
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"\n{env}: HTTP {e.code} — {e.read().decode('utf-8', 'replace')[:200]}")
        return
    except Exception as e:  # noqa: BLE001
        print(f"\n{env}: {type(e).__name__}: {e}")
        return
    ids = sorted(m.get("id", "?") for m in data.get("data", []))
    if filter_str:
        ids = [i for i in ids if filter_str.lower() in i.lower()]
    print(f"\n{env}: {len(ids)} models")
    for i in ids:
        print("   ", i)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--filter", default="", help="substring filter, e.g. gpt or thai")
    p.add_argument("--test", action="store_true", help="one live call per configured model")
    args = p.parse_args()

    for env, url in PROVIDERS.items():
        list_provider(env, url, args.filter)

    if not args.test:
        print("\nrun with --test to make one real call per model in MODELS")
        return

    print("\n" + "=" * 60)
    print("live test — one short call per model in collect.MODELS")
    print("=" * 60)
    for name, spec in MODELS.items():
        if not os.environ.get(spec["key_env"]):
            print(f"{name:14s} SKIP  {spec['key_env']} not set")
            continue
        try:
            text, version = call_model(
                spec, SYSTEM_PROMPTS["th"],
                "ตามประมวลกฎหมายแพ่งและพาณิชย์ มาตรา 7 ปัจจุบันใช้อัตราร้อยละเท่าใดต่อปี ตอบสั้น ๆ")
            preview = " ".join(text.split())[:70]
            print(f"{name:14s} OK    version={version}")
            print(f"{'':14s}       {preview}")
        except ApiError as e:
            print(f"{name:14s} FAIL  HTTP {e.status}")
            print(f"{'':14s}       {' '.join(e.body.split())[:220]}")
        except Exception as e:  # noqa: BLE001
            print(f"{name:14s} FAIL  {type(e).__name__}: {e}")

    print("\nCopy the version= strings into the paper. That is what the API "
          "actually served, which is not always what you asked for.")


if __name__ == "__main__":
    main()
