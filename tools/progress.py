#!/usr/bin/env python3
"""
Minecraft language pack progress estimator.

Edit the PATHS below, then run:
    python tools/progress.py

It reports:
- Filled progress: % of reference keys that have a non-empty value in your lang file
- Optional "non-English" progress: counts filled entries that differ from vanilla en_us.json
"""

import json
from pathlib import Path
from typing import Any, Dict, Set


# =========================
# EDIT THESE INPUTS
# =========================

# 1) Reference key set (authoritative keys).
#    Use either:
#    - the extracted vanilla en_us.json (best), OR
#    - a schema file that contains keys (values can be anything).
REFERENCE_PATH = Path("reference/en_nz.json")

# 2) Your target language file (Globasa).
LANG_PATH = Path("globasamc/assets/minecraft/lang/glb_glb.json")

# 3) Optional: vanilla en_us.json (for detecting entries that are still English).
#    Set to None to disable.
ENGLISH_PATH = Path("reference/en_nz.json")  # or None

# 4) Optional: print missing/empty keys (cap below).
PRINT_MISSING_KEYS = True
MISSING_KEYS_CAP = 200

# =========================
# END EDIT SECTION
# =========================


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_filled(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ""


def main() -> None:
    if not REFERENCE_PATH.exists():
        raise SystemExit(f"Reference file not found: {REFERENCE_PATH}")

    if not LANG_PATH.exists():
        raise SystemExit(f"Lang file not found: {LANG_PATH}")

    ref = load_json(REFERENCE_PATH)
    glb = load_json(LANG_PATH)

    ref_keys: Set[str] = set(ref.keys())
    total = len(ref_keys)
    if total == 0:
        raise SystemExit(f"Reference file has no keys: {REFERENCE_PATH}")

    filled = 0
    missing_or_empty = []

    for k in sorted(ref_keys):
        v = glb.get(k, None)
        if is_filled(v):
            filled += 1
        else:
            missing_or_empty.append(k)

    filled_pct = 100.0 * filled / total

    print("=== Globasa Minecraft Translation Progress ===")
    print(f"Reference: {REFERENCE_PATH}")
    print(f"Lang file: {LANG_PATH}")
    print()
    print(f"Total keys (reference): {total}")
    print(f"Filled translations:     {filled}  ({filled_pct:.2f}%)")
    print(f"Missing/empty:           {len(missing_or_empty)}")

    # Optional: "still English" detection
    if ENGLISH_PATH is not None:
        if not ENGLISH_PATH.exists():
            raise SystemExit(f"English file not found: {ENGLISH_PATH}")

        en = load_json(ENGLISH_PATH)

        non_english = 0
        identical_english = 0

        for k in ref_keys:
            gv = glb.get(k, None)
            ev = en.get(k, None)

            if not (isinstance(gv, str) and isinstance(ev, str)):
                continue
            if not is_filled(gv):
                continue

            if gv == ev:
                identical_english += 1
            else:
                non_english += 1

        non_english_pct = 100.0 * non_english / total

        print()
        print("If you treat 'still English' as NOT translated:")
        print(f"Non-English (filled & != en_us): {non_english}  ({non_english_pct:.2f}% of total keys)")
        print(f"Identical to en_us (likely untranslated): {identical_english}")

    if PRINT_MISSING_KEYS and missing_or_empty:
        print()
        print(f"Missing/empty keys (first {MISSING_KEYS_CAP}):")
        for k in missing_or_empty[:MISSING_KEYS_CAP]:
            print("  -", k)
        if len(missing_or_empty) > MISSING_KEYS_CAP:
            print(f"  ... and {len(missing_or_empty) - MISSING_KEYS_CAP} more")


if __name__ == "__main__":
    main()
