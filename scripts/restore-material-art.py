#!/usr/bin/env python3
"""Restore the upstream material artwork while preserving Razi-only asteroid shapes.

Source: spartanlaser32/More-Asteroids (MIT), pinned to a reviewed revision.
Only colour sprites/icons are changed. Never modify normal or roughness maps.
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path
import urllib.request
import zipfile
import zlib

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_COMMIT = "ba209beccc0ad363a155e8ced0e3967f2997d500"
ORIGINAL_ZIP = (
    "https://codeload.github.com/spartanlaser32/More-Asteroids/zip/"
    + ORIGINAL_COMMIT
)
FORK_BASE_ZIP = (
    "https://codeload.github.com/Raziphel/Razi-More-Asteroids/zip/"
    "57cf549e9a3db9694cc733e37a4310dc83cd5302"
)
RESTORED = ("chemical", "organic", "rock", "scrap", "uranium")
CUSTOM = ("crystalline", "electrostatic", "halide")
# Dark matrix, main mineral, secondary inclusion, and a sparing bright inclusion.
PALETTES = {
    "crystalline": (
        (93, 109, 119), (187, 203, 213), (112, 169, 209), (228, 229, 218)
    ),
    "electrostatic": (
        (70, 80, 103), (82, 137, 193), (161, 110, 184), (141, 220, 211)
    ),
    "halide": (
        (92, 91, 110), (179, 168, 215), (136, 187, 202), (223, 219, 206)
    ),
}


def upstream_archive(url: str = ORIGINAL_ZIP) -> zipfile.ZipFile:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Razi-More-Asteroids-art-refresh"}
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        payload = response.read(25_000_001)
    if len(payload) > 25_000_000:
        raise ValueError("Unexpected upstream archive size")
    return zipfile.ZipFile(io.BytesIO(payload))


def image_from_zip(zf: zipfile.ZipFile, path: str) -> Image.Image:
    found = [name for name in zf.namelist() if name.endswith("/" + path)]
    if len(found) != 1:
        raise FileNotFoundError(f"Expected one upstream copy of {path}, got {found}")
    return Image.open(io.BytesIO(zf.read(found[0]))).convert("RGBA")


def save_if_changed(image: Image.Image, dest: Path) -> bool:
    image = image.convert("RGBA")
    if dest.exists():
        with Image.open(dest) as previous:
            if previous.size == image.size and previous.convert("RGBA").tobytes() == image.tobytes():
                return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest, "PNG", optimize=True)
    print("updated", dest.relative_to(ROOT))
    return True


def strip_mipmap_strip(im: Image.Image) -> Image.Image:
    # Original icon PNGs are 120x64 (64 + 32 + 16 + 8 mipmap strip).
    # The fork's prototype files point to regular 64x64 single-mip icons.
    if im.size == (120, 64):
        return im.crop((0, 0, 64, 64))
    if im.size == (64, 64):
        return im
    raise ValueError(f"Unexpected source icon dimensions: {im.size}")


def texture_noise(width: int, height: int, seed: int, cell: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    low = rng.integers(
        0, 256, (max(3, height // cell), max(3, width // cell)),
        dtype=np.uint8
    )
    smooth = Image.fromarray(low, "L").resize(
        (width, height), Image.Resampling.BICUBIC
    )
    return np.asarray(smooth, dtype=np.float32) / 255.0


def repigment(im: Image.Image, family: str, key: str, is_icon: bool) -> Image.Image:
    """Recolour the surfaces using several mineral pigments, not a hue overlay.

    Spatially coherent patches expose dark rock, bright crystals and inclusions.
    The old image supplies facet structure, occlusion, silhouettes and alpha.
    """
    rgba = np.asarray(im.convert("RGBA"), dtype=np.uint8).copy()
    height, width, _ = rgba.shape
    original = rgba[:, :, :3].astype(np.float32)
    lum = original @ np.array([0.24, 0.67, 0.09], dtype=np.float32)
    seed = zlib.crc32((family + ":" + key).encode("utf-8"))
    patches = texture_noise(width, height, seed, 10 if is_icon else 22)
    veins = texture_noise(width, height, seed ^ 0xA59F32D1, 4 if is_icon else 8)
    pigment = np.empty_like(original)
    colors = [np.array(c, dtype=np.float32) for c in PALETTES[family]]
    pigment[:] = colors[0]
    pigment[patches > 0.48] = colors[1]
    pigment[(patches > 0.61) & (veins > 0.42)] = colors[2]
    pigment[(patches > 0.72) & (veins > 0.66) & (lum > 82)] = colors[3]

    # Respect source shading: lower luminance stays in shadow; bright areas shine.
    surface_light = np.clip(0.30 + lum / 260.0, 0.34, 1.05)
    mineral = pigment * surface_light[:, :, None]
    # Keep a portion of the existing material's facet colour and shading.
    result = 0.31 * original + 0.69 * mineral
    rgba[:, :, :3] = np.clip(result, 0, 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def refresh_custom_icon(
    current: Image.Image,
    family: str,
    filename: str,
    arrow_reference: Image.Image,
) -> Image.Image:
    output = repigment(current, family, filename, is_icon=True)
    if filename.endswith("-crushing.png") and not filename.startswith("advanced-"):
        arr = np.asarray(output).copy()
        upstream = np.asarray(arrow_reference)
        y = np.arange(64)[:, None]
        # The upstream's actual warm-gold crushing chevrons, not a recoloured rock.
        arrow_pixels = (
            (y > 23)
            & (upstream[:, :, 0] > 145)
            & (upstream[:, :, 1] > 95)
            & (upstream[:, :, 2] < 125)
            & (upstream[:, :, 3] > 40)
            & (arr[:, :, 3] > 40)
        )
        arr[arrow_pixels, :3] = upstream[arrow_pixels, :3]
        output = Image.fromarray(arr, "RGBA")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Report edits, don't write them")
    args = parser.parse_args()
    zf = upstream_archive()
    # The pre-overhaul fork snapshot is used for every custom-family pass.
    # This makes reruns idempotent, rather than layering repeated colour edits.
    fork_zf = upstream_archive(FORK_BASE_ZIP)
    changes = 0
    icons = ROOT / "graphics" / "icons"
    entity_root = ROOT / "graphics" / "entity" / "asteroid"
    standard_arrow = strip_mipmap_strip(
        image_from_zip(zf, "graphics/icons/chemical-asteroid-crushing.png")
    )

    # For five upstream families, prefer the original high-detail material pixels.
    # All size tiers and both recipe icons are included, not merely the chunk.
    for family in RESTORED:
        for path in sorted(icons.glob("*.png")):
            if path.name.endswith(f"-{family}-asteroid.png") or (
                path.name in (f"{family}-asteroid-chunk.png",
                              f"{family}-asteroid-crushing.png",
                              f"advanced-{family}-asteroid-crushing.png")
            ):
                original = strip_mipmap_strip(
                    image_from_zip(zf, "graphics/icons/" + path.name)
                )
                if args.check:
                    print("would restore", path.relative_to(ROOT))
                else:
                    changes += save_if_changed(original, path)
        for path in sorted((entity_root / family).rglob("*-colour-*.png")):
            rel = path.relative_to(ROOT).as_posix()
            original = image_from_zip(zf, rel)
            with Image.open(path) as current:
                if original.size != current.size:
                    raise ValueError(f"Colour layer dimensions mismatch: {rel}")
            if args.check:
                print("would restore", rel)
            else:
                changes += save_if_changed(original, path)

    # Custom families have their own asteroid silhouettes. Retain those images
    # and add contrasting mineral inclusions rather than replacing their shapes.
    for family in CUSTOM:
        for path in sorted(icons.glob("*.png")):
            if not (
                path.name.endswith(f"-{family}-asteroid.png")
                or path.name in (f"{family}-asteroid-chunk.png",
                                 f"{family}-asteroid-crushing.png",
                                 f"advanced-{family}-asteroid-crushing.png")
            ):
                continue
            original = image_from_zip(fork_zf, path.relative_to(ROOT).as_posix())
            result = refresh_custom_icon(original, family, path.name, standard_arrow)
            if args.check:
                print("would retouch", path.relative_to(ROOT))
            else:
                changes += save_if_changed(result, path)
        for path in sorted((entity_root / family).rglob("*-colour-*.png")):
            original = image_from_zip(fork_zf, path.relative_to(ROOT).as_posix())
            result = repigment(original, family, path.name, is_icon=False)
            if args.check:
                print("would retouch", path.relative_to(ROOT))
            else:
                changes += save_if_changed(result, path)

    print(f"Graphics refresh complete: {changes} updated files")
    # An unchanged second run is valid: all renders are derived from pinned inputs.


if __name__ == "__main__":
    main()
