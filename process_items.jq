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

# Main processing logic
.items
| with_entries(select(.key as $key | excludeItems | index($key) | not))
| .[] | filterFields(.)