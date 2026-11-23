# SPDX-License-Identifier: GPL-2.0-or-later
"""Browser adapter for the validated CDJ-350 USB FLAC patch."""
import hashlib
import json
from pathlib import Path

import c850_repack
import modelfw
import patch_main
import payloadbuild
import validate

MODEL = "cdj350"


def prebuilt_payload(folders, model):
    if model != MODEL or tuple(folders) != ("flac",):
        raise payloadbuild.PayloadError("Unsupported payload selection.")
    root = Path(__file__).with_name("payload")
    try:
        blob = root.with_suffix(".bin").read_bytes()
        symbols = json.loads(root.with_suffix(".json").read_text(encoding="utf-8"))
    except OSError as error:
        raise payloadbuild.PayloadError("Missing prebuilt CDJ-350 FLAC payload.") from error
    return payloadbuild.Payload(blob, symbols, ("flac",), "", {})


def patch_flac(stock, version, progress):
    if hashlib.sha256(stock).hexdigest() != modelfw.main_file(MODEL)[1]:
        raise ValueError("Choose the original CDJ-350 v1.14 C350MAIN.UPD.")
    if version == modelfw.cdj_model.load(MODEL).fw_version:
        raise ValueError("Choose an output version that differs from the stock version.")

    progress("Applying USB FLAC playback…")
    image = c850_repack.unpack_main(stock)
    names = patch_main.with_loader(modelfw.mod_patch("flac", MODEL).MODS, MODEL)
    report, spans = {}, {}
    patched = patch_main.patch(image, names, MODEL, report, spans)
    if any(report.get(name, (None,))[0] != "applied" for name in names):
        print(report)
        raise ValueError("The USB FLAC patch could not be applied in full.")

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
