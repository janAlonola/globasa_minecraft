#!/usr/bin/env python3
"""
Minecraft language pack progress estimator.

Reports:
- Filled progress: % of reference keys that have a non-empty value
- Still English: filled and identical to reference English (except allowed same-words)
- Fully translated: filled and contains ~no English tokens from reference (after allowed words removed)
- Partially translated: filled and contains some English tokens from reference (after allowed words removed)

New:
- SAME_AS_ENGLISH_WORDS: words you consider "translated/checked" even if they match English
  e.g. colors like "blue", "orange" that you intentionally keep as-is.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, Set, Tuple, List


# =========================
# EDIT THESE INPUTS
# =========================
REFERENCE_PATH = Path("reference/en_nz.json")
LANG_PATH = Path("globasamc/assets/minecraft/lang/glb_glb.json")
ENGLISH_PATH = Path("reference/en_nz.json")  # set to None to disable overlap stats

PRINT_MISSING_KEYS = True
MISSING_KEYS_CAP = 200

PRINT_PARTIAL_EXAMPLES = True
PARTIAL_EXAMPLES_CAP = 40

# Words you accept as "translated/checked" even if they remain English.
# Put them in lowercase.
SAME_AS_ENGLISH_WORDS: Set[str] = {
    "blue",
    "orange",
    # add more here...
}

# Heuristic thresholds
MOSTLY_ENGLISH_THRESHOLD = 0.85
FULLY_TRANSLATED_THRESHOLD = 0.05
# =========================
# END EDIT SECTION
# =========================


PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[sdfoxXeEgGcbhHaAtT]|%%")
MC_COLOR_RE = re.compile(r"§.")  # Minecraft formatting codes


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_filled(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ""


def normalize_for_tokens(s: str) -> str:
    # Remove placeholders and formatting codes so they don't skew overlap
    s = PLACEHOLDER_RE.sub(" ", s)
    s = MC_COLOR_RE.sub(" ", s)
    return s.lower()


def tokens(s: str) -> Set[str]:
    s = normalize_for_tokens(s)
    return set(re.findall(r"[a-z0-9]+", s))


def filtered_english_tokens(english: str) -> Set[str]:
    """English tokens minus the whitelist of allowed same-as-English words."""
    e = tokens(english)
    return {t for t in e if t not in SAME_AS_ENGLISH_WORDS}


def overlap_ratio(english: str, candidate: str) -> float:
    """
    Ratio of (filtered) English tokens present in candidate.
    1.0 means candidate contains all filtered English tokens (likely English).
    0.0 means candidate contains none of them (likely fully translated).
    """
    e = filtered_english_tokens(english)
    if not e:
        # English string contains only whitelisted words/placeholders/etc.
        return 0.0
    c = tokens(candidate)
    return len(e & c) / len(e)


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
    missing_or_empty: List[str] = []

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
    print(f"Allowed same-as-English words: {len(SAME_AS_ENGLISH_WORDS)}")
    if SAME_AS_ENGLISH_WORDS:
        preview = ", ".join(sorted(list(SAME_AS_ENGLISH_WORDS))[:20])
        print(f"  (preview: {preview}{' ...' if len(SAME_AS_ENGLISH_WORDS) > 20 else ''})")
    print()
    print(f"Total keys (reference): {total}")
    print(f"Filled translations:     {filled}  ({filled_pct:.2f}%)")
    print(f"Missing/empty:           {len(missing_or_empty)}")

    # Overlap / English detection
    if ENGLISH_PATH is not None:
        if not ENGLISH_PATH.exists():
            raise SystemExit(f"English file not found: {ENGLISH_PATH}")
        en = load_json(ENGLISH_PATH)

        identical_english = 0
        identical_but_allowed = 0
        fully_translated = 0
        partially_translated = 0
        mostly_english = 0

        partial_examples: List[Tuple[float, str, str, str]] = []

        for k in ref_keys:
            gv = glb.get(k, None)
            ev = en.get(k, None)

            if not (isinstance(gv, str) and isinstance(ev, str)):
                continue
            if not is_filled(gv):
                continue

            # If identical to English, only count as "still English" if it includes
            # some non-whitelisted English tokens.
            if gv == ev:
                if filtered_english_tokens(ev):
                    identical_english += 1
                else:
                    # e.g. "Blue" where "blue" is in SAME_AS_ENGLISH_WORDS
                    identical_but_allowed += 1
                    fully_translated += 1
                continue

            r = overlap_ratio(ev, gv)

            if r >= MOSTLY_ENGLISH_THRESHOLD:
                mostly_english += 1
                if PRINT_PARTIAL_EXAMPLES:
                    partial_examples.append((r, k, ev, gv))
            elif r <= FULLY_TRANSLATED_THRESHOLD:
                fully_translated += 1
            else:
                partially_translated += 1
                if PRINT_PARTIAL_EXAMPLES:
                    partial_examples.append((r, k, ev, gv))

        clean_non_english = fully_translated
        clean_non_english_pct = 100.0 * clean_non_english / total

        print()
        print("English-overlap analysis (whitelist applied):")
        print(f"Identical to English:            {identical_english}")
        print(f"Identical but allowed/checked:   {identical_but_allowed}")
        print(f"Mostly English:                  {mostly_english}  (overlap >= {MOSTLY_ENGLISH_THRESHOLD:.2f})")
        print(f"Partially translated:            {partially_translated}")
        print(f"Fully translated:                {fully_translated}  (overlap <= {FULLY_TRANSLATED_THRESHOLD:.2f})")
        print(f"Clean non-English progress:      {clean_non_english}  ({clean_non_english_pct:.2f}% of total keys)")

        if PRINT_PARTIAL_EXAMPLES and partial_examples:
            partial_examples.sort(key=lambda x: x[0], reverse=True)
            print()
            print(f"Partial/mostly-English examples (top {PARTIAL_EXAMPLES_CAP} by overlap):")
            for r, k, ev, gv in partial_examples[:PARTIAL_EXAMPLES_CAP]:
                print(f"- {k}  (overlap {r:.2f})")
                print(f"  en:  {ev}")
                print(f"  glb: {gv}")

    if PRINT_MISSING_KEYS and missing_or_empty:
        print()
        print(f"Missing/empty keys (first {MISSING_KEYS_CAP}):")
        for k in missing_or_empty[:MISSING_KEYS_CAP]:
            print("  -", k)
        if len(missing_or_empty) > MISSING_KEYS_CAP:
            print(f"  ... and {len(missing_or_empty) - MISSING_KEYS_CAP} more")


if __name__ == "__main__":
    main()
