#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build the static CDJ-350 patcher. No firmware input is needed."""
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENDOR = ROOT / "vendor"
DIST = ROOT / "dist"

sys.path[:0] = [str(VENDOR), str(VENDOR / "scripts/firmware")]
from c850_repack import VERSION_OFF  # noqa: E402
from launcher.model import load  # noqa: E402


def main():
    web = ROOT / "web"
    model = load("cdj350")
    config = {
        "model": model.title,
        "filename": model.upd[0],
        "stockVersion": model.fw_version,
        "stockHash": model.upd_sha256[0],
        "versionOffset": VERSION_OFF,
        "counterUrl": os.environ.get("PATCH_COUNTER_URL", "").strip(),
    }
    stock_module = f"export default {json.dumps(config)};\n".encode("utf-8")
    assets = sorted(path for path in web.iterdir() if path.name != "index.html")
    fingerprint = hashlib.sha256(stock_module)
    for asset in assets:
        fingerprint.update(asset.read_bytes())
    key = fingerprint.hexdigest()[:12]

    # Keep retired assets from earlier builds out of the published site.
    shutil.rmtree(DIST, ignore_errors=True)
    output = DIST / "assets" / key
    output.mkdir(parents=True)
    for asset in assets:
        shutil.copyfile(asset, output / asset.name)
    (output / "stock.mjs").write_bytes(stock_module)
    index = (web / "index.html").read_text(encoding="utf-8")
    (DIST / "index.html").write_text(index.replace("__ASSET_PATH__", f"./assets/{key}"), encoding="utf-8")
    shutil.copyfile(ROOT / "LICENSE", DIST / "LICENSE")
    (DIST / ".nojekyll").touch()
    print(f"Built assets/{key}")


if __name__ == "__main__":
    main()
