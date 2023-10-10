import pygame.sprite

from games.easy_game.src.env import FoodTypeEnum, FOOD_COLOR_MAP
from mlgame.view.view_model import create_rect_view_data


class Food(pygame.sprite.Sprite):
    def __init__(self, group, type: FoodTypeEnum):
        pygame.sprite.Sprite.__init__(self, group)
        self.image = pygame.Surface([8, 8])
        self.type = type
        self.score = 0
        self.color = FOOD_COLOR_MAP[type]

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
