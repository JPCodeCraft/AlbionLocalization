import json
from typing import Dict, List, Union, Any

# Constants
EXCLUDE_ITEMS = ["@xmlns:xsi", "@xsi:noNamespaceSchemaLocation", "crystalleagueitem"]

KEEP_FIELDS = [
    "@uniquename", "@shopcategory", "@shopsubcategory1", "@shopsubcategory2", "@shopsubcategory3", "@craftingcategory", "@resourcetype",
    "@baselootamount", "@famevalue", "@itemvalue", "@tier", "@weight", "@durability",
    "@enchantmentlevel", "craftingrequirements", "@destinycraftfamefactor", "famefillingmissions",
    "lootlist", "@maxfame", "enchantments", "@itempower", "@combatspecachievement",
    "@maxqualitylevel", "@slottype", "harvest", "@foodcategory", "@nutrition",
    "@placefame", "@kind", "@activefarmfocuscost", "@activefarmmaxcycles",
    "@activefarmactiondurationseconds", "@activefarmcyclelengthseconds", "@activefarmbonus",
    "grownitem", "consumption", "products", "@unlockedtoplace", "@unlockedtocraft"
]

def ensure_array(value: Union[Dict, List]) -> List:
    """Convert single object to array if needed."""
    if isinstance(value, dict):
        return [value]
    return value

def filter_fields(item: Dict) -> Dict:
    """Keep only the specified fields in an item."""
    return {k: v for k, v in item.items() if k in KEEP_FIELDS}

def process_items(data: Dict) -> Dict:
    # Remove excluded items
    items = {k: v for k, v in data['items'].items() if k not in EXCLUDE_ITEMS}
    
    # Process each category
    processed_items = {}
    for key, value in items.items():
        if key == "shopcategories":
            processed_items[key] = value
        else:
            # Ensure value is an array and filter fields
            items_array = ensure_array(value)
            processed_items[key] = [filter_fields(item) for item in items_array]
    
    return processed_items
