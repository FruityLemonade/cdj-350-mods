# SPDX-License-Identifier: GPL-2.0-or-later
"""Browser adapter for the emulator project's CDJ-850 tools."""
import hashlib

import c850_repack as repack
import modelfw
import patch_main
import validate

MODEL = "cdj850"
OUTPUT_VERSION = "1.14"
MODS = {
    "tempo_wide": ("tempowide", "tempowidemath1", "tempowidemath2"),
    "dsp_probe": ("dspprobe",),
}


def patch_update(stock, selections, progress):
    if not selections or any(name not in MODS for name in selections):
        raise ValueError("Select at least one available modification.")
    if hashlib.sha256(stock).hexdigest() != modelfw.main_file(MODEL)[1]:
        raise ValueError("Choose the original CDJ-850 firmware version 1.13.")

    progress("Applying selected modifications…")
    image = repack.unpack_main(stock)
    names = list(dict.fromkeys(patch for key in selections for patch in MODS[key]))
    report, spans = {}, {}
    patched = patch_main.patch(image, names, MODEL, report, spans)
    if any(report.get(name, (None,))[0] != "applied" for name in names):
        raise ValueError("A selected modification could not be applied.")
    if patched == image:
        raise ValueError("The selected modifications produced no changes.")

    progress("Compressing the modified firmware…")
    output = repack.build_upd(stock, patched)
    progress("Verifying the repacked update…")
    profile = patch_main.PATCH_SETS[MODEL].profile
    checks = validate.verify(
        stock, output, MODEL, {"main"}, {"main": spans}, {"main": profile}
    )
    if checks.exit_code:
        raise ValueError("The repacked firmware did not pass validation.")

    # The upstream validator requires the stock header during comparison.
    # Change the updater's version field only after that comparison passes.
    return repack.set_version(output, OUTPUT_VERSION)
