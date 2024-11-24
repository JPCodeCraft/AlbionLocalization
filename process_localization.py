def process_localization(data):
    # Process items
    items = [
        {**item, '@tuid': item['@tuid'].replace('@', '')}
        for item in data['tmx']['body']['tu']
        if item['@tuid'].startswith('@ITEMS_') and not item['@tuid'].endswith('_DESC')
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

    # Combine all processed entries
    return items + shop_categories + shop_subcategories + destiny_board