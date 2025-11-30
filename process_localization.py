def process_localization(data):
    # Process items
    items = [
        {**item, '@tuid': item['@tuid'].replace('@', '')}
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
        {**item, '@tuid': item['@tuid'].replace('@', '')}
        for item in data['tmx']['body']['tu']
        if item['@tuid'].startswith('@SPELLS_') and not item['@tuid'].endswith('_DESC')
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