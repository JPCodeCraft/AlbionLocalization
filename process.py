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
processed_data = process_localization(data)  # Now calls the function directly

# Save processed localization to merged_localization.json
with open("merged_localization.json", "w", encoding="utf-8") as file:
    json.dump(processed_data, file, separators=(',', ':'), ensure_ascii=False)