# CDJ-850 Firmware Patcher

[Open the patcher](https://fruitylemonade.github.io/cdj-850-mods/)

Choose an original Pioneer CDJ-850 v1.13 `C850MAIN.UPD`, select the mods you want, enter an output version in `D.DD` format, and download the repacked update. The options include USB WIDE tempo, experimental USB FLAC playback, hot cues, quantized loops, loop resize, BPM up to 999, BPM decimals, and 20-minute auto standby. The BPM display probe and payload demo are under Developer tools.

To replace a custom build with stock firmware, leave all mods unchecked and enter a version higher than the one shown on the deck. For example, use `1.15` on a deck running `1.14`. The stock firmware payload is copied byte for byte and only the version field changes. The service-mode updater can skip a file whose version matches the installed version.

**Firmware installation risk.** These custom builds are untested on physical decks. Installing one can cause playback problems or leave the deck unable to boot. Keep an original update for recovery.

The browser verifies the stock update by SHA-256, applies the existing patches in a Web Worker, and offers the result as a local download. The worker loads the pinned Pyodide runtime from jsDelivr and uses a JavaScript port of the reference LZSS encoder for compression. Firmware files stay in the browser.

## Development

Install the [CDJ-850 SH-2A toolchain](https://github.com/FruityLemonade/cdj-850-emulator/blob/59da742b402bd9a712328de52e766242c9942f7a/scripts/build/sh_elf_toolchain.sh). Put the `sh-elf-*` tools on your PATH or point `CDJ850_SH_ELF` at the toolchain prefix, for example `/opt/sh-elf/bin/sh-elf-`.

```sh
python3 build.py
python3 -m http.server 8000 --directory dist
```

Open `http://localhost:8000/`. The build compiles the selectable combinations of mod payloads using the existing compiler driver. It needs no firmware file. GitHub Pages serves the static build from the `gh-pages` branch.

The tools and patch definitions in `vendor/` are unchanged copies from the [CDJ-850 emulator project](https://github.com/FruityLemonade/cdj-850-emulator/tree/59da742b402bd9a712328de52e766242c9942f7a). The browser adapter is in `patcher.py`. See [LICENSE](LICENSE).
