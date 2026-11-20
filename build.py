#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Prepare the static GitHub Pages directory. No firmware input is needed."""
import json
import shutil
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent
VENDOR = ROOT / "vendor"
DIST = ROOT / "dist"

sys.path.insert(0, str(VENDOR))
from launcher.model import load  # noqa: E402


def main():
    DIST.mkdir(exist_ok=True)
    for asset in (ROOT / "web").iterdir():
        shutil.copyfile(asset, DIST / asset.name)
    shutil.copyfile(ROOT / "LICENSE", DIST / "LICENSE")
    model = load("cdj850")
    config = {"stockVersion": model.fw_version, "stockHash": model.upd_sha256[0]}
    (DIST / "stock.mjs").write_text(f"export default {json.dumps(config)};\n", encoding="utf-8")
    (DIST / ".nojekyll").touch()

    sources = [(ROOT / "patcher.py", "patcher.py")]
    sources += [
        (path, path.relative_to(VENDOR).as_posix())
        for path in sorted(VENDOR.rglob("*"))
        if path.is_file() and path.suffix in {".py", ".conf", ".bin", ".s"}
    ]
    with ZipFile(DIST / "patcher.zip", "w", compression=ZIP_DEFLATED) as archive:
        for path, name in sources:
            archive.writestr(ZipInfo(name), path.read_bytes(), compress_type=ZIP_DEFLATED)


if __name__ == "__main__":
    main()
