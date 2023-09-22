import copy
import json
import os.path
from os import path

import pygame

from mlgame.game.paia_game import PaiaGame, GameResultState, GameStatus
from mlgame.utils.enum import get_ai_name
from mlgame.view.decorator import check_game_progress, check_game_result
from mlgame.view.view_model import *
from .enums import FoodTypeEnum
from .game_object import Ball, Food

BG_COLOR = "#111111"
PG_COLOR = "#B3E5FC"

WIDTH = 800
HEIGHT = 600
ASSET_PATH = path.join(path.dirname(__file__), "../asset")
LEVEL_PATH = path.join(path.dirname(__file__), "../levels")


class EasyGame(PaiaGame):
    """
    This is a Interface of a game
    """

    def __init__(
            self, time_to_play, score_to_pass, green_food_count, black_food_count,
            playground_size: list,
            level: int = -1,
            # level_file,
            *args, **kwargs):
        super().__init__(user_num=1)

        self.game_result_state = GameResultState.FAIL
        self.scene = Scene(width=WIDTH, height=HEIGHT, color=BG_COLOR, bias_x=0, bias_y=0)
        if level != -1:
            with open(os.path.join(LEVEL_PATH, f"{level:03d}.json")) as f:
                game_params = json.load(f)
            self.playground_w = int(game_params["playground_size"][0])
            self.playground_h = int(game_params["playground_size"][1])
            self.playground = pygame.Rect(
                0, 0,
                self.playground_w,
                self.playground_h
            )
            self.green_food_count = int(game_params["green_food_count"])
            self.black_food_count = int(game_params["black_food_count"])
            self.score_to_win = int(game_params["score_to_pass"])
            self.frame_limit = int(game_params["time_to_play"])
            pass
        else:
            self.playground_w = int(playground_size[0])
            self.playground_h = int(playground_size[1])
            self.playground = pygame.Rect(
                0, 0,
                self.playground_w,
                self.playground_h
            )
            self.green_food_count = green_food_count
            self.black_food_count = black_food_count
            self.score_to_win = score_to_pass
            self.frame_limit = time_to_play

        self.playground.center = (WIDTH / 2, HEIGHT / 2)
        self.foods = pygame.sprite.Group()
        self.init_game()

    def init_game(self):
        self.ball = Ball()
        self.foods.empty()
        self.score = 0
        self._create_foods(self.green_food_count, FoodTypeEnum.GREEN)
        self._create_foods(self.black_food_count, FoodTypeEnum.BLACK)
        self.frame_count = 0
        self._frame_count_down = self.frame_limit

    def update(self, commands):
        # handle command
        ai_1p_cmd = commands[get_ai_name(0)]
        if ai_1p_cmd is not None:
            action = ai_1p_cmd[0]
        else:
            action = "NONE"

        self.ball.update(action)
        self.revise_ball(self.ball, self.playground)
        # update sprite
        self.foods.update()

        # handle collision
        hits = pygame.sprite.spritecollide(self.ball, self.foods, True)
        if hits:
            for food in hits:
                if food.type == FoodTypeEnum.GREEN:
                    self.score += 1
                    self._create_foods(1, FoodTypeEnum.GREEN)

                elif food.type == FoodTypeEnum.BLACK:
                    self._create_foods(1, FoodTypeEnum.BLACK)
                    self.score -= 1
        # self._timer = round(time.time() - self._begin_time, 3)

        self.frame_count += 1
        self._frame_count_down = self.frame_limit - self.frame_count
        # self.draw()

        if not self.is_running:
            return "RESET"

    def get_data_from_game_to_player(self):
        """
        send something to game AI
        we could send different data to different ai
        """
        to_players_data = {}
        foods_data = []
        for food in self.foods:
            foods_data.append({"x": food.rect.x, "y": food.rect.y})
        data_to_1p = {
            "frame": self.frame_count,
            "ball_x": self.ball.rect.centerx,
            "ball_y": self.ball.rect.centery,
            "foods": foods_data,
            "score": self.score,
            "status": self.get_game_status()
        }

        to_players_data[get_ai_name(0)] = data_to_1p
        # should be equal to config. GAME_SETUP["ml_clients"][0]["name"]

        return to_players_data

    def get_game_status(self):

        if self.is_running:
            status = GameStatus.GAME_ALIVE
        elif self.score > self.score_to_win:
            status = GameStatus.GAME_PASS
        else:
            status = GameStatus.GAME_OVER
        return status

    def reset(self):
        self.init_game()

        pass

    @property
    def is_running(self):
        return self.frame_count < self.frame_limit

    def get_scene_init_data(self):
        """
        Get the initial scene and object information for drawing on the web
        """
        # TODO add music or sound
        bg_path = path.join(ASSET_PATH, "img/background.jpg")
        background = create_asset_init_data(
            "background", WIDTH, HEIGHT, bg_path,
            github_raw_url="https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/easy_game/main/asset/img/background.jpg")
        scene_init_data = {"scene": self.scene.__dict__,
                           "assets": [
                               background
                           ],
                           # "audios": {}
                           }
        return scene_init_data

    @check_game_progress
    def get_scene_progress_data(self):
        """
        Get the position of game objects for drawing on the web
        """
        foods_data = []
        for food in self.foods:
            foods_data.append(food.game_object_data)
        game_obj_list = [self.ball.game_object_data]
        game_obj_list.extend(foods_data)
        backgrounds = [
            create_image_view_data("background", 0, 0, WIDTH, HEIGHT),
            create_rect_view_data(
                "playground", self.playground.x, self.playground.y,
                self.playground.w, self.playground.h, PG_COLOR)
        ]
        foregrounds = [create_text_view_data(f"Score = {self.score:04d}", 650, 50, "#FF0000", "24px Arial BOLD")]
        toggle_objs = [
            create_text_view_data(f"{self._frame_count_down:04d} frame", 650, 100, "#FFAA00", "24px Arial BOLD")]
        scene_progress = create_scene_progress_data(frame=self.frame_count, background=backgrounds,
                                                    object_list=game_obj_list,
                                                    foreground=foregrounds, toggle=toggle_objs)
        return scene_progress

    @check_game_result
    def get_game_result(self):
        """
        send game result
        """
        if self.get_game_status() == GameStatus.GAME_PASS:
            self.game_result_state = GameResultState.FINISH
        return {"frame_used": self.frame_count,
                "state": self.game_result_state,
                "attachment": [
                    {
                        "player": get_ai_name(0),
                        "rank": 1,
                        "score": self.score,
                        "passed": self.score > self.score_to_win
                    }
                ]

                }

    def get_keyboard_command(self):
        """
        Define how your game will run by your keyboard
        """
        cmd_1p = []
        key_pressed_list = pygame.key.get_pressed()
        if key_pressed_list[pygame.K_UP]:
            cmd_1p.append("UP")
        elif key_pressed_list[pygame.K_DOWN]:
            cmd_1p.append("DOWN")
        elif key_pressed_list[pygame.K_LEFT]:
            cmd_1p.append("LEFT")
        elif key_pressed_list[pygame.K_RIGHT]:
            cmd_1p.append("RIGHT")
        else:
            cmd_1p.append("NONE")
        return {get_ai_name(0): cmd_1p}

    def _create_foods(self, count: int = 5, type: FoodTypeEnum = FoodTypeEnum.GREEN):
        for i in range(count):
            # add food to group
            food = Food(self.foods, type)

            food.rect.centerx = random.randint(self.playground.left, self.playground.right)
            food.rect.centery = random.randint(self.playground.top, self.playground.bottom)
        pass

    def revise_ball(self, ball: Ball, playground: pygame.Rect):
        ball_rect = copy.deepcopy(ball.rect)
        if ball_rect.left < playground.left:
            ball_rect.left = playground.left
        elif ball_rect.right > playground.right:
            ball_rect.right = playground.right

        if ball_rect.top < playground.top:
            ball_rect.top = playground.top
        elif ball_rect.bottom > playground.bottom:
            ball_rect.bottom = playground.bottom
        ball.rect = ball_rect
        pass
