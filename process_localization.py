import re


def _clean_spell_desc_seg(seg):
    if not isinstance(seg, str):
        return seg
    def _replace_tag(match):
        tag = match.group(0)
        if tag.startswith("[/"):
            return "</strong>"
        return "<strong>"

    seg = re.sub(r"\[/?[^\]]+\]", _replace_tag, seg)
    # Replace unknown value placeholders like $foo$ or $$BAR$ with a simple marker.
    seg = re.sub(r"\$\$?[^$]+\$", "?", seg)
    seg = seg.replace("\n", "<br>")
    return seg


def _clean_spell_desc_item(item):
    if not item.get("@tuid", "").endswith("_DESC"):
        return item
    tuv_list = item.get("tuv", [])
    if not isinstance(tuv_list, list):
        return item
    cleaned_tuv = []
    for tuv in tuv_list:
        if isinstance(tuv, dict) and "seg" in tuv:
            cleaned_tuv.append({**tuv, "seg": _clean_spell_desc_seg(tuv["seg"])})
        else:
            cleaned_tuv.append(tuv)
    return {**item, "tuv": cleaned_tuv}


def process_localization(data):
    # Process items
    items = [
        {**item, '@tuid': ('ITEMS_' + item['@tuid'].replace('@', '')) if item['@tuid'] == '@EXPEDITION_TOKEN' else item['@tuid'].replace('@', '')}
        for item in data['tmx']['body']['tu']
        if (item['@tuid'].startswith('@ITEMS_') and not item['@tuid'].endswith('_DESC')) or item['@tuid'] == '@EXPEDITION_TOKEN'
    ]

    # Process shop categories
    shop_categories = [
        {**item, '@tuid': item['@tuid'].replace('@MARKETPLACEGUI_ROLLOUT_', '')}
        for item in data['tmx']['body']['tu']
        if item['@tuid'].startswith('@MARKETPLACEGUI_ROLLOUT_SHOPCATEGORY_')
    ]

    # Process shop subcategories
    shop_subcategories = [
        {**item, '@tuid': item['@tuid'].replace('@MARKETPLACEGUI_ROLLOUT_', '')}
        for item in data['tmx']['body']['tu']
        if item['@tuid'].startswith('@MARKETPLACEGUI_ROLLOUT_SHOPSUBCATEGORY_')
    ]

    # Process destiny board entries
    destiny_board = [
        {**item, '@tuid': item['@tuid'].replace('@', '')}
        for item in data['tmx']['body']['tu']
        if item['@tuid'].startswith('@DESTINYBOARD_TITLE_')
    ]

    # Process spell entries
    spell_entries = [
        _clean_spell_desc_item({**item, '@tuid': item['@tuid'].replace('@', '')})
        for item in data['tmx']['body']['tu']
        if item['@tuid'].startswith('@SPELLS_')
    ]

    # Process journal category and activity entries (e.g., @JOURNAL_CATEGORY_PVE, @JOURNAL_ACTIVITY_EXPEDITION)
    journal_categories = [
        {**item, '@tuid': item['@tuid'].replace('@', '')}
        for item in data['tmx']['body']['tu']
        if item['@tuid'].startswith('@JOURNAL_CATEGORY_') or item['@tuid'].startswith('@JOURNAL_ACTIVITY_')
    ]

    # Process journal achievement entries (title and description)
    # Achievement names like SA_PVE_RANDOMDUNGEON_ENTERED_01 have @SA_PVE_RANDOMDUNGEON_ENTERED_01_TITLE and _DESCRIPTION
    journal_achievements = [
        {**item, '@tuid': item['@tuid'].replace('@', '')}
        for item in data['tmx']['body']['tu']
        if (item['@tuid'].endswith('_TITLE') or item['@tuid'].endswith('_DESCRIPTION')) 
        and (item['@tuid'].startswith('@SA_') or item['@tuid'].startswith('@JOURNAL_'))
    ]

    # Combine all processed entries
    return items + shop_categories + shop_subcategories + destiny_board + spell_entries + journal_categories + journal_achievements
