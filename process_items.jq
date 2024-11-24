# Define the items to exclude
def excludeItems: ["@xmlns:xsi", "@xsi:noNamespaceSchemaLocation", "crystalleagueitem"];

# Define the fields to keep
def keepFields: [
  "@uniquename", "@shopcategory", "@shopsubcategory1", "@craftingcategory", "@resourcetype",
  "@baselootamount", "@famevalue", "@itemvalue", "@tier", "@weight", "@durability",
  "@enchantmentlevel", "craftingrequirements", "@destinycraftfamefactor", "famefillingmissions",
  "lootlist", "@maxfame", "enchantments", "@itempower", "@combatspecachievement",
  "@maxqualitylevel", "@slottype", "harvest",
  "@placefame", "@kind", "@activefarmfocuscost", "@activefarmmaxcycles",
  "@activefarmactiondurationseconds", "@activefarmcyclelengthseconds", "@activefarmbonus"
];

# Remove the excluded items from .items
.items |= with_entries(
    select(.key as $k | excludeItems | index($k) | not)
  )

# If the entry is an object, convert it to an object that has as value an array of objects
| .items | with_entries(
    if .key == "shopcategories" then
      .
    else
      if .value | type == "object" then
        .value = [.value]
      else
        .
      end
    end
  )

| with_entries(
    if .key == "shopcategories" then
      .
    else
      .value |= map(
        with_entries(
          select(.key as $k | keepFields | index($k))
        )
      )
    end
  )
