# First-public-release verification

Candidate ZIP: `dist/razi-more-asteroids_1.2.0.zip`
Status: **package-ready, engine validation pending**. Do not claim a completed in-game test until performed.

## Packaging gate

Build with the `git archive` command in README.md, using only the explicitly listed Factorio files. Check the ZIP root is `razi-more-asteroids_1.2.0/` and that `unzip -l` shows no `.exe`, `.bat`, `.ps1`, `.sh`, or `.py` entries. The development repository includes a Python art generator, but the release archive must exclude it. This packaging check is not an in-game test.

## Required manual startup tests

- [ ] Confirm **razi_lib >= 1.3.1** is installed and Factorio recognizes it as a required dependency.

- [ ] Factorio **2.1.20+ with Space Age and RaziLib only**, clean mod configuration: reaches main menu with no prototype errors.
- [ ] New Space Age game: eight themed families populate the vanilla routes, no duplicate/prototype errors.
- [ ] Space Age Dense-Metal basic/advanced crushing yields tungsten; processing works in a fluid-equipped crusher.
- [ ] Repeat loading and crafting with **Krastorio2-spaced-out 2.0.17+** installed alongside RaziLib.
- [ ] Confirm all **eight** optional K2SO orbital recipes appear after Advanced Asteroid Processing and have functional ingredients, inputs and outputs.
- [ ] K2SO ground crusher handles dry recipes. **Wet recipes must not appear** in dry-only K2SO machine selections.
- [ ] Inspect a physical space platform's crusher fluid inputs and outputs (including uranium, chemicals, and extra K2SO recipes).
- [ ] Test optional **K2SO Recovery = Off**: specialty recipes absent; basic Dense-Metal tungsten outputs still work.
- [ ] Test **Space Age routes = Off**: family prototypes still exist; extra location/route populations do not.
- [ ] Optional: load with Null's K2SO Tweaks and Any Planet Start, if installed, and check that nothing resets their fields.
- [ ] Inspect all 56 UI icons, 40 in-world sprites, and 144px thumbnail in-game; check all eight asteroid families for missing graphics.
- [ ] Confirm source-based asteroid textures keep their natural colours in-game, with no coloured fill-light wash; the three custom families should have only small mineral accents.
- [ ] Confirm the rendered basic/advanced recipe icons show the actual output item/fluid colours, and their crushing arrows are unaffected.
- [ ] Verify a saved game can be reopened; back up any existing save with Crystalline prototypes now displayed as Dense-Metal and changed outputs.
- [ ] Validate science progression and reasonable availability without unlocking high-tier resources too early.


## New processing and compatibility tests (1.2.0)

- [ ] Inspect all 16 custom crushing/advanced crushing recipe icons and all 8 new reprocessing icons. Distinct materials must use their actual, untinted sprite colors.
- [ ] Research Asteroid reprocessing and confirm eight custom recipes are unlocked in the native crusher without replacing the vanilla three.
- [ ] Test one reprocessing recipe over many crafts: the return/alternative/loss rates approximate 40/20/20/20, with **at most one chunk** output per craft.
- [ ] Confirm reprocessing never accepts productivity or quality modules, and doesn't create material or quality loops.
- [ ] Load with Muluna 2.5.0+ and Quality: confirm eight additional Muluna Asteroid upcycling recipes appear under the **existing** technology and use astronomical-data fluid in Crusher 2.
- [ ] Verify Muluna upcycling consumes 1 astronomical data except Dense-Metal, Halide and Electrostatic (2 data). Its normal output retains quality, upgraded output gains exactly one level, and the 50% loss is still present.
- [ ] Repeat Muluna tests with Rigor installed and confirm the cloned Muluna quality chance and Rigor metadata match the template.
- [ ] Load **without Muluna**, and **without Quality** where supported, to confirm none of its upcycling content appears and the mod still starts normally.
- [ ] Repeat with Muluna + K2SO, watch for recipe conflicts/hidden outputs, and compare optional K2SO icons with actual recipe products.

## Publication procedure

1. Complete the packaging gate and manual tests above.
2. If a prototype, crafting or sprite issue appears, fix it and **bump the patch version** before uploading.
3. Open [Factorio Mod Portal](https://mods.factorio.com/), create the new mod using the prepared ZIP, and copy the text from `docs/MOD_PORTAL.md`.
4. Set the license to **MIT**, link the repository, and use the existing 144px thumbnail.
5. Add screenshots captured **from Factorio** with the new asteroid types and representative processing recipes. Do not substitute generated concept art for in-game screenshots.
6. Publish only after the checks pass, then verify the mod listing and downloaded ZIP.

## Deliberate integration boundary

RP3 owns its custom planet routes, quality escalation, difficulty presets and journal entries. None of these are release requirements or should be built into this standalone mod.
