import random

import pygame.sprite

from mlgame.view.view_model import create_rect_view_data

BALL_VEL = 10.5

BALL_H = 100

BALL_W = 10


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
    def __init__(self, group):
        pygame.sprite.Sprite.__init__(self, group)
        self.image = pygame.Surface([8, 8])
        self.color = "#E91E63"
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(0, 800)
        self.rect.centery = random.randint(0, 600)
        self.angle = 0

    def update(self) -> None:
        self.angle += 10
        if self.angle > 360:
            self.angle -= 360

    @property
    def game_object_data(self):
        return {"type": "rect",
                "name": "ball",
                "x": self.rect.x,
                "y": self.rect.y,
                "angle": 0,
                "width": self.rect.width,
                "height": self.rect.height,
                "color": self.color
                }
