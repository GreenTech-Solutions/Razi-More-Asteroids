#!/usr/bin/env python3
"""Restore the original More Asteroids sprites and add tightly masked new minerals.

Only the crystalline, halide and electrostatic *asteroid body material* is
modified. An unchanged upstream pixel remains identical in the output. No
filters are run on whole sprites, transparent pixels, crushing arrows or
advanced-crushing product fragments.

Run: python scripts/restore-material-art.py
Source art copyright spartanlaser32; MIT licence retained in root LICENSE.
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path
import urllib.request
import zipfile

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_SHA = "ba209beccc0ad363a155e8ced0e3967f2997d500"
UPSTREAM_ZIP = "https://codeload.github.com/spartanlaser32/More-Asteroids/zip/" + UPSTREAM_SHA

# Never touch these five families' upstream art.
ORIGINALS = ("chemical", "organic", "rock", "scrap", "uranium")
# Use geometry-matched original asteroid material as the source.
NEW_FAMILIES = {
    "crystalline": "rock",
    "halide": "chemical",
    "electrostatic": "scrap",
}
SIZES = ("chunk", "small", "medium", "big", "huge")
ICON_PATTERNS = (
    "{f}-asteroid-chunk.png",
    "{f}-asteroid-crushing.png",
    "advanced-{f}-asteroid-crushing.png",
    "small-{f}-asteroid.png",
    "medium-{f}-asteroid.png",
    "big-{f}-asteroid.png",
    "huge-{f}-asteroid.png",
)

# A small fraction of the *asteroid body*, NOT the whole icon.
# Matte, believable minerals rather than pure, saturated RGB primaries.
ART = {
    "crystalline": {"coverage": 0.095, "colour": (93, 152, 185), "blend": 0.57},
    "halide": {"coverage": 0.095, "colour": (166, 131, 185), "blend": 0.58},
    "electrostatic": {"coverage": 0.105, "colour": (105, 116, 191), "blend": 0.57},
}


def source_archive():
    request = urllib.request.Request(UPSTREAM_ZIP, headers={"User-Agent": "More-Asteroids-graphics"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read(26_000_000)
    if len(payload) >= 26_000_000:
        raise ValueError("Upstream archive unexpectedly large")
    return zipfile.ZipFile(io.BytesIO(payload))


def read_upstream(zf, path):
    items = [k for k in zf.namelist() if k.endswith("/" + path)]
    if len(items) != 1:
        raise FileNotFoundError(path)
    return Image.open(io.BytesIO(zf.read(items[0]))).convert("RGBA")


def source_icon(zf, filename):
    im = read_upstream(zf, "graphics/icons/" + filename)
    if im.size == (120, 64):
        return im.crop((0, 0, 64, 64))  # main mip; no change to real sprite pixels
    if im.size == (64, 64):
        return im
    raise ValueError(f"Unexpected upstream icon dimensions: {filename} {im.size}")


def material_mask(img, family, icon_kind):
    """Build *semantic* mask using sprite geometry and source material signatures.

    The crusher and advanced-crusher masks are intentionally conservative:
    only the primary asteroid body in the upper-left is eligible.
    The arrows, miniatures, result items and background are hard-excluded.
    The surface score is smoothed ONLY for mask selection, never for output.
    """
    rgba = np.asarray(img, dtype=np.uint8)
    h, w = rgba.shape[:2]
    r, g, b = [rgba[:, :, i].astype(np.float32) for i in range(3)]
    a = rgba[:, :, 3]
    yy, xx = np.mgrid[:h, :w]
    allowed = a > 224

    # Leave antialiased outer perimeter and all transparent pixels alone.
    allowed &= np.asarray(
        Image.fromarray((allowed * 255).astype(np.uint8), "L")
        .filter(ImageFilter.MinFilter(3 if max(h, w) <= 128 else 5))
    ) > 0

    if icon_kind == "crushing":
        # The full chevron area (including grey rock arrows) is protected
        # geometrically, NOT using unreliable yellow-colour detection.
        allowed &= (xx < 39) & (yy < 27)
    elif icon_kind == "advanced":
        # Advanced recipes include other resources: never edit those outputs.
        allowed &= (xx < 38) & (yy < 36)
    elif icon_kind == "single":
        # These icons contain only the asteroid plus transparent background.
        pass
    elif icon_kind == "entity":
        pass
    else:
        raise ValueError(icon_kind)

    # Original asteroid material signatures: no random noise, no changes to
    # unrelated materials, no global hue shift or saturation adjustments.
    lum = 0.24 * r + 0.68 * g + 0.08 * b
    if family == "crystalline":
        # Cool, exposed grey-rock mineral faces rather than its rusty matrix.
        eligible = (b > 49) & (b >= r - 13) & (b >= g - 8)
        score = 0.47 * b + 1.60 * (b - r) + 0.50 * (b - g) + 0.12 * lum
    elif family == "halide":
        # Only naturally green, illuminated veins inside oxide stone.
        eligible = (g > 69) & (g > r + 3) & (g > b + 4)
        score = 0.50 * g + 1.00 * (g - r) + 0.95 * (g - b) + 0.12 * lum
    else:
        # Rust-coloured inclusions of upstream scrap; leave steel intact.
        eligible = (r > 73) & (r > g + 11) & (r > b + 10)
        score = 0.35 * r + 1.17 * (r - g) + 1.32 * (r - b) + 0.08 * lum

    allowed &= eligible
    if not np.any(allowed):
        # Leave this particular source unchanged rather than painting some
        # other component or relaxing a semantic mask to meet a quota.
        return np.zeros((h, w), dtype=bool), 0.0

    radius = 0.85 if max(h, w) <= 128 else max(1.5, min(4.5, max(h, w) / 100))
    # Smooth only the ranking scores to favour connected mineral faces rather
    # than pixel noise. The original RGB pixels are never blurred.
    floating_score = (score - score.min()) / max(0.001, score.max() - score.min())
    smooth = np.asarray(
        Image.fromarray(np.uint8(floating_score * 255), "L")
        .filter(ImageFilter.GaussianBlur(radius)),
        dtype=np.float32
    )

    # The coverage limit applies to opaque source ASTEROID pixels. For crushers
    # restrict selection further to the body rectangle, never arrows/products.
    full_body = rgba[:, :, 3] > 224
    if icon_kind in ("crushing", "advanced"):
        full_body &= (xx < 39) & (yy < (27 if icon_kind == "crushing" else 36))
    max_count = max(1, round(np.count_nonzero(full_body) * ART[family]["coverage"]))
    candidate_count = np.count_nonzero(allowed)
    if candidate_count > max_count:
        threshold = np.partition(smooth[allowed], -max_count)[-max_count]
        allowed &= smooth >= threshold
        # Keep an exact upper bound in case tied gradient pixels sit at threshold.
        ys, xs = np.where(allowed)
        if len(ys) > max_count:
            ranked = np.argsort(smooth[ys, xs], kind="stable")[::-1][:max_count]
            limited = np.zeros_like(allowed)
            limited[ys[ranked], xs[ranked]] = True
            allowed = limited
    actual_coverage = np.count_nonzero(allowed) / max(1, np.count_nonzero(full_body))
    assert actual_coverage <= ART[family]["coverage"] + 0.002
    return allowed, actual_coverage


def alter_only_mineral(img, family, kind):
    original = np.asarray(img.convert("RGBA")).copy()
    mask, coverage = material_mask(img, family, kind)
    output = original.copy()
    if np.any(mask):
        colour = np.asarray(ART[family]["colour"], dtype=np.float32)
        blend = ART[family]["blend"]
        source = original[:, :, :3].astype(np.float32)
        # Preserve the inherited stone/metal face lighting and local roughness.
        light = (0.72 + np.mean(source, axis=2) / 290.0)
        pigment = colour[None, None, :] * light[:, :, None]
        mixed = (1 - blend) * source + blend * pigment
        output[:, :, :3][mask] = np.clip(mixed[mask], 0, 255).astype(np.uint8)

    # These pixel-identity checks are essential. They prove that the arrows,
    # transparent background, resource outputs, and non-target mineral surfaces
    # are copied unmodified from the upstream originals.
    assert np.array_equal(output[:, :, 3], original[:, :, 3])
    assert np.array_equal(output[~mask], original[~mask])
    if kind == "crushing":
        assert np.array_equal(output[27:, :, :], original[27:, :, :])
        assert np.array_equal(output[:, 39:, :], original[:, 39:, :])
    if kind == "advanced":
        assert np.array_equal(output[36:, :, :], original[36:, :, :])
        assert np.array_equal(output[:, 38:, :], original[:, 38:, :])
    return Image.fromarray(output, "RGBA"), coverage


def write_if_changed(im, destination, check):
    if destination.exists():
        with Image.open(destination) as current:
            if current.size == im.size and current.convert("RGBA").tobytes() == im.tobytes():
                return False
    if check:
        print("Would change:", destination.relative_to(ROOT))
        return True
    destination.parent.mkdir(parents=True, exist_ok=True)
    im.save(destination, format="PNG", optimize=True)
    print("Updated:", destination.relative_to(ROOT))
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true", help="Report differences without writing files")
    opts = p.parse_args()
    archive = source_archive()
    total = 0
    fractions = {}
    for family in (*ORIGINALS, *NEW_FAMILIES):
        parent = NEW_FAMILIES.get(family, family)
        for pat in ICON_PATTERNS:
            name = pat.format(f=parent)
            art = source_icon(archive, name)
            kind = "crushing" if pat == "{f}-asteroid-crushing.png" else (
                "advanced" if pat.startswith("advanced-") else "single"
            )
            if family in NEW_FAMILIES:
                art, ratio = alter_only_mineral(art, family, kind)
                fractions.setdefault(family, []).append(ratio)
            total += write_if_changed(
                art, ROOT / "graphics/icons" / pat.format(f=family), opts.check
            )
        for size in SIZES:
            name = f"asteroid-{parent}-{size}-colour-01.png"
            art = read_upstream(archive, f"graphics/entity/asteroid/{parent}/{size}/{name}")
            if family in NEW_FAMILIES:
                art, ratio = alter_only_mineral(art, family, "entity")
                fractions.setdefault(family, []).append(ratio)
            destination = (ROOT / "graphics/entity/asteroid" / family / size /
                           f"asteroid-{family}-{size}-colour-01.png")
            total += write_if_changed(art, destination, opts.check)
    for family, ratios in fractions.items():
        print(f"{family}: inclusion coverage of the allowed asteroid body "
              f"{min(ratios):.1%} to {max(ratios):.1%}. Everything else copied unchanged.")
    print(f"Changed graphics: {total}")


if __name__ == "__main__":
    main()
