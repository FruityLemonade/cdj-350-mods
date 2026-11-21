# CDJ-850 Firmware Patcher

[Open the patcher](https://fruitylemonade.github.io/cdj-850-mods/)

Custom firmware for the Pioneer CDJ-850. Pick the mods you want in the browser and download a ready-to-install update file.

> [!WARNING]
> These custom builds are untested on physical decks. Installing one can cause playback problems or leave the deck unable to boot. Keep an original update file so you can recover.

## How to use it

1. Get the original Pioneer CDJ-850 **v1.13** update file, `C850MAIN.UPD`.
2. Open the [patcher](https://fruitylemonade.github.io/cdj-850-mods/) and choose that file.
3. Tick the mods you want (see the table below).
4. Enter a version number for the new firmware in `D.DD` format, for example `1.14`.
5. Download the patched update and install it on the deck the usual way.

Your firmware file never leaves your computer. All the patching happens in the browser.

## Available mods

All mods are off until you tick them, and you can combine them freely.

| Mod | What it does | How to use it on the deck |
|---|---|---|
| **USB WIDE tempo** | Gives you ±100% tempo for USB tracks. | Press **TEMPO** while at ±10%. It skips the other ranges and goes straight to **WIDE**. |
| **USB FLAC playback**  | Plays FLAC files from USB. Only stereo, 16-bit, 44.1 kHz files are supported. | Load a FLAC file like any other track. |
| **Hot cues** | Turns **BEAT 1**, **2** and **4** into hot cues A, B and C. Reads the hot cues you set in rekordbox, and saves new ones back to the USB stick. The beat LEDs show which slots are set (lit) and which are empty (blinking). | Press **BEAT SELECT + RELOOP** to switch hot-cue mode on or off (the display shows HOT CUE ON/OFF, and the setting is saved). Press a pad to jump to its cue, or to set one if the slot is empty. Hold **BEAT 8** and press a pad to delete its cue. |
| **Quantized loops** | Makes loops snap to the rekordbox beat grid: auto beat loops, LOOP IN and LOOP OUT. Loops stay in time however many times they repeat. Needs USB tracks analysed in rekordbox. | Press **BEAT SELECT + LOOP IN** to switch quantize on or off (the display shows QUANTIZE ON/OFF, and the setting is saved). |
| **Loop resize** | Halves or doubles a playing loop, following the beat grid when the track has one. | While a loop plays, press **CUE/LOOP CALL ◀** to halve it or **CALL ▶** to double it. Outside a loop the buttons work as normal. |
| **BPM up to 999** | Raises the BPM limit from 180 to 999, for both rekordbox beat grids and the BPM display. Useful for very fast genres. | Nothing to do. Fast tracks just show and play with their real BPM. |
| **BPM decimals** | Shows the actual BPM to two decimal places, next to the rekordbox BPM. | Open the **INFO** view on a track with a beat grid. |
| **20-minute auto standby** | Puts the deck into standby after 20 minutes without use, instead of 4 hours. | Turn on **AUTO STANDBY** in the **UTILITY** menu. |

## Going back to stock firmware

1. Open the patcher and choose the original v1.13 file.
2. Leave every mod unticked.
3. Enter a version **higher** than the one on the deck. For example, use `1.15` on a deck running `1.14`. The deck's updater may skip a file whose version matches what is already installed.
4. Download and install it.

The stock firmware is copied byte for byte. Only the version number changes.

## How it works

The browser checks the SHA-256 of your file to make sure it is the original v1.13 update. It then applies the patches in a Web Worker and offers the result as a download. The worker loads a pinned Pyodide runtime from jsDelivr and compresses the firmware with a JavaScript port of the reference LZSS encoder.

## Development

The mods are developed in the [CDJ-850 emulator project](https://github.com/FruityLemonade/cdj-850-emulator). Go there to write a new mod, change an existing one, test in the emulator or report a mod bug. This repository only packages those mods into the browser patcher.

### Building the patcher site

Install the [CDJ-850 SH-2A toolchain](https://github.com/FruityLemonade/cdj-850-emulator/blob/main/scripts/build/sh_elf_toolchain.sh). Put the `sh-elf-*` tools on your PATH or point `CDJ850_SH_ELF` at the toolchain prefix, for example `/opt/sh-elf/bin/sh-elf-`.

```sh
python3 sync_vendor.py ../cdj-850-emulator   # optional: take the mods from a local emulator checkout
python3 build.py
python3 -m http.server 8000 --directory dist
```

Open `http://localhost:8000/`. The build compiles the selectable combinations of mod payloads using the existing compiler driver. It needs no firmware file. GitHub Pages serves the static build from the `gh-pages` branch.

The tools and patch definitions in `vendor/` are copies from the [CDJ-850 emulator project](https://github.com/FruityLemonade/cdj-850-emulator); `vendor/UPSTREAM` names the emulator commit. The [pages workflow](.github/workflows/pages.yml) checks the emulator's `main` branch every hour, commits any change to `vendor/`, rebuilds the payloads and publishes the site, so the patcher always ships the newest mods. A new CDJ-850 mod in the emulator shows up as a workflow warning until it is added to `OPTIONS` in `patcher.py`, the browser adapter. See [LICENSE](LICENSE).
