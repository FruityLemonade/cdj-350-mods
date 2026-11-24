#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build the static CDJ-350 patcher. No firmware input is needed."""
import hashlib
import json
import os
import shutil
import sys
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent
VENDOR = ROOT / "vendor"
DIST = ROOT / "dist"

sys.path[:0] = [str(VENDOR / subdir) for subdir in ("", "mods", "scripts/firmware")]
from c850_repack import VERSION_OFF  # noqa: E402
from launcher.model import load  # noqa: E402
import patcher  # noqa: E402
import payloadbuild  # noqa: E402
from patcher import MODEL  # noqa: E402


def package_engine(bundle):
    payload_mods = sorted(set(patcher.OPTIONS) & set(payloadbuild.payload_mods(MODEL)))
    groups = [group for count in range(1, len(payload_mods) + 1)
              for group in combinations(payload_mods, count)]
    mod_dirs = patcher.OPTIONS.keys() | {"loader", "payload", "players"}
    with ZipFile(bundle, "w", compression=ZIP_DEFLATED) as archive:
        def add(name, data):
            archive.writestr(ZipInfo(name), data, compress_type=ZIP_DEFLATED)

        add("patcher.py", (ROOT / "patcher.py").read_bytes())
        for path in sorted(VENDOR.rglob("*")):
            if not path.is_file() or path.suffix not in {".py", ".conf", ".bin", ".s", ".S", ".c", ".h", ".ld"}:
                continue
            rel = path.relative_to(VENDOR)
            if rel.parts[0] == "mods" and len(rel.parts) > 2 and rel.parts[1] not in mod_dirs:
                continue
            add(rel.as_posix(), path.read_bytes())
        for group in groups:
            payload = payloadbuild.build(group, MODEL)
            key = "payloads/" + "+".join(group)
            add(key + ".bin", payload.blob)
            add(key + ".json", json.dumps(payload.symbols, sort_keys=True))


def main():
    web = ROOT / "web"
    model = load(MODEL)
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
    with TemporaryDirectory(dir=ROOT) as tmp:
        staging = Path(tmp)
        bundle = staging / "patcher.zip"
        package_engine(bundle)
        fingerprint = hashlib.sha256(stock_module)
        fingerprint.update(bundle.read_bytes())
        for asset in assets:
            fingerprint.update(asset.read_bytes())
        key = fingerprint.hexdigest()[:12]

        output = staging / "assets" / key
        output.mkdir(parents=True)
        bundle.replace(output / bundle.name)
        for asset in assets:
            shutil.copyfile(asset, output / asset.name)
        (output / "stock.mjs").write_bytes(stock_module)
        index = (web / "index.html").read_text(encoding="utf-8")
        (staging / "index.html").write_text(
            index.replace("__ASSET_PATH__", f"./assets/{key}"), encoding="utf-8"
        )
        shutil.copyfile(ROOT / "LICENSE", staging / "LICENSE")
        (staging / ".nojekyll").touch()

        # Publish only after the payload and all site assets are ready.
        shutil.rmtree(DIST, ignore_errors=True)
        staging.replace(DIST)
    print(f"Built assets/{key}")


if __name__ == "__main__":
    main()
