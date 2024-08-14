# Define the items to exclude
def excludeItems: ["@xmlns:xsi", "@xsi:noNamespaceSchemaLocation", "crystalleagueitem"];

# Define the fields to keep
def keepFields: [
  "@uniquename", "@shopcategory", "@shopsubcategory1", "@craftingcategory", "@resourcetype",
  "@baselootamount", "@famevalue", "@itemvalue", "@tier", "@weight", "@durability",
  "@enchantmentlevel", "craftingrequirements", "@destinycraftfamefactor", "famefillingmissions",
  "lootlist", "@maxfame", "enchantments", "@itempower", "@combatspecachievement",
  "@maxqualitylevel", "@slottype"
];

# Function to filter fields
def filterFields(item):
  item
  | with_entries(select(.key as $key | keepFields | index($key)));

# Normalize items to always be arrays
def normalizeItems(item):
  if item | type == "object" then
    [item]
  else
    item
  end;

# Main processing logic
.items
| to_entries
| map(
    .value
    | if type == "object" then
        with_entries(select(.key as $key | excludeItems | index($key) | not))
        | normalizeItems(.)
        | map(
            . as $item
            | filterFields(.)
          )
      else
        empty
      end
  )
| flatten