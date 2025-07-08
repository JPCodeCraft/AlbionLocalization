import json
from process_items import process_items
from process_localization import process_localization
from process_spells import process_spells

# MARK: Items
# Load items.json
with open("items.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Load transformations data
with open('transformations.json', 'r', encoding='utf-8') as f:
    transformations_data = json.load(f)
    
# Process items
processed_data = process_items(data, transformations_data)

# Save processed items to processed_items.json
with open("processed_items.json", "w", encoding="utf-8") as file:
    json.dump(processed_data, file, separators=(',', ':'), ensure_ascii=False)
    
# MARK: Spells
# Load spells.json
with open("spells.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Process spells
processed_data = process_spells(data)

# Save processed spells to processed_spells.json
with open("processed_spells.json", "w", encoding="utf-8") as file:
    json.dump(processed_data, file, separators=(',', ':'), ensure_ascii=False)
    
# MARK: Localization
# Load localization.json
with open("localization.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    
# Process localization
processed_data = process_localization(data)

# Save processed localization to merged_localization.json
with open("merged_localization.json", "w", encoding="utf-8") as file:
    json.dump(processed_data, file, separators=(',', ':'), ensure_ascii=False)
    
# MARK: Loot
# Load loot.json
with open("loot.json", "r", encoding="utf-8") as file:
    loot = json.load(file)
    
# Load processed_items.json
with open("processed_items.json", "r", encoding="utf-8") as file:
    items = json.load(file)
    
# For each item that has the property ['harvest']['@lootlist'], add the loot to the item
def find_loot_by_name(loot_data, loot_name):
    """Find loot configuration by name in loot data."""
    for loot_entry in loot_data["LootDefinition"]["Lootlist"]:
        if loot_entry.get('@name') == loot_name:
            return loot_entry
    return None

for item in items['farmableitem']:
            
    if 'harvest' in item:
        harvest_loot_list_name = item['harvest'].get('@lootlist')
        if harvest_loot_list_name:
            harvest_matched_loot = find_loot_by_name(loot, harvest_loot_list_name)
            if harvest_matched_loot is None:
                print(f"Warning: No loot found for {harvest_loot_list_name}")
                continue
            item['harvest']['@lootlist'] = harvest_matched_loot
            
    if 'products' in item:
        products = item.get('products', {})
        product = products.get('product', {})
        products_loot_list_name = product.get('@lootlist')
        if products_loot_list_name:
            products_matched_loot = find_loot_by_name(loot, products_loot_list_name)
            if products_matched_loot is None:
                print(f"Warning: No loot found for {products_loot_list_name}")
                continue
            item['products']['product']['@lootlist'] = products_matched_loot
    
# Save items with loot to processed_items.json
with open("processed_items.json", "w", encoding="utf-8") as file:
    json.dump(items, file, separators=(',', ':'), ensure_ascii=False)