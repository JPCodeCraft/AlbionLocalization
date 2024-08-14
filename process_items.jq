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

# Normalize items to always be arrays and convert strings/numbers to objects
def normalizeItems:
  if type == "object" then [.]
  elif type == "string" or type == "number" then [{value: .}]
  else . end;

# Main processing logic
.items 
| to_entries
| map(.value |= normalizeItems)
| del(.. | select(keys[] as $k | excludeItems | index($k)))
| map(.value |= filterFields)
| from_entries