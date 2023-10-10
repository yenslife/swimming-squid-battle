from enum import auto
from os import path

from mlgame.utils.enum import StringEnum
# game
WIDTH = 800
HEIGHT = 600
BG_COLOR = "#111111"
PG_COLOR = "#B3E5FC"

# ball
BALL_COLOR = "#FFEB3B"
BALL_VEL = 10.5
BALL_H = 30
BALL_W = 30


# food
class FoodTypeEnum(StringEnum):
    # TODO add good_lv1~good_lv3
    GREEN = auto()
    RED = auto()
FOOD_COLOR_MAP = {FoodTypeEnum.GREEN: "#009688",
                  FoodTypeEnum.RED: "#FF1744"}

# path of assets
ASSET_PATH = path.join(path.dirname(__file__), "..", "asset")
LEVEL_PATH = path.join(path.dirname(__file__), "..", "levels")
SOUND_PATH = path.join(path.dirname(__file__), "..", "asset", "sounds")
MUSIC_PATH = path.join(path.dirname(__file__), "..", "asset", "music")


