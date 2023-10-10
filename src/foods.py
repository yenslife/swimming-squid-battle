import pygame.sprite

from games.easy_game.src.env import FoodTypeEnum, FOOD_COLOR_MAP
from mlgame.view.view_model import create_rect_view_data


class Food(pygame.sprite.Sprite):
    def __init__(self, group):
        pygame.sprite.Sprite.__init__(self, group)
        self.image = pygame.Surface([8, 8])
        self.type = None
        self.score = 0
        self.color = None

        self.rect = self.image.get_rect()
        self.angle = 0

    def update(self) -> None:
        pass

    @property
    def game_object_data(self):
        return create_rect_view_data(
            "food",
            self.rect.x,
            self.rect.y,
            self.rect.width,
            self.rect.height,
            self.color
        )


class GoodFoodLv1(Food):
    def __init__(self, group):
        super().__init__(group)
        self.image = pygame.Surface([8, 8])
        self.type = FoodTypeEnum.GOOD_1
        self.color = FOOD_COLOR_MAP[self.type]
        self.score = 1
        self.rect = self.image.get_rect()
        self.angle = 0


class BadFoodLv1(Food):
    def __init__(self, group):
        super().__init__(group)
        self.image = pygame.Surface([8, 8])
        self.type = FoodTypeEnum.BAD_1
        self.color = FOOD_COLOR_MAP[self.type]
        self.score = -1
        self.rect = self.image.get_rect()
        self.angle = 0
