# Asteroid artwork: original source, targeted mineral details

Source: **spartanlaser32/More-Asteroids**, commit
`ba209beccc0ad363a155e8ced0e3967f2997d500`, credited under the root MIT
licence. Reuse the real sprites. Never redraw the art with generative images,
apply full-image hue/saturation filters, or alter transparent silhouettes.

## Material identity

| Family | Source diffuse/geometry | What changes |
| --- | --- | --- |
| Chemical | Original chemical | Nothing; upstream restored |
| Organic | Original organic | Nothing; upstream restored |
| Rock | Original rock | Nothing; upstream restored |
| Scrap | Original scrap | Nothing; upstream restored |
| Uranium | Original uranium | Nothing; upstream restored |
| Crystalline (Dense-Metal) | Original rock | Subtle blue-grey deposits on exposed cool mineral facets |
| Halide | Original chemical | Muted lilac accents on selected salt/mineral seams |
| Electrostatic | Original scrap | Subtle blue-violet accents on selected rust/conductor inclusions |

Crystalline uses the **metallic** Space Age normal/roughness map (rock geometry);
Halide uses **oxide** (chemical geometry); Electrostatic uses **metallic**
(scrap geometry). The five upstream families retain upstream neutral/warm lighting.
The new families inherit their source family's lighting and shading.
**Never illuminate an entire asteroid blue/green/purple to distinguish its type.**

## Safety boundaries

- Maintain 56 native 64×64 UI icons and 40 asteroid colour sprites with their
  current filenames and dimensions.
- Original source-family art is pixel-identical to upstream (first 64×64
  mip from upstream's 120×64 icon strips).
- For new families, edit only pixels selected within *actual asteroid material*.
  Keep changes to approximately 6–8% of world-sprite body pixels and at most
  11–12.5% of eligible icon body pixels.
- Standard crushing: protect the complete crusher-arrow region, **including
  the grey arrows**, with geometry-based exclusions; do not identify arrows
  only by yellow pigment.
- Advanced crushing: protect the additional debris and output fragments.
- Never alter alpha or pixels outside the material-selection mask. Preserve
  existing microtexture, normal/roughness maps and lighting geometry.
- Dynamic recipe icons in `prototypes/compat/recipe_icons.lua` present the
  *actual* product icon colours and may override baked crushing PNGs in-game.

## Rebuilding and verifying

Developer requirements: Python, Pillow and NumPy (the graphics audit used
Pillow 11.3.0 and NumPy 2.3.3).

```sh
python scripts/restore-material-art.py
python scripts/restore-material-art.py --verify
```

The generator fetches the pinned upstream revision and deterministically
reconstructs the PNGs. `--verify` fails if any committed sprite differs.
A successful one-off CI audit also parses Lua and validates icon dimensions and
transparency. This is **not** a substitute for in-game Factorio visual testing.

Scripts are allowed in the development repository but are **excluded from
release ZIPs**, using the explicit `git archive` allowlist in README.md.
