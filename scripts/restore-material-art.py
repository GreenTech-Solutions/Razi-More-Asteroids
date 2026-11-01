#!/usr/bin/env python3
"""Rebuild More Asteroids artwork from original, high-detail source PNGs.

The source is the MIT-licensed spartanlaser32/More-Asteroids repo, pinned below.
All replacements are independently rebuilt from source, not re-tinted fork images.

The five original families are restored without colour changes. The three new
families replace only specific pigments/inclusions of carefully chosen original
materials. All other pixels, local shading, fracture detail and alpha stay intact.
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path
import urllib.request
import zipfile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_COMMIT = "ba209beccc0ad363a155e8ced0e3967f2997d500"
ORIGINAL_ZIP = (
    "https://codeload.github.com/spartanlaser32/More-Asteroids/zip/"
    + ORIGINAL_COMMIT
)

# Parent artwork determines geometry AND the matching Space Age normal map.
# See asteroid_map in asteroids.lua: carbonic for petrified, metallic for scrap,
# oxide for chemical.
PARENTS = {
    "chemical": "chemical",
    "organic": "organic",
    "rock": "rock",
    "scrap": "scrap",
    "uranium": "uranium",
    "crystalline": "petrified",
    "halide": "chemical",
    "electrostatic": "scrap",
}
ORIGINAL_FAMILIES = ("chemical", "organic", "rock", "scrap", "uranium")
CUSTOM_FAMILIES = ("crystalline", "halide", "electrostatic")
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


def download_source():
    req = urllib.request.Request(
        ORIGINAL_ZIP, headers={"User-Agent": "Razi-More-Asteroids-source-art"}
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        blob = response.read(25_000_001)
    if len(blob) > 25_000_000:
        raise ValueError("Source archive exceeded expected size")
    return zipfile.ZipFile(io.BytesIO(blob))


def open_source(zf, path):
    matches = [key for key in zf.namelist() if key.endswith("/" + path)]
    if len(matches) != 1:
        raise FileNotFoundError(f"Source asset not unique or absent: {path}")
    return Image.open(io.BytesIO(zf.read(matches[0]))).convert("RGBA")


def original_icon(zf, name):
    image = open_source(zf, "graphics/icons/" + name)
    # Upstream is a complete 120x64 mip strip. The fork expects a 64x64 icon.
    if image.size == (120, 64):
        return image.crop((0, 0, 64, 64))
    if image.size == (64, 64):
        return image
    raise ValueError(f"Unexpected icon format {name} = {image.size}")


def isolate_inclusions(image, family, standard_recipe=False):
    """Select only source-material pigments. No global hue/tint replacement.

    crystalline: bright ochre-orange mineral inclusions in petrified rock;
                 preserve the original dark carbonic rock matrix.
    halide:      bright jade streaks in oxide rock; preserve original muted
                 turquoise/green rock and deep crevices.
    electrostatic: warm oxidised metal flakes in the scrap asteroid; preserve
                 blue/steel metal, metal ridges and all shadows.

    A pixel outside the mask is copied EXACTLY from upstream, bit for bit.
    """
    original = np.asarray(image.convert("RGBA")).copy()
    rgb = original[:, :, :3].astype(np.float32)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    a = original[:, :, 3]
    if family == "crystalline":
        mask = (r > 158) & (r > 1.42 * g) & (r > 1.43 * b) & ((r - g) > 42)
    elif family == "halide":
        mask = (g > 109) & (g > 1.07 * r) & (g > 1.08 * b) & ((g - b) > 18)
    elif family == "electrostatic":
        mask = (r > 105) & (r > 1.18 * g) & (r > 1.20 * b) & ((r - g) > 22)
    else:
        raise ValueError(f"Not a custom family: {family}")
    mask &= a > 48

    if standard_recipe:
        # The original icon's golden crushing arrows occupy the lower half.
        # Never recolour arrows or their existing highlights.
        row_index = np.arange(image.height, dtype=np.int32)[:, None]
        mask &= row_index < 30

    # Keep only the brightest exposed mineral inclusions, never an entire
    # contiguous asteroid surface. The cap is applied to each original PNG
    # individually, allowing for the different small/huge/recipe silhouettes.
    # Pixel selection is based on original material luminance/chroma only.
    coverage_limit = {"crystalline": 0.26, "halide": 0.19, "electrostatic": 0.24}[family]
    visible = int(np.count_nonzero(a > 48))
    max_selected = max(1, int(visible * coverage_limit))
    if np.count_nonzero(mask) > max_selected:
        if family == "crystalline":
            score = r * 0.55 + (r - g) * 1.25 + (r - b) * 0.5
        elif family == "halide":
            score = g * 0.50 + (g - b) * 1.5 + (g - r) * 0.25
        else:
            score = r * 0.60 + (r - g) * 1.35 + (r - b) * 0.20
        candidates = score[mask]
        cutoff = np.partition(candidates, -max_selected)[-max_selected]
        mask &= score >= cutoff

    hsv = np.asarray(image.convert("RGB").convert("HSV")).copy()
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    if family == "crystalline":
        # Frost-blue quartz highlights in naturally dark fossilised stone.
        # Preserve per-pixel brightness variations that form crystal facets.
        cooler = (g > 75)
        h[mask] = np.where(cooler[mask], 139, 163).astype(np.uint8)
        s[mask] = np.where(cooler[mask], 100, 117).astype(np.uint8)
        v[mask] = np.minimum(255, v[mask].astype(np.int16) + 8).astype(np.uint8)
    elif family == "halide":
        # Icy lilac salt inclusions. Dark surrounding green rock remains original.
        colder = (b > 55)
        h[mask] = np.where(colder[mask], 183, 173).astype(np.uint8)
        s[mask] = np.where(colder[mask], 93, 112).astype(np.uint8)
        v[mask] = np.minimum(255, v[mask].astype(np.int16) + 5).astype(np.uint8)
    else:
        # Swap rusty-orange ONLY into violet/cyan electrically conductive seams.
        bright = (r > 161)
        h[mask] = np.where(bright[mask], 173, 190).astype(np.uint8)
        s[mask] = np.where(bright[mask], 168, 136).astype(np.uint8)

    toned = np.asarray(Image.fromarray(hsv, "HSV").convert("RGB"))
    changed = original.copy()
    changed[mask, :3] = toned[mask]
    output = Image.fromarray(changed, "RGBA")

    assert np.array_equal(original[:, :, 3], changed[:, :, 3])
    changed_pixels = np.any(original[:, :, :3] != changed[:, :, :3], axis=2)
    opaque = original[:, :, 3] > 48
    ratio = float(np.count_nonzero(changed_pixels & opaque)) / max(1, int(np.count_nonzero(opaque)))
    # A strict ceiling catches accidental blanket transformations or arrow recolour.
    if not 0.005 <= ratio <= 0.48:
        raise ValueError(f"{family}: changed {ratio:.1%} of visible pixels; expected selected inclusions only")
    return output, ratio


def emit(image, destination, dry_run):
    image = image.convert("RGBA")
    if destination.exists():
        with Image.open(destination) as prev:
            if prev.size == image.size and prev.convert("RGBA").tobytes() == image.tobytes():
                return False
    if dry_run:
        print("Would update:", destination.relative_to(ROOT))
        return True
    destination.parent.mkdir(exist_ok=True, parents=True)
    image.save(destination, optimize=True)
    print("Updated:", destination.relative_to(ROOT))
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Preview changed paths without writing")
    args = parser.parse_args()
    zf = download_source()
    changes = 0
    counts = {}

    for family, parent in PARENTS.items():
        for pattern in ICON_PATTERNS:
            dest = ROOT / "graphics" / "icons" / pattern.format(f=family)
            upstream = original_icon(zf, pattern.format(f=parent))
            if family not in ORIGINAL_FAMILIES:
                upstream, ratio = isolate_inclusions(
                    upstream, family,
                    standard_recipe=(pattern == "{f}-asteroid-crushing.png"),
                )
                counts.setdefault(family, []).append(ratio)
            changes += int(emit(upstream, dest, args.check))

        for size in SIZES:
            source_name = f"asteroid-{parent}-{size}-colour-01.png"
            target_name = f"asteroid-{family}-{size}-colour-01.png"
            src = open_source(
                zf,
                f"graphics/entity/asteroid/{parent}/{size}/{source_name}",
            )
            dest = ROOT / "graphics" / "entity" / "asteroid" / family / size / target_name
            # The scene uses only the colour diffuse layer. Its corresponding
            # Space Age normal/roughness map must match the chosen source shape.
            if family not in ORIGINAL_FAMILIES:
                src, ratio = isolate_inclusions(src, family)
                counts.setdefault(family, []).append(ratio)
            changes += int(emit(src, dest, args.check))

    for family, ratios in counts.items():
        print(f"{family}: selected-pigment coverage {min(ratios):.1%}–{max(ratios):.1%}; "
              "all other pixels preserved from original sprites")
    print(f"Finished: {changes} changed graphics files")


if __name__ == "__main__":
    main()
