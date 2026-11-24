# SPDX-License-Identifier: GPL-2.0-or-later
"""Browser adapter for the validated CDJ-350 firmware patches."""
import hashlib
import json
from pathlib import Path

import c850_repack
import modelfw
import patch_main
import payloadbuild
import validate

MODEL = "cdj350"
OPTIONS = {
    "flac": (
        "USB FLAC playback",
        "Stereo FLAC, 16 or 24 bit, 44.1 or 48 kHz. Tested in the CDJ-350 emulator.",
    ),
    "quant_loops": (
        "Quantized loops",
        "Snap BEAT LOOP, LOOP IN, and LOOP OUT to the nearest beat of the rekordbox grid, with per-pass drift correction. Tested in the CDJ-350 emulator.",
    ),
}
MODS = {name: list(modelfw.mod_patch(name, MODEL).MODS) for name in OPTIONS}


def prebuilt_payload(folders, model):
    if model != MODEL:
        raise payloadbuild.PayloadError("Unsupported model.")
    key = "+".join(sorted(folders))
    base = Path(__file__).with_name("payloads") / key
    try:
        blob = base.with_suffix(".bin").read_bytes()
        symbols = json.loads(base.with_suffix(".json").read_text(encoding="utf-8"))
    except OSError as error:
        raise payloadbuild.PayloadError("Missing prebuilt CDJ-350 payload for " + key) from error
    return payloadbuild.Payload(blob, symbols, tuple(folders), "", {})


def patch_update(stock, selections, version, progress):
    if not selections or any(name not in MODS for name in selections):
        raise ValueError("Choose modifications from the available options.")
    if hashlib.sha256(stock).hexdigest() != modelfw.main_file(MODEL)[1]:
        raise ValueError("Choose the original CDJ-350 v1.14 C350MAIN.UPD.")
    if version == modelfw.cdj_model.load(MODEL).fw_version:
        raise ValueError("Choose an output version that differs from the stock version.")

    progress("Applying selected modifications…")
    image = c850_repack.unpack_main(stock)
    names = list(dict.fromkeys(patch for key in selections for patch in MODS[key]))
    names = patch_main.with_loader(names, MODEL)
    report, spans = {}, {}
    patched = patch_main.patch(image, names, MODEL, report, spans)
    if any(report.get(name, (None,))[0] != "applied" for name in names):
        print(report)
        raise ValueError("A selected modification could not be applied.")

    progress("Compressing the modified firmware…")
    output = c850_repack.build_upd(stock, patched, version=version, model=MODEL)
    progress("Verifying the generated update…")
    profile = patch_main.PATCH_SETS[MODEL].profile
    checks = validate.verify(
        stock, output, MODEL, {"main"}, {"main": spans}, {"main": profile}
    )
    if checks.exit_code:
        print(checks.text())
        raise ValueError("The generated update did not pass validation.")
    return output
