# CDJ-350 Mods

[Open the firmware patcher](https://fruitylemonade.github.io/cdj-350-mods/)

Verify and repack the original Pioneer CDJ-350 **v1.14** firmware in your browser. There are currently no CDJ-350 firmware mods available in the patcher.

## Repack the stock firmware

1. Get the CDJ-350 v1.14 update from [AlphaTheta's firmware downloads](https://pioneer-support.zendesk.com/hc/en-us/articles/11949537649305-Firmware) and extract `C350MAIN.UPD`.
2. Open the patcher and choose `C350MAIN.UPD`. The patcher checks it against the SHA-256 of the original update. Your file stays in the browser.
3. Keep the version at `1.14` for a byte-for-byte copy, or enter a different version label in the form `D.DD`. The label is the only field the repacker changes.
4. Select **Repack firmware**, then download `C350MAIN.UPD`.

Keep the original update and follow the [official CDJ-350 update guide](https://downloads.support.alphatheta.com/firmwares/dj-players/CDJ-350/CDJ-350_update_guide_en.pdf) for installation. Repacked files have been checked byte-for-byte in the browser. Flashing a relabelled update has not been verified on hardware.

## Build the site

```sh
python3 build.py
python3 -m http.server --directory dist
```

The build uses the CDJ-350 profile from [FruityLemonade/cdj-850-emulator](https://github.com/FruityLemonade/cdj-850-emulator/tree/main/models). GitHub Actions refreshes the vendored tools, reports newly available CDJ-350 ports for review, and publishes the static site to GitHub Pages. A firmware mod needs a CDJ-350 implementation and CDJ-350 repacking and validation support before it can be offered here.

Derived from [CDJ-850 Mods](https://github.com/FruityLemonade/cdj-850-mods). Licensed under GPL-2.0-or-later.
