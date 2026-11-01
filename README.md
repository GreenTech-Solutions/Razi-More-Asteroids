# Razi More Asteroids

A Factorio **2.1 Space Age** mod with **eight distinct asteroid families** using updated versions of the original More Asteroids graphics. Based on the MIT-licensed original by spartanlaser32.

**Requires:** Space Age 2.1.20+ and [RAZI Library](https://mods.factorio.com/mod/razi_lib) 1.3.1+. **Optional:** Krastorio 2: Spaced Out (K2SO) 2.0.17+ and Muluna 2.5.0+ (with Quality). Does not require Razi Protocol.

## Eight orbital resources

| In-game identity | Basic extraction | Advanced extraction | K2SO integration |
| --- | --- | --- | --- |
| Radioactive | Uranium ore | Uranium isotopes | Uranium processing chain |
| Lithic | Stone | Stone + calcite | K2SO stone/sand/glass processing |
| Dense-Metal | Tungsten ore | More tungsten | Raw rare-metal ore, acid leaching |
| Wreckage | Fulgora scrap | Consistent scrap recovery | Electronic components and inserter-part salvage |
| Biogenic | Spoilage | Nutrient-fed biological recovery | Biomass processing |
| Volatile | Ammonia | More ammonia | Hydrogen and oxygen extraction |
| Halide | Fluorine | Fluorine + lithium brine | Mineral water and sulfur recovery |
| Electrostatic | Holmium ore | More holmium | K2SO silicon and conductor recovery |

These are eight *new asteroid families* relative to vanilla Space Age's Metallic, Carbonic, Oxide and Promethium asteroids. No fictional lens factories or extra materials are needed.

**Existing-save compatibility:** the six established prototype IDs (`uranium`, `rock`, `scrap`, `organic`, `chemical`, `crystalline`) remain unchanged, but their displayed identities and outputs have changed. Dense-Metal uses the former Crystalline ID. Halide and Electrostatic add entirely new prototype IDs. Back up existing games and review production lines before updating.

## Game progression and locations

Families appear in themed densities across native Space Age routes and vanilla planet orbits, with additional hazards on outer-system routes. Dense-Metal requires Vulcanus discovery to process tungsten; Electrostatic requires Fulgora discovery to process holmium; Halide and Volatile require Aquilo discovery for their chemical products. Custom RP3 planet routes and asteroid quality are handled by RP3, not this mod.

Existing vanilla and third-party asteroid spawn entries are preserved and duplicate records are avoided. Space Age's base asteroid types are not replaced.

## Deeper K2SO integration

K2SO expands processing without replacing its normal industry or providing free tech cards:

- Dense-Metal: raw rare-metal ore separation and acid-based ore leaching.
- Wreckage: salvage electronic components and inserter parts.
- Biogenic: recover biomass using nutrients.
- Volatile: wash volatile chunks for hydrogen or oxygen.
- Halide: mineral-water extraction and sulfur separation.
- Electrostatic: acid-based recovery of holmium and K2SO silicon.
- Lithic: yields stone for the existing K2SO mineral/glass lines.
- Radioactive: uranium and isotope products for the existing nuclear chain.

All eight optional specialty recipes require valid K2SO prototypes and the relevant processing research. Dry recipes can run in compatible K2SO crushers; wet recipes remain in fluid-capable crushers. The mod does not modify K2SO's own recipe balances.

## Processing that matches Space Age

**Reprocessing:** all eight custom families can be reprocessed once the vanilla **Asteroid reprocessing** technology is researched. Each recipe uses the same exclusive outcomes as vanilla: 40% to keep the input chunk, 20% for either of two thematically related families, and 20% loss. Reprocessing does not create extra materials, use productivity, or permit quality modules. It does not replace Space Age's original three reprocessing recipes.

**Muluna upcycling:** when `planet-muluna` and Quality are both installed, all eight custom chunks become valid targets for Muluna's **Asteroid upcycling** research. The new recipes consume the existing astronomical-data fluid and use Muluna's own Crusher 2, quality rolls, loss rate and optional Rigor settings. Dense-Metal, Halide and Electrostatic use 2 astronomical data per craft; other families use 1. No Muluna-only items or recipes appear without Muluna.

**Icons:** crushing, advanced crushing, reprocessing, upcycling and K2SO-specialty recipe icons now composite the actual input-chunk graphic with the full-color icons of the materials returned. Iron stays iron-colored, copper stays copper-colored, and fluid icons keep their own palette. We no longer tint every ingredient the same color as the asteroid.

## Original artwork, selectively restored

The five original asteroid families (Chemical, Organic, Rock, Scrap and Uranium)
use the original More Asteroids artwork, with no global tinting. The three new
families reuse matching original geometry and change only selected asteroid
mineral regions: Crystalline from Rock, Halide from Chemical, and Electrostatic
from Scrap. Crushing arrows, output fragments, transparent backgrounds and
non-selected material pixels retain their original colours.

The 56 icons and 40 asteroid entity colour textures remain at their original
dimensions. Asteroid entities use the matching upstream Space Age normal and
roughness maps **and neutral upstream lighting** so the renderer doesn't tint
the whole asteroid. Recipe icons are layered from real ingredient/product
prototypes at runtime, rather than using monochrome recipe artwork.

The pinned, reproducible art generator is `scripts/restore-material-art.py`.
Run `python scripts/restore-material-art.py` to regenerate PNGs, then
`python scripts/restore-material-art.py --verify` to assert that the committed
graphics match source. This developer-only script must **not** be included in
the Factorio Mod Portal ZIP. See [Asteroid art direction](docs/ART_DIRECTION.md).


## Settings

- **Populate Space Age asteroid routes** (on): add all eight families to vanilla routes and locations.
- **Enable K2SO orbital resource recovery** (on): register eight optional K2SO recovery recipes when K2SO is installed.

## Packaging and release

**Current release: 1.2.1.** This patch restores detailed upstream asteroid textures and corrects full-entity colour casting. Reprocessing, upcycling and other 1.2.0 gameplay features are unchanged.

The repository includes a developer-only Python art generator, but the release ZIP must **exclude** scripts and workflows. Package version 1.2.1 using the explicit allowlist:

```sh
mkdir -p dist
git archive --format=zip --prefix=razi-more-asteroids_1.2.1/ -o dist/razi-more-asteroids_1.2.1.zip HEAD info.json LICENSE changelog.txt thumbnail.png settings.lua data.lua data-updates.lua data-final-fixes.lua asteroids.lua recipe.lua item.lua more-asteroids-spawn-definitions.lua locale graphics prototypes
```

Check the ZIP contents before uploading. Factorio 2.1 in-game load/crafting tests are still required with Space Age + RaziLib, with and without K2SO and Muluna/Quality. In particular, check reprocessing probability, quality upgrades, and the dynamically composed icons. See `docs/RELEASE_CHECKLIST.md`. This repository has not automatically published the mod to the Mod Portal.

## Original credits

Based on [More Asteroids](https://mods.factorio.com/mod/More-Asteroids) by spartanlaser32, originally released under MIT. The upstream license is retained. [Original source repository](https://github.com/spartanlaser32/More-Asteroids).
