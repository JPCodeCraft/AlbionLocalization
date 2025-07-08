import json
from typing import Dict, List, Union, Any

# Constants
EXCLUDE_ITEMS = ["@xmlns:xsi", "@xsi:noNamespaceSchemaLocation", "crystalleagueitem"]

KEEP_FIELDS = [
    "@uniquename", "@shopcategory", "@shopsubcategory1", "@shopsubcategory2", "@shopsubcategory3", "@craftingcategory", "@resourcetype",
    "@baselootamount", "@famevalue", "@itemvalue", "@tier", "@weight", "@durability",
    "@enchantmentlevel", "craftingrequirements", "@destinycraftfamefactor", "famefillingmissions",
    "lootlist", "@maxfame", "enchantments", "@itempower", "@combatspecachievement",
    "@maxqualitylevel", "@slottype", "harvest", "@foodcategory", "@nutrition", "@twohanded",
    "@placefame", "@kind", "@activefarmfocuscost", "@activefarmmaxcycles",
    "@activefarmactiondurationseconds", "@activefarmcyclelengthseconds", "@activefarmbonus",
    "grownitem", "consumption", "products", "@unlockedtoplace", "@unlockedtocraft", "craftingspelllist", "@transformation"
]

def ensure_array(value: Union[Dict, List]) -> List:
    """Convert single object to array if needed."""
    if isinstance(value, dict):
        return [value]
    return value

def filter_fields(item: Dict) -> Dict:
    """Keep only the specified fields in an item."""
    return {k: v for k, v in item.items() if k in KEEP_FIELDS}

def process_items(data: Dict, transformations_data: Dict) -> Dict:
    # Create a lookup for transformations by uniquename
    all_transformations = {}
    if 'transformations' in transformations_data:
        trans_root = transformations_data.get('transformations', {})
        transformation_list = ensure_array(trans_root.get('transformation', []))
        passive_list = ensure_array(trans_root.get('passivetransformation', []))
        for t in transformation_list + passive_list:
            if '@uniquename' in t:
                all_transformations[t['@uniquename']] = t

    # Remove excluded items
    items = {k: v for k, v in data['items'].items() if k not in EXCLUDE_ITEMS}
    
    # Process each category
    processed_items = {}
    for key, value in items.items():
        if key == "shopcategories":
            processed_items[key] = value
        else:
            # Ensure value is an array
            items_array = ensure_array(value)
            processed_list = []
            for item in items_array:
                # Handle transformations
                if '@transformation' in item:
                    trans_name = item['@transformation']
                    if trans_name in all_transformations:
                        transformation = all_transformations[trans_name]
                        transformation_spells = []
                        
                        # Process active spells
                        if 'spells' in transformation and 'spell' in transformation['spells']:
                            spells = ensure_array(transformation['spells']['spell'])
                            for spell in spells:
                                spell_info = {'@uniquename': spell.get('@uniquename')}
                                if '@slot' in spell:
                                    spell_info['@slot'] = spell.get('@slot')
                                transformation_spells.append(spell_info)
                        
                        # Process passive spells
                        if 'passivespells' in transformation and 'passivespell' in transformation['passivespells']:
                            passives = ensure_array(transformation['passivespells']['passivespell'])
                            for passive in passives:
                                spell_info = {'@uniquename': passive.get('@uniquename')}
                                if '@slot' in passive:
                                    spell_info['@slot'] = passive.get('@slot')
                                transformation_spells.append(spell_info)

                        if transformation_spells:
                            if 'craftingspelllist' not in item:
                                item['craftingspelllist'] = {}
                            item['craftingspelllist']['transformationspell'] = transformation_spells
                
                processed_list.append(filter_fields(item))
            processed_items[key] = processed_list
    
    return processed_items
