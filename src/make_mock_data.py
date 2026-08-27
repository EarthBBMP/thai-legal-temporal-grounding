"""Generate synthetic responses to smoke-test parse.py and analyze.py.

NOT DATA. Random noise with a plausible shape, so you can verify the pipeline
runs before spending money on API calls. Delete raw/ afterwards.

    python src/make_mock_data.py && python src/parse.py && python src/analyze.py
    rm -rf raw/*.json
"""
import json, pathlib, random
ROOT = pathlib.Path(__file__).resolve().parent.parent; RAW = ROOT/'raw'; RAW.mkdir(exist_ok=True)
V = json.load(open(ROOT/'data/vignettes.json', encoding='utf-8'))['vignettes']
random.seed(7)

def render(nums, regexes, lang):
    bits = []
    if nums: bits.append(" และ ".join(f"{n:g}" for n in nums) if lang=='th' else " and ".join(f"{n:g}" for n in nums))
    if regexes: bits.append(regexes[0].split('|')[0].replace('(?<!ไม่)','').replace('(?<!not )','').replace('\\b',''))
    return " ".join(bits) or "ไม่ทราบ"

n=0
for v in V:
    for model, anchor_p in (("gpt",0.15),("claude",0.10),("typhoon",0.55)):
        for lang in ("th","en"):
            for run in (1,2,3):
                r = random.random()
                bump = 0.15 if lang=='th' else 0.0
                if r < anchor_p + bump and (v.get('anchored_numbers') or v.get(f'anchored_regex_{lang}')):
                    txt = render(v.get('anchored_numbers'), v.get(f'anchored_regex_{lang}'), lang)
                elif r < anchor_p + bump and (v.get('over_numbers') or v.get(f'over_regex_{lang}')):
                    txt = render(v.get('over_numbers'), v.get(f'over_regex_{lang}'), lang)
                elif r > 0.95:
                    txt = "ขออภัย ไม่สามารถตอบได้ ควรปรึกษาทนายความ"
                else:
                    txt = render(v.get('gold_numbers'), v.get(f'gold_regex_{lang}'), lang)
                    if random.random()<0.25: txt += " (ไม่แน่ใจ โปรดตรวจสอบ)" if lang=='th' else " (not certain, please verify)"
                f = RAW/f"{v['id']}__{model}__{lang}__baseline__r{run}.json"
                f.write_text(json.dumps({"vignette_id":v['id'],"model":model,"model_version":model+"-mock",
                    "language":lang,"condition":"baseline","run_index":run,"system_prompt":"",
                    "prompt":"","raw_response":txt,"timestamp":"mock"}, ensure_ascii=False), encoding='utf-8')
                n+=1
print("mock responses:", n)
