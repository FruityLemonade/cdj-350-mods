# CDJ-350 Mods

[Open the firmware patcher](https://fruitylemonade.github.io/cdj-350-mods/)

Build an update from the original Pioneer CDJ-350 **v1.14** firmware. Available
modifications, tested in the CDJ-350 emulator (physical deck validation is pending):

- **USB FLAC playback**: stereo 16- or 24-bit FLAC at 44.1 or 48 kHz.
- **Quantized loops**: snap `BEAT LOOP`, `LOOP IN`, and `LOOP OUT` to the nearest beat of the rekordbox grid, with per-pass drift correction. `QUANTIZE` and `DRIFT FIX` switch on or off at the end of the `UTILITY` list (both on by default, saved).
- **INFO track details**: the INFO rotary shows `Title - Artist`, the actual BPM with two decimals and the Camelot key (such as `128.23 8A`), and `RATING ****` for rekordbox USB tracks.
- **Played markers and track sort**: tracks played for over 20 seconds get a `*` in the USB browser, and `TRACK` lists by BPM or key (`UTILITY` > `SORT`: DEFAULT / BPM / KEY, saved).
- **BPM up to 999**: beat grids above 180 BPM keep their real tempo instead of `180.0`, and the `BPM LOCK` master BPM goes up to 999.

To reach the new `UTILITY` items, hold `DISPLAY/UTILITY` and turn past `Ver`.

## Build an update in the browser

1. Get the CDJ-350 v1.14 update from [AlphaTheta's firmware downloads](https://pioneer-support.zendesk.com/hc/en-us/articles/11949537649305-Firmware) and extract `C350MAIN.UPD`.
2. Choose the original file in the patcher. It checks the official SHA-256 and works on your local copy in the browser.
3. Select the modifications you want to apply (any combination). The output version defaults to `1.15`. For a byte-for-byte stock copy, clear all checkboxes and enter `1.14`.
4. Select **Patch firmware** or **Repack firmware**, then download `C350MAIN.UPD`.

Keep the original update and use the [official CDJ-350 update guide](https://downloads.support.alphatheta.com/firmwares/dj-players/CDJ-350/CDJ-350_update_guide_en.pdf) for the deck's update procedure.

## Build the site locally

Build the emulator project's SH-2A toolchain with
`scripts/build/sh_elf_toolchain.sh`. Point the website build at its
`sh-elf-` prefix.

```sh
CDJ850_SH_ELF=/path/to/tools/sh-elf/bin/sh-elf- python3 build.py
python3 -m http.server --directory dist
```

The build packages the compiled mod payloads (one per combination of payload
mods) and the emulator project's patch and validation tools. No firmware file is needed to build the site. The browser worker
loads Pyodide for the patch engine. The stock repacker runs directly in JavaScript.

GitHub Actions refreshes the vendored tools and publishes the static site to
GitHub Pages. Sync preserves the working FLAC port while upstream is missing it.

Derived from [CDJ-850 Mods](https://github.com/FruityLemonade/cdj-850-mods). Licensed under GPL-2.0-or-later.
