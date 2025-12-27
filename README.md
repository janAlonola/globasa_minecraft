# Globasa Minecraft Translation

A Minecraft Java Edition resource pack that adds **Globasa** as a selectable language and provides Globasa translations for the game UI.

## Download / Install

1. Download the latest `.zip` from **Releases** (or use “Download ZIP” from the repo).
2. Put the folder `globasamc` in your Minecraft resource pack folder:
   - Windows: `%APPDATA%\.minecraft\resourcepacks`
   - macOS: `~/Library/Application Support/minecraft/resourcepacks`
   - Linux: `~/.minecraft/resourcepacks`
3. Launch Minecraft → **Options** → **Resource Packs** → enable the pack.
4. Go to **Options** → **Language** → select **Globasa**.

## Compatibility

- **Minecraft Java Edition:** **1.21.11**

## Translation Status

Snapshot for **1.21.11**:

- Total keys (reference): **7765**

English-overlap analysis (whitelist applied):

- Identical to English: **4656**
- Identical but allowed/checked: **73**
- Mostly English: **260** (overlap ≥ 0.85)
- Partially translated: **1492**
- Fully translated: **1357** (overlap ≤ 0.05)
- Clean non-English progress: **1357** (**17.48%** of total keys)

> “Clean non-English progress” counts entries that are filled and contain (almost) no English tokens from the reference text, after applying the whitelist of words that are intentionally the same in Globasa.

## Contributing

Contributions are welcome!

- Please only change **values**, not the translation **keys**.
- Keep placeholders intact (examples: `%s`, `%1$s`, `%%`) and preserve newlines (`\n`) where present.
- Prefer small PRs focused on one area (menus, subtitles, items, etc.).

### Checking progress locally

This repo includes a progress script that compares the Globasa file to a reference language file and estimates completion:

```bash
python tools/progress.py
````

(Adjust the paths and whitelist inside `tools/progress.py` if your local setup differs.)

## License

TBD (add a license file: MIT / CC0 / etc.)