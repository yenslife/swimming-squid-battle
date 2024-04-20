import random
from pprint import pprint
import math

import orjson
import pygame
import numpy as np

NUM = 100
json_file_path = "/Users/mac/ncku/moodle/112-2三下/ML機器學習/swimming-squid-battle/model/v2_qtable.json"

class MLPlay:
    def __init__(self,ai_name,*args,**kwargs):
        print("Initial ml script")
        self.qtable_init()

    def qtable_init(self):
        global json_file_path
        self.qtable = np.zeros((4, 4, 4, 4, 4))
        self.previous_score = 0
        self.previous_action_index = 0
        self.state = {"UP": 0, "RIGHT": 0, "DOWN": 0, "LEFT": 0}
        # check if file exists
        exist = False
        try:
            json_file = open(json_file_path, "r")
            self.qtable = orjson.loads(json_file.read())
            if len(self.qtable) > 0:
                exist = True
            # make it numpy array
            self.qtable = np.array(self.qtable)
            json_file.close()
        except Exception as e:
            print("e:",e)
            # json_file_path = "/Users/mac/ncku/moodle/112-2三下/ML機器學習/swimming-squid-battle/tmp_qtable.json"
        if not exist:
            self.qtable = np.zeros((4, 4, 4, 4, 4))

    def extract_feature(self, scene_info, N=NUM):
        """
        提取特徵
        """
        self_x = scene_info["self_x"]
        self_y = scene_info["self_y"]
        self_w = scene_info["self_w"]
        self_h = scene_info["self_h"]
        self_vel = scene_info["self_vel"]
        self_lv = scene_info["self_lv"]
        foods = scene_info["foods"]
        feature = []
        N = min(N, len(foods)) # 防止物件數量不足N個 # 取前N個靠近的物件
        # 上下左右
        # 將以魷魚為中心，分成 12 個區域 (T, R, B, L, LTT, LLT, RTT, RRT, LLB, LBB, RRB, RBB)
        # T: Top, R: Right, B: Bottom, L: Left 依此類推
        # 由於的寬度為 self_w 高度為 self_h
        # 以上區為例，由於正上方的食物分數權重 (weight) 為 2，所以將正上方的食物的座標差乘上 2
        # 靠近正上方的左邊和右邊的食物分數權重為 1.5，所以將靠近正上方的左邊和右邊的食物的座標差乘上 1.5
        # 靠近左邊或右邊的食物分數權重為 1，所以將靠近左邊或右邊的食物的座標差乘上 1
        # 下、左、右的分數權重也是如此
        # 特殊物件：對手的魷魚，分數權重為 (self.lv - component.lv) * 10 if component.lv < self.lv else 0
        # 當自己的等級大於對手的等級時，對手的魷魚的分數權重為 (self.lv - component.lv) * 10，也就是追蹤對手的魷魚攻擊他
        # 所以也要把對手的魷魚物件加入特徵中

        # 公式如下：設 x 為食物 (包含負分的垃圾以及對手) 的分數
        # 上區總分 = sum(Xi * weight * quantized_distance) 從 i = 0 到 N
        # weight = 2 if Xi 是正上方的食物, 1.5 if Xi 是靠近正上方的左右方的食物, 1 if Xi 是靠近左右偏上方的食物
        # quantized_distance = distance / self.vel (為了讓量化距離，才不會讓 Q table 太大)
        # distance = abs(food_x - self_x) + abs(food_y - self_y)
        # self.vel 是魷魚的速度

        # 最後將上下左右四個區域的分數相加，並且排名為 feature，降低維度複雜度
        # 使用 4, 3, 2, 1 來表示分數的大小順序，這樣可以讓 Q table 的維度降低
        # 比較高的分數給他 4，再來是 3，2，1，0，如果有同分的就給他一樣的分數

        # 判斷食物的位置
        object_position = {"T": [], "R": [], "B": [], "L": [], "LTT": [], "LLT": [], "RTT": [], "RRT": [], "LLB": [], "LBB": [], "RRB": [], "RBB": []}
        weight = {"T": 2, "R": 1, "B": 1, "L": 1, "LTT": 1.5, "LLT": 1.5, "RTT": 1.5, "RRT": 1.5, "LLB": 1.5, "LBB": 1.5, "RRB": 1.5, "RBB": 1.5}

        def calculate_direction(x, y):
            x_moved = x - self_x # 物件的座標減去魷魚的座標，也就是當作魷魚的座標是 (0, 0)
            y_moved = y - self_y
            x_rotated = x_moved * math.cos(math.pi/4) - y_moved * math.sin(math.pi/4)
            y_rotated = x_moved * math.sin(math.pi/4) + y_moved * math.cos(math.pi/4)
            if abs(x - self_x) <= self_w / 2 and y < self_y: # 上
                return "T"
            elif x > self_x and abs(y - self_y) <= self_h / 2: # 右
                return "R"
            elif abs(x - self_x) <= self_w / 2 and y > self_y: # 下
                return "B"
            elif x < self_x and abs(y - self_y) <= self_h / 2: # 左
                return "L"
            elif x_rotated > 0 and y_rotated > 0: # 右部分，判斷是 RRT 還是 RRB
                if y < self_y:
                    return "RRT"
                else:
                    return "RRB"
            elif x_rotated > 0 and y_rotated < 0: # 上部分，判斷是 LTT 還是 RTT
                if x < self_x:
                    return "LTT"
                else:
                    return "RTT"
            elif x_rotated < 0 and y_rotated < 0: # 左部分，判斷是 LLT 還是 LLB
                if y < self_y:
                    return "LLT"
                else:
                    return "LLB"
            elif x_rotated < 0 and y_rotated > 0: # 下部分，判斷是 LBB 還是 RBB
                if x < self_x:
                    return "LBB"
                else:
                    return "RBB"
            else:
                "UP" # 有可能是 NONE，這邊直接用 UP 因為我們比較不希望魷魚掉下去，垃圾是往下掉的

        def quantized_distance_calculator(x, y):
            distance = abs(x - self_x) + abs(y - self_y)
            denominator = ((distance / self_vel) * 10 - 5) if ((distance / self_vel) * 10 - 5) != 0 else 1
            quantized_distance = 1 / denominator
            return quantized_distance
                
        for i in range(N):
            food_x = foods[i]["x"]
            food_y = foods[i]["y"]
            food_score = foods[i]["score"]
            quantized_distance = quantized_distance_calculator(food_x, food_y)
            direction = calculate_direction(food_x, food_y)
            try:
                object_position[direction].append(food_score * weight[direction] * quantized_distance)
            except: # 可能是 key error: None
                pass

            
        # 對手的魷魚
        opponent_x = scene_info["opponent_x"]
        opponent_y = scene_info["opponent_y"]
        opponent_lv = scene_info["opponent_lv"]
        attack_score = 10
        quantized_distance = quantized_distance_calculator(opponent_x, opponent_y)
        direction = calculate_direction(opponent_x, opponent_y)
        if opponent_lv < self_lv:
            try: 
                object_position[direction].append((self_lv - opponent_lv) * attack_score * quantized_distance)
            except:
                pass
        
        # 根據區域分數，給予分數
        feature_scores = {"UP": (sum(object_position["T"]) + sum(object_position["LTT"]) + sum(object_position["RTT"])),
                  "RIGHT": (sum(object_position["R"]) + sum(object_position["RRT"]) + sum(object_position["RRB"])),
                  "DOWN": (sum(object_position["B"]) + sum(object_position["LBB"]) + sum(object_position["RBB"])),
                  "LEFT": (sum(object_position["L"]) + sum(object_position["LLT"]) + sum(object_position["LLB"]))}
        
        # 排名
        # find max, 如果有多個 max 就給他一樣的分數
        quantized_feature_scores = { key : value for key, value in feature_scores.items()}
        grade = 3
        count = 0
        while count < 4:
            max_value_list = [key for key, value in feature_scores.items() if value == max(feature_scores.values())]
            count += len(max_value_list)
            for key in max_value_list:
                quantized_feature_scores[key] = grade
                feature_scores[key] = -999
            grade -= 1
            
        return quantized_feature_scores
    
    def get_action(self, feature: dict):
        # 找出 feature 中 value 最大者 
        for key, value in feature.items():
            if value == max(feature.values()):
                max_action = key
        max_action_index = 0
        if max_action == "UP":
            max_action_index = 0
        elif max_action == "RIGHT":
            max_action_index = 1
        elif max_action == "DOWN":
            max_action_index = 2
        elif max_action == "LEFT":
            max_action_index = 3
        return max_action, max_action_index
    
    def get_reward(self, scene_info):
        reward = 0
        if scene_info["score"] > self.previous_score:
            reward = 1
        elif scene_info["score"] < self.previous_score:
            reward = -1
        self.previous_score = scene_info["score"]
        return reward
    
    def update_qtable(self, scene_info, action_index, reward, state, previous_state):
        learning_rate = 0.1
        discount_factor = 0.9
        _, max_action_index = self.get_action(state)
        previous_state = [previous_state["UP"], previous_state["RIGHT"], previous_state["DOWN"], previous_state["LEFT"]]
        state = [state["UP"], state["RIGHT"], state["DOWN"], state["LEFT"]]
        old_Q = self.qtable[previous_state[0]][previous_state[1]][previous_state[2]][previous_state[3]][action_index]
        try:
            new_Q = old_Q + learning_rate * (reward + discount_factor * self.qtable[state[0]][state[1]][state[2]][state[3]][max_action_index] - old_Q)
        except:
            new_Q = old_Q
        self.qtable[previous_state[0]][previous_state[1]][previous_state[2]][previous_state[3]][action_index] = new_Q


    def update(self, scene_info: dict, keyboard:list=[], *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        # pprint("AI received data from game :", orjson.dumps(scene_info))
        # pprint(scene_info)
        actions = []

        state = self.extract_feature(scene_info, N=NUM)
        action = self.get_action(state)
        action_index = action[1]
        reward = self.get_reward(scene_info)
        if self.previous_action_index != None:
            self.update_qtable(scene_info, action_index, reward, state, self.state)
        self.state = state
        self.previous_action_index = action_index

        actions = [action[0]]

        return actions



    def reset(self):
        """
        Reset the status
        """
        print("reset ml script")
        # write to json
        global json_file_path
        json_file = open(json_file_path, "w")
        to_list = self.qtable.tolist()
        json_file.write(orjson.dumps(to_list).decode())
        json_file.close()
        pass
