# SPDX-License-Identifier: GPL-2.0-or-later
"""Browser adapter for the emulator project's CDJ-850 tools."""
import hashlib
import json
from pathlib import Path

import c850_repack as repack
import modelfw
import patch_main
import payloadbuild
import validate
from patch_update import conf_rows

MODEL = "cdj850"
OPTIONS = {
    "tempo_wide": ("USB WIDE tempo", "Enable ±100% tempo on USB. TEMPO cycles ±6% → ±10% → ±16% → WIDE, as on a CD."),
    "flac": ("USB FLAC playback", "Experimental: plays stereo 16-bit, 44.1 kHz FLAC files. Holding SEARCH or spinning the jog fast can drop the sound for a moment."),
    "hot_cues": ("Hot cues", "Use BEAT 1, 2 and 4 for hot cues A–C, read from and saved to rekordbox. Hold BEAT 8 and press one to delete it. Toggle with BEAT SELECT + RELOOP. Unfinished: a jump takes a few seconds."),
    "quant_loops": ("Quantized loops", "Snap loops (and new hot cues) to the nearest beat of the rekordbox grid. Toggle with BEAT SELECT + LOOP IN."),
    "loop_resize": ("Loop resize", "While a loop plays, use CUE/LOOP CALL to halve or double its length."),
    "bpm999": ("BPM up to 999", "Raise the tempo ceiling for rekordbox grids and the panel display."),
    "bpm_decimals": ("BPM decimals", "Show the actual BPM to two decimal places in place of the rekordbox BPM in the INFO view, on grid tracks."),
    "info_order": ("INFO screen order", "Reorder the INFO screens for USB tracks: Track, BPM and Camelot key (e.g. 128.23 12A), waveform / Artist, Rating, Key / Album, Comment."),
    "auto_standby": ("20-minute auto standby", "Shorten the idle timeout to 20 minutes when AUTO STANDBY is enabled."),
}

rows = conf_rows()
MODS = {name: rows[name] for name in OPTIONS}


def prebuilt_payload(folders, model):
    """Load the exact payload combination that the site compiled at build time."""
    key = "+".join(sorted(folders))
    base = Path(__file__).with_name("payloads") / key
    try:
        blob = base.with_suffix(".bin").read_bytes()
        symbols = json.loads(base.with_suffix(".json").read_text(encoding="utf-8"))
    except OSError as error:
        raise payloadbuild.PayloadError("Missing prebuilt payload for " + key) from error
    return payloadbuild.Payload(blob, symbols, tuple(folders), "", {})


def patch_update(stock, selections, version, progress):
    if any(name not in MODS for name in selections):
        raise ValueError("Choose modifications from the available options.")
    if hashlib.sha256(stock).hexdigest() != modelfw.main_file(MODEL)[1]:
        raise ValueError("Choose the original CDJ-850 firmware version 1.13.")

    relabelled = repack.set_version(stock, version)
    if not selections:
        progress("Verifying the stock update…")
        if repack.check_upd(relabelled):
            raise ValueError("The stock update did not pass validation.")
        return relabelled

    progress("Applying selected modifications…")
    image = repack.unpack_main(stock)
    names = list(dict.fromkeys(patch for key in selections for patch in MODS[key]))
    names = patch_main.with_loader(names, MODEL)
    report, spans = {}, {}
    patched = patch_main.patch(image, names, MODEL, report, spans)
    if any(report.get(name, (None,))[0] != "applied" for name in names):
        raise ValueError("A selected modification could not be applied.")
    if patched == image:
        raise ValueError("The selected modifications produced no changes.")

    progress("Compressing the modified firmware…")
    output = repack.build_upd(stock, patched, version=version)
    progress("Verifying the repacked update…")
    profile = patch_main.PATCH_SETS[MODEL].profile
    checks = validate.verify(
        stock, output, MODEL, {"main"}, {"main": spans}, {"main": profile}
    )
    if checks.exit_code:
        print(checks.text())
        raise ValueError("The repacked firmware did not pass validation.")
    return output
