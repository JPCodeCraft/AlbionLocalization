from typing import Dict, List, Union

# Fields to keep at each level
CATEGORY_FIELDS = [
    "@uniquename", "@displayname", "categoryrewards", "@hideinjournal", 
    "tutorialsubcategory", "subcategory"
]

ITEMREWARD_FIELDS = [
    "@id", "@item", "@percentageofmissionsfinished", "@nextachievementrevealamount"
]

TUTORIAL_SUBCATEGORY_FIELDS = [
    "@uniquename", "@displayname", "tutorialachievement"
]

TUTORIAL_ACHIEVEMENT_FIELDS = [
    "@name", "@questindex", "@quest", "@rewarditem", "@rewardamount", 
    "@absoluteprogressmax", "@symbol", "@expandabledescription"
]

SUBCATEGORY_FIELDS = [
    "@uniquename", "@displayname", "@tutorial", "achievement"
]

ACHIEVEMENT_FIELDS = [
    "@name", "@rewarditem", "@difficultyrating", "@rewardamount"
]


def ensure_array(value: Union[Dict, List, None]) -> List:
    """Convert single object to array if needed."""
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    return value


def filter_fields(item: Dict, fields: List[str]) -> Dict:
    """Keep only the specified fields in an item."""
    return {k: v for k, v in item.items() if k in fields}


def process_itemrewards(itemrewards: Union[Dict, List, None]) -> List[Dict]:
    """Process itemreward entries in categoryrewards."""
    items = ensure_array(itemrewards)
    return [filter_fields(item, ITEMREWARD_FIELDS) for item in items]


def process_categoryrewards(categoryrewards: Dict) -> Dict:
    """Process categoryrewards object."""
    if not categoryrewards:
        return {}
    
    result = {}
    if 'itemreward' in categoryrewards:
        result['itemreward'] = process_itemrewards(categoryrewards['itemreward'])
    return result


def process_achievements(achievements: Union[Dict, List, None]) -> List[Dict]:
    """Process achievement entries."""
    items = ensure_array(achievements)
    return [filter_fields(item, ACHIEVEMENT_FIELDS) for item in items]


def process_tutorial_achievements(achievements: Union[Dict, List, None]) -> List[Dict]:
    """Process tutorialachievement entries."""
    items = ensure_array(achievements)
    return [filter_fields(item, TUTORIAL_ACHIEVEMENT_FIELDS) for item in items]


def process_subcategory(subcategory: Dict) -> Dict:
    """Process a single subcategory."""
    result = filter_fields(subcategory, SUBCATEGORY_FIELDS)
    
    # Process nested achievements
    if 'achievement' in result:
        result['achievement'] = process_achievements(result['achievement'])
    
    return result


def process_subcategories(subcategories: Union[Dict, List, None]) -> List[Dict]:
    """Process subcategory entries."""
    items = ensure_array(subcategories)
    return [process_subcategory(item) for item in items]


def process_tutorial_subcategory(subcategory: Dict) -> Dict:
    """Process a single tutorialsubcategory."""
    result = filter_fields(subcategory, TUTORIAL_SUBCATEGORY_FIELDS)
    
    # Process nested tutorialachievements
    if 'tutorialachievement' in result:
        result['tutorialachievement'] = process_tutorial_achievements(result['tutorialachievement'])
    
    return result


def process_tutorial_subcategories(subcategories: Union[Dict, List, None]) -> List[Dict]:
    """Process tutorialsubcategory entries."""
    items = ensure_array(subcategories)
    return [process_tutorial_subcategory(item) for item in items]


def process_category(category: Dict) -> Dict:
    """Process a single category."""
    result = filter_fields(category, CATEGORY_FIELDS)
    
    # Process nested categoryrewards
    if 'categoryrewards' in result:
        result['categoryrewards'] = process_categoryrewards(result['categoryrewards'])
    
    # Process nested tutorialsubcategory
    if 'tutorialsubcategory' in result:
        result['tutorialsubcategory'] = process_tutorial_subcategories(result['tutorialsubcategory'])
    
    # Process nested subcategory
    if 'subcategory' in result:
        result['subcategory'] = process_subcategories(result['subcategory'])
    
    return result


def process_journal(data: Dict) -> Dict:
    """Process the albionjournal.json data, keeping only specified fields."""
    categories = data.get('albionjournal', {}).get('categories', {}).get('category', [])
    categories_array = ensure_array(categories)
    
    processed_categories = [process_category(cat) for cat in categories_array]
    
    return {
        'categories': processed_categories
    }
