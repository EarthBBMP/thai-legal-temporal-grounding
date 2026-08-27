"""Dump the complete API response for one model, to diagnose empty answers.

    python src/debug_call.py gpt5

Prints the whole JSON the provider returned. When a model returns an empty
string the reason is almost always visible in `finish_reason` or in the token
usage breakdown, and guessing at it wastes more time than looking.
"""

import json
import os
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from collect import MODELS, SYSTEM_PROMPTS, _post, ApiError  # noqa: E402

name = sys.argv[1] if len(sys.argv) > 1 else "gpt5"
spec = MODELS[name]
key = os.environ[spec["key_env"]]

question = ("ตามประมวลกฎหมายแพ่งและพาณิชย์ มาตรา 7 ปัจจุบันใช้อัตราร้อยละเท่าใดต่อปี "
            "ตอบสั้น ๆ โดยระบุตัวเลข")

variants = [
    ("system role + max_completion_tokens 4000",
     {"model": spec["model"], "max_completion_tokens": 4000,
      "messages": [{"role": "system", "content": SYSTEM_PROMPTS["th"]},
                   {"role": "user", "content": question}]}),
    ("developer role instead of system",
     {"model": spec["model"], "max_completion_tokens": 4000,
      "messages": [{"role": "developer", "content": SYSTEM_PROMPTS["th"]},
                   {"role": "user", "content": question}]}),
    ("no system message at all",
     {"model": spec["model"], "max_completion_tokens": 4000,
      "messages": [{"role": "user", "content": question}]}),
    ("reasoning_effort minimal",
     {"model": spec["model"], "max_completion_tokens": 4000, "reasoning_effort": "minimal",
      "messages": [{"role": "system", "content": SYSTEM_PROMPTS["th"]},
                   {"role": "user", "content": question}]}),
    ("no token cap at all",
     {"model": spec["model"],
      "messages": [{"role": "system", "content": SYSTEM_PROMPTS["th"]},
                   {"role": "user", "content": question}]}),
]

print(f"model: {spec['model']}\n" + "=" * 70)
for label, payload in variants:
    print(f"\n--- {label}")
    try:
        body = _post(f"{spec['base']}/chat/completions", payload,
                     {"Authorization": f"Bearer {key}"}, timeout=180)
    except ApiError as e:
        print(f"    HTTP {e.status}: {' '.join(e.body.split())[:300]}")
        continue
    except Exception as e:  # noqa: BLE001
        print(f"    {type(e).__name__}: {e}")
        continue

    ch = (body.get("choices") or [{}])[0]
    msg = ch.get("message", {})
    content = msg.get("content")
    print(f"    finish_reason : {ch.get('finish_reason')}")
    print(f"    usage         : {json.dumps(body.get('usage', {}), ensure_ascii=False)}")
    print(f"    message keys  : {list(msg.keys())}")
    if content:
        print(f"    CONTENT       : {' '.join(content.split())[:160]}")
        print("    >>> this variant works")
    else:
        print(f"    CONTENT       : {content!r}  <-- empty")
        # Some models put the answer somewhere other than message.content.
        blob = json.dumps(body, ensure_ascii=False)
        if len(blob) < 4000:
            print(f"    full body     : {blob}")
