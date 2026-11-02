-- Space Age standalone compatibility validation.
-- Dense-Metal and other family outputs are finalized by eight_family_recipes.
-- Never import K2SO-only resource names on the standalone path.
local Item = require("__razi_lib__/lib/item")
local recipes = data.raw.recipe or {}
local fluids = data.raw.fluid or {}
-- Protect against other optional mods that replace the normal fluids or
-- items (validation happens after all recipe-stage updates).
local families = {"uranium","rock","scrap","organic","chemical","crystalline","halide","electrostatic"}
for _,family in ipairs(families) do
  for _,prefix in ipairs({"","advanced-"}) do
    local name = prefix .. family .. "-asteroid-crushing"
    local recipe = recipes[name]
    if recipe then
      for _,group in ipairs({"ingredients","results"}) do
        for _,entry in ipairs(recipe[group] or {}) do
          local exists
          if entry.type == "fluid" then exists = fluids[entry.name] else exists = Item.find(entry.name) end
          if not exists then
            error("[Razi More Asteroids] Missing Space Age " .. group ..
              " prototype " .. tostring(entry.name) .. " in recipe " .. name)
          end
        end
      end
    end
  end
end
