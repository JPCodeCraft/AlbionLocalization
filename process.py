import json
from process_items import process_items
from process_localization import process_localization

# Load items.json
with open("items.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    
# Process items
processed_data = process_items(data)

# Save processed items to processed_items.json
with open("processed_items.json", "w", encoding="utf-8") as file:
    json.dump(processed_data, file, separators=(',', ':'), ensure_ascii=False)
    

# Load localization.json
with open("localization.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    
# Process localization
processed_data = process_localization(data)

# Save processed localization to merged_localization.json
with open("merged_localization.json", "w", encoding="utf-8") as file:
    json.dump(processed_data, file, separators=(',', ':'), ensure_ascii=False)
    
    
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
    if 'harvest' not in item:
        continue
    loot_list_name = item['harvest']['@lootlist']
    matched_loot = find_loot_by_name(loot, loot_list_name)
    
    if matched_loot is None:
        print(f"Warning: No loot found for {loot_list_name}")
        continue
        
    item['harvest']['@lootlist'] = matched_loot
    
# Save items with loot to processed_items.json
with open("processed_items.json", "w", encoding="utf-8") as file:
    json.dump(items, file, separators=(',', ':'), ensure_ascii=False)