#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Compile mod payloads and prepare a static site. No firmware input is needed."""
import hashlib
import json
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent
VENDOR = ROOT / "vendor"
DIST = ROOT / "dist"

sys.path[:0] = [str(VENDOR / base) for base in ("", "mods", "scripts/firmware")]
import patcher  # noqa: E402
import payloadbuild  # noqa: E402
from launcher.model import load  # noqa: E402


def package_engine(path, sources):
    payload_mods = sorted(set(patcher.OPTIONS) & set(payloadbuild.payload_mods(patcher.MODEL)))
    groups = [group for count in range(1, len(payload_mods) + 1)
              for group in combinations(payload_mods, count)]
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        for source, name in sources:
            archive.writestr(ZipInfo(name), source.read_bytes(), compress_type=ZIP_DEFLATED)
        with ProcessPoolExecutor(max_workers=4) as pool:
            for group, payload in zip(groups, pool.map(payloadbuild.build, groups)):
                if tuple(payload.mods) != group:
                    raise ValueError("Wrong payload returned for " + ", ".join(group))
                key = "payloads/" + "+".join(group)
                archive.writestr(ZipInfo(key + ".bin"), payload.blob, compress_type=ZIP_DEFLATED)
                archive.writestr(ZipInfo(key + ".json"), json.dumps(payload.symbols, sort_keys=True),
                                 compress_type=ZIP_DEFLATED)
    print(f"Packaged {len(groups)} payload combinations", flush=True)


def main():
    web = ROOT / "web"
    sources = [(ROOT / "patcher.py", "patcher.py")]
    sources += [
        (path, path.relative_to(VENDOR).as_posix())
        for path in sorted(VENDOR.rglob("*"))
        if path.is_file() and path.suffix in {".py", ".conf", ".bin", ".s", ".S", ".c", ".h", ".ld"}
    ]
    DIST.mkdir(exist_ok=True)
    bundle = DIST / "patcher.zip"
    package_engine(bundle, sources)
    assets = sorted(path for path in web.iterdir() if path.name != "index.html")
    fingerprint = hashlib.sha256(bundle.read_bytes())
    for asset in assets:
        fingerprint.update(asset.read_bytes())
    key = fingerprint.hexdigest()[:12]
    output = DIST / "assets" / key
    output.mkdir(parents=True, exist_ok=True)
    bundle.replace(output / bundle.name)
    for asset in assets:
        shutil.copyfile(asset, output / asset.name)

    model = load(patcher.MODEL)
    config = {
        "stockVersion": model.fw_version,
        "stockHash": model.upd_sha256[0],
        "options": [
            {"id": name, "title": title, "description": description,
             "developer": name in patcher.DEVELOPER_OPTIONS}
            for name, (title, description) in patcher.OPTIONS.items()
        ],
        "conflict": patcher.CONFLICT,
    }
    (output / "stock.mjs").write_text(f"export default {json.dumps(config)};\n", encoding="utf-8")
    index = (web / "index.html").read_text(encoding="utf-8")
    (DIST / "index.html").write_text(index.replace("__ASSET_PATH__", f"./assets/{key}"), encoding="utf-8")
    shutil.copyfile(ROOT / "LICENSE", DIST / "LICENSE")
    (DIST / ".nojekyll").touch()
    print(f"Built assets/{key}", flush=True)


if __name__ == "__main__":
    main()
