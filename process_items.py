import json
from collections import defaultdict
from typing import Any, DefaultDict, Dict, List, Set, Union

# Constants
EXCLUDE_ITEMS = ["@xmlns:xsi", "@xsi:noNamespaceSchemaLocation", "crystalleagueitem"]

KEEP_FIELDS = [
    '@dontgivefameoncraft',
    "@uniquename", "@abilitypower", "@namelocatag", "@uisprite", "@shopcategory", "@shopsubcategory1", "@shopsubcategory2", "@shopsubcategory3", "@craftingcategory", "@resourcetype",
    "@baselootamount", "@famevalue", "@itemvalue", "@tier", "@weight", "@fasttravelfactor", "@durability",
    "@enchantmentlevel", "craftingrequirements", "@destinycraftfamefactor", "famefillingmissions",
    "lootlist", "@maxfame", "enchantments", "@itempower", "@combatspecachievement",
    "@maxqualitylevel", "@slottype", "harvest", "@foodcategory", "@nutrition", "@twohanded", "@showinmarketplace",
    "@placefame", "@kind", "@activefarmfocuscost", "@activefarmmaxcycles",
    "@activefarmactiondurationseconds", "@activefarmcyclelengthseconds", "@activefarmbonus",
    "grownitem", "consumption", "products", "@unlockedtoplace", "@unlockedtocraft", "craftingspelllist", "mountspelllist", "@transformation", "@masterymodifier",
    "@consumespell", "@maxstacksize"
]

BLACK_MARKET_ENCHANTMENTS_FIELD = "@blackmarketenchantments"


def ensure_array(value: Union[Dict, List]) -> List:
    """Convert single object to array if needed."""
    if isinstance(value, dict):
        return [value]
    return value

def filter_fields(item: Dict) -> Dict:
    """Keep only the specified fields in an item."""
    return {k: v for k, v in item.items() if k in KEEP_FIELDS}


def _parse_enchantment_level(value: Any, context: str) -> int:
    """Parse a non-negative integer enchantment level or fail with context."""
    if isinstance(value, bool):
        raise ValueError(f"Invalid enchantment level at {context}: {value!r}")

    if isinstance(value, int):
        level = value
    elif isinstance(value, str) and value.isdigit():
        level = int(value)
    else:
        raise ValueError(f"Invalid enchantment level at {context}: {value!r}")

    if level < 0:
        raise ValueError(f"Invalid enchantment level at {context}: {value!r}")

    return level


def _collect_black_market_enchantments(loot_data: Any) -> Dict[str, List[int]]:
    """Recursively collect and deduplicate exact Black Market item variants."""
    levels_by_item: DefaultDict[str, Set[int]] = defaultdict(set)

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            if node.get("@useblackmarket") in ("true", True):
                item_name = node.get("@type")
                if not isinstance(item_name, str) or not item_name:
                    raise ValueError(
                        f"Black Market marker at {path} has no valid @type"
                    )

                level = _parse_enchantment_level(
                    node.get("@enchantmentlevel", "0"),
                    f"{path}.@enchantmentlevel",
                )
                levels_by_item[item_name].add(level)

            for key, value in node.items():
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")

    walk(loot_data, "loot")

    if not levels_by_item:
        raise ValueError("No Black Market item markers were found in loot data")

    return {
        item_name: sorted(levels)
        for item_name, levels in levels_by_item.items()
    }


def add_black_market_enchantments(items: Dict, loot_data: Any) -> Dict:
    """Annotate processed base items with their exact Black Market levels."""
    processed_items_by_name: Dict[str, Dict] = {}
    available_levels_by_name: Dict[str, Set[int]] = {}

    for category, category_items in items.items():
        if category == "shopcategories":
            continue
        if not isinstance(category_items, list):
            raise ValueError(
                f"Processed item category {category!r} must be an array"
            )

        for index, item in enumerate(category_items):
            context = f"{category}[{index}]"
            if not isinstance(item, dict):
                raise ValueError(f"Processed item at {context} must be an object")

            item_name = item.get("@uniquename")
            if not isinstance(item_name, str) or not item_name:
                raise ValueError(
                    f"Processed item at {context} has no valid @uniquename"
                )
            if item_name in processed_items_by_name:
                raise ValueError(f"Duplicate processed item @uniquename: {item_name}")

            item.pop(BLACK_MARKET_ENCHANTMENTS_FIELD, None)
            processed_items_by_name[item_name] = item

            available_levels = {
                _parse_enchantment_level(
                    item.get("@enchantmentlevel", "0"),
                    f"{context}.@enchantmentlevel",
                )
            }
            enchantments = item.get("enchantments")
            if enchantments is not None:
                if not isinstance(enchantments, dict):
                    raise ValueError(
                        f"Processed enchantments at {context} must be an object"
                    )
                enchantment_entries = ensure_array(
                    enchantments.get("enchantment", [])
                )
                for enchantment_index, enchantment in enumerate(
                    enchantment_entries
                ):
                    enchantment_context = (
                        f"{context}.enchantments.enchantment[{enchantment_index}]"
                    )
                    if not isinstance(enchantment, dict):
                        raise ValueError(
                            f"Processed enchantment at {enchantment_context} "
                            "must be an object"
                        )
                    if "@enchantmentlevel" not in enchantment:
                        raise ValueError(
                            f"Processed enchantment at {enchantment_context} "
                            "has no @enchantmentlevel"
                        )
                    available_levels.add(
                        _parse_enchantment_level(
                            enchantment["@enchantmentlevel"],
                            f"{enchantment_context}.@enchantmentlevel",
                        )
                    )

            available_levels_by_name[item_name] = available_levels

    black_market_levels_by_name = _collect_black_market_enchantments(loot_data)
    for item_name, black_market_levels in black_market_levels_by_name.items():
        item = processed_items_by_name.get(item_name)
        if item is None:
            raise ValueError(
                f"Black Market marker references unknown item: {item_name}"
            )

        available_levels = available_levels_by_name[item_name]
        unsupported_levels = [
            level
            for level in black_market_levels
            if level not in available_levels
        ]
        if unsupported_levels:
            raise ValueError(
                f"Black Market marker for {item_name} references unsupported "
                f"enchantment levels {unsupported_levels}; available levels are "
                f"{sorted(available_levels)}"
            )

        item[BLACK_MARKET_ENCHANTMENTS_FIELD] = black_market_levels

    return items


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
