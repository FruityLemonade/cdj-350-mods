# CDJ-850 Firmware Patcher

[Open the patcher](https://fruitylemonade.github.io/cdj-850-mods/)

Choose an original Pioneer CDJ-850 v1.13 `C850MAIN.UPD`, select one or more modifications, and repack the update. The patched download is labelled v1.14 so a deck running v1.13 can recognize it as a different version.

- **USB WIDE tempo** enables the ±100% tempo range on USB and jumps from ±10% to WIDE.
- **DSP probe** inserts a test hook in the audio DSP loop for developers.

The browser verifies the stock update by SHA-256, runs the existing patch and repack tools in a Web Worker, and offers the result as a local download. The worker loads the pinned Pyodide runtime from jsDelivr. Firmware files stay in the browser.

Modified firmware is untested on physical decks. Keep the original update for recovery.

## Development

Run the build and serve the output with Python 3.

```sh
python3 build.py
python3 -m http.server 8000 --directory dist
```

Open `http://localhost:8000/`. The build uses the checked-in patch tools and does not require a firmware file. GitHub Pages serves the contents of `dist/` from the `gh-pages` branch.

The tools and patch definitions in `vendor/` are unchanged copies from the [CDJ-850 emulator project](https://github.com/FruityLemonade/cdj-850-emulator/tree/5c7208e31bcebb30e3c2a502dec4e8b63ae34ed8). The browser adapter is in `patcher.py`. See [LICENSE](LICENSE).
