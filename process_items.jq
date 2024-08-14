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
  else . end;

# Main processing logic
.items 
| to_entries
| map(select(.value | has_any(excludeItems[]) | not))
| map(.value |= normalizeItems)
| map(.value |= filterFields)
| from_entries