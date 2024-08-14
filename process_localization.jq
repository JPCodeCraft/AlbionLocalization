[
  .tmx.body.tu[] 
  | select(.["@tuid"] | startswith("@ITEMS_") and (endswith("_DESC") | not)) 
  | .["@tuid"] |= sub("@"; "")
] as $items |
[
  .tmx.body.tu[] | select(.["@tuid"] | startswith("@MARKETPLACEGUI_ROLLOUT_SHOPCATEGORY_")) | .["@tuid"] |= sub("^@MARKETPLACEGUI_ROLLOUT_"; "")
] as $shopcategory |
[
  .tmx.body.tu[] | select(.["@tuid"] | startswith("@MARKETPLACEGUI_ROLLOUT_SHOPSUBCATEGORY_")) | .["@tuid"] |= sub("^@MARKETPLACEGUI_ROLLOUT_"; "")
] as $shopsubcategory |
[
  .tmx.body.tu[] | select(.["@tuid"] | startswith("@DESTINYBOARD_TITLE_")) | .["@tuid"] |= sub("@"; "")
] as $destinyboard |
# [
#   .tmx.body.tu[] | select(.["@tuid"] | startswith("@CRYSTAL_LEAGUE") and contains("TOKEN")) | .["@tuid"] |= sub("@"; "ITEMS_")
# ] as $crystal_league_token |
# ($items + $shopcategory + $shopsubcategory + $destinyboard + $crystal_league_token)
($items + $shopcategory + $shopsubcategory + $destinyboard)