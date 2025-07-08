import json
from typing import Dict, List, Union, Any

# Constants
EXCLUDE_ITEMS = ["@xmlns:xsi", "@xsi:noNamespaceSchemaLocation", "colortag"]

KEEP_FIELDS = [
    "@uniquename", "@castingtime", "@recastdelay", "@namelocatag"
]

def ensure_array(value: Union[Dict, List]) -> List:
    """Convert single object to array if needed."""
    if isinstance(value, dict):
        return [value]
    return value

def filter_fields(item: Dict) -> Dict:
    """Keep only the specified fields in an item, and remove @ from the value of @namelocatag."""
    result = {}
    for k, v in item.items():
        if k in KEEP_FIELDS:
            if k == "@namelocatag" and isinstance(v, str) and v.startswith("@SPELLS_"):
                result[k] = v[8:]
            else:
                result[k] = v
    return result

def process_spells(data: Dict) -> List[Dict]:
    # Remove excluded items
    items = {k: v for k, v in data['spells'].items() if k not in EXCLUDE_ITEMS}
    
    # Collect all spells into a flat list
    flat_spells = []
    for key, value in items.items():
        items_array = ensure_array(value)
        for item in items_array:
            spell = filter_fields(item)
            if key == "passivespell":
                spell["@spelltype"] = "passive"
            elif key == "activespell":
                spell["@spelltype"] = "active"
            elif key == "togglespell":
                spell["@spelltype"] = "toggle"
            else:
                spell["@spelltype"] = "undefined"
            flat_spells.append(spell)
    
    return flat_spells
