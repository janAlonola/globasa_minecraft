#!/usr/bin/env python3
import json
from pathlib import Path

# Edit these paths if your repo uses different locations
EN_PATH = Path("reference/en_nz.json")
GLOBASA_PATH = Path("globasamc/assets/minecraft/lang/glb_glb.json")
OUT_PATH = Path("globasamc/assets/minecraft/lang/glb_glb.json")  # in-place update

def main():
    en = json.loads(EN_PATH.read_text(encoding="utf-8"))
    glb = json.loads(GLOBASA_PATH.read_text(encoding="utf-8"))

    merged = {}
    missing = 0
    kept = 0

    # Keep vanilla key order (nice for diff reviews)
    for k in en.keys():
        if k in glb and isinstance(glb[k], str) and glb[k].strip() != "":
            merged[k] = glb[k]
            kept += 1
        else:
            merged[k] = en[k]     # fallback to English
            missing += 1

    # (Optional) detect obsolete keys that existed in old file but not anymore
    obsolete = sorted(set(glb.keys()) - set(en.keys()))

    OUT_PATH.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print(f"Kept existing translations: {kept}")
    print(f"Missing (filled placeholder): {missing}")
    print(f"Obsolete keys (not written): {len(obsolete)}")
    if obsolete:
        print("First 30 obsolete keys:")
        for k in obsolete[:30]:
            print("  -", k)

if __name__ == "__main__":
    main()
