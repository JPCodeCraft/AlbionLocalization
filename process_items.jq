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
def filterFields:
  with_entries(select(.key as $key | keepFields | index($key) != null));

# Normalize items to always be arrays
def normalizeItems:
  if type == "object" then [.] else . end;

# Main processing logic
.items 
| del(.. | select(type == "object" and . != null and (keys[] as $k | excludeItems | index($k))))
| to_entries
| map(.value |= normalizeItems)
| map(.value |= map(if type == "object" then filterFields else . end))
| from_entries