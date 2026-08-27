"""List which statute-text files the mitigation condition still needs."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
v = json.load(open(ROOT/'data/vignettes.json', encoding='utf-8'))['vignettes']
need = sorted({s for x in v for s in x.get('sections', [])})
missing = 0
for s in need:
    f = ROOT/'sources/statute_texts'/(s.replace(' ','_').replace('.','').replace('/','-')+'.txt')
    ok = f.exists()
    missing += not ok
    print(('OK   ' if ok else 'MISS '), s, '->', f.name)
print(f"\n{len(need)-missing}/{len(need)} present")
if missing:
    print("mitigation condition will silently fall back to baseline for the missing ones")
