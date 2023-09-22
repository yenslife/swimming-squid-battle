import random

import pygame.sprite

from games.easy_game.src.enums import FoodTypeEnum
from mlgame.view.view_model import create_rect_view_data

FOOD_COLOR_MAP = {FoodTypeEnum.GREEN: "#009688",
                  FoodTypeEnum.BLACK: "#263238"}

BALL_VEL = 10.5

BALL_H = 50

BALL_W = 50


class Ball(pygame.sprite.Sprite):
    def __init__(self, color="#FFEB3B"):
        pygame.sprite.Sprite.__init__(self)
        self.origin_image = pygame.Surface([BALL_W, BALL_H])
        self.image = self.origin_image
        self.color = color
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300)

    def update(self, motion):
        # for motion in motions:
        if motion == "UP":
            self.rect.centery -= BALL_VEL
        elif motion == "DOWN":
            self.rect.centery += BALL_VEL
        elif motion == "LEFT":
            self.rect.centerx -= BALL_VEL
            # self.angle += 5
        elif motion == "RIGHT":
            self.rect.centerx += BALL_VEL
            # self.angle -= 5
        # self.image = pygame.transform.rotate(self.origin_image, self.angle)
        # print(self.angle)
        # center = self.rect.center
        # self.rect = self.image.get_rect()
        # self.rect.center = center

    @property
    def game_object_data(self):
        return create_rect_view_data(
            "ball",
            self.rect.x,
            self.rect.y,
            self.rect.width,
            self.rect.height,
            self.color
        )


class Food(pygame.sprite.Sprite):
    def __init__(self, group, type: FoodTypeEnum):
        pygame.sprite.Sprite.__init__(self, group)
        self.image = pygame.Surface([8, 8])
        self.type = type
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
