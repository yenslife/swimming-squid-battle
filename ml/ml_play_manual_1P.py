"""
Use Q table to make decision, and update Q table by the result of the decision
"""
import random
from pprint import pprint
import numpy as np
import orjson
import pygame
import math
import pickle

json_file_path = "/Users/mac/ncku/moodle/112-2三下/ML機器學習/swimming-squid-battle/n_3_qtable.json"
class MLPlay:
    def __init__(self,ai_name,*args,**kwargs):
        print("Initial ml script")
        self.qtable_init()
        self.state = {'UP': 0, 'RIGHT': 0, 'DOWN': 0, 'LEFT': 0}  
        self.current_reward = 0
        self.previous_reward = 0  

    
    def qtable_init(self):
        global json_file_path
        self.qtable = {}
        # check if file exists
        try:
            json_file = open(json_file_path, "r")
            self.qtable = orjson.loads(json_file.read())
            json_file.close()
        except Exception as e:
            print("e:",e)
            json_file_path = "/Users/mac/ncku/moodle/112-2三下/ML機器學習/swimming-squid-battle/tmp_qtable.json"    

            

    def feature_extract(self, scene_info, mode=1):
        """
        提取特徵
        計算所有物件與魷魚的距離，排序後，選擇前N個靠近的物件，將每個被選取的物件的座標減去魷魚的座標（與魷魚的座標差）。根據其座標差分為上下左右四類。
        """
        # 魷魚的座標
        x = scene_info['self_x']
        y = scene_info['self_y']

        # 物件的座標
        food = scene_info['foods']
        food_distance = []

        # 計算所有物件與魷魚的距離
        for i in range(len(food)):
            x_diff = food[i]['x'] - x
            y_diff = food[i]['y'] - y
            food_distance.append(math.sqrt(x_diff**2 + y_diff**2))
        food_distance = np.array(food_distance)

        # 排序
        food = np.array(food)
        sorted_index = np.argsort(food_distance) # 排序後的索引
        food = food[sorted_index] # 排序後的物件

        # 選擇前N個靠近的物件，計算其座標差，分為上下左右四類
        # 看哪個類別的分數總和最高
        # 如果是 mode 1 則只取前 5 個物件
        # 如果是 mode 2 則移除分數為負的物件，並只取第一個物件
        if mode == 1:
            N = 3 if len(food) >= 3 else len(food)
        elif mode == 2:
            N = 1
            food = [f for f in food if f['score'] > 0]
        # N = len(food)
        food = food[:N]
        score = {}
        score['UP'] = 0
        score['RIGHT'] = 0
        score['DOWN'] = 0
        score['LEFT'] = 0
        
        for i in range(N):
            x_moved = food[i]['x'] - x # 物件的座標減去魷魚的座標，也就是當作魷魚的座標是 (0, 0)
            y_moved = food[i]['y'] - y
            x_rotated = x_moved * math.cos(math.pi/4) - y_moved * math.sin(math.pi/4) # 逆時針旋轉 45 度
            y_rotated = x_moved * math.sin(math.pi/4) + y_moved * math.cos(math.pi/4)
            weighted_score = food[i]['score'] + round(1/(food_distance[i]+1) * 20) # 距離越近，分數越高
            if x_rotated > 0 and y_rotated > 0:
                score['RIGHT'] += weighted_score
            elif x_rotated > 0 and y_rotated < 0:
                score['UP'] += weighted_score
            elif x_rotated < 0 and y_rotated < 0:
                score['LEFT'] += weighted_score
            elif x_rotated < 0 and y_rotated > 0:
                score['DOWN'] += weighted_score

        # 找出分數最高的方向，如果有多個方向的分數一樣，則隨機選擇一個
        # 隨機用 random
        max_direction = max(score, key=score.get)
        max_score = score[max_direction]
        max_directions = [k for k, v in score.items() if v == max_score]
        max_direction = random.choice(max_directions) # 隨機選擇一個

        # 如果 self.lv > component.lv，則選擇吃 component
        fuck_score = 20
        run_away = -100
        # 計算上下左右
        x_diff = scene_info['opponent_x'] - x
        y_diff = scene_info['opponent_y'] - y
        x_rotated = x_diff * math.cos(math.pi/4) - y_diff * math.sin(math.pi/4)
        y_rotated = x_diff * math.sin(math.pi/4) + y_diff * math.cos(math.pi/4)
        if scene_info['self_lv'] > scene_info['opponent_lv']:
            if x_rotated > 0 and y_rotated > 0:
                score['RIGHT'] += fuck_score
            elif x_rotated > 0 and y_rotated < 0:
                score['UP'] += fuck_score
            elif x_rotated < 0 and y_rotated < 0:
                score['LEFT'] += fuck_score
            elif x_rotated < 0 and y_rotated > 0:
                score['DOWN'] += fuck_score
            max_direction = max(score, key=score.get)
        
        return score, max_direction
        
    
    def get_action(self, state):
        max_direction = max(state, key=state.get)
        max_state = state[max_direction]
        max_directions = [k for k, v in state.items() if v == max_state]
        max_direction = random.choice(max_directions) # 隨機選擇一個
        return [max_direction]
    
    def get_reward(self, scene_info):
        self.current_reward = scene_info['score'] - self.previous_reward
        reword = self.current_reward
        return reword

    def update(self, scene_info: dict, keyboard:list=[], *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        actions = []

        # update Q table
        reward = self.get_reward(scene_info)  

        # get next state and maxQ
        next_state, maxQ = self.feature_extract(scene_info, mode=1)

        # update Q table
        state_array = np.array(list(self.state.values()))
        next_state_array = np.array(list(next_state.values())) if next_state else np.zeros_like(state_array)  # 將下一個狀態轉換為numpy陣列，如果下一個狀態不存在，則為零
        Q = self.qtable.get(str(self.state), 0) 
        max_next_Q = np.max(next_state_array)  # 獲取下一個狀態的最大Q值
        updated_Q = Q + 0.1 * (reward + 0.9 * max_next_Q - Q)
        self.qtable[str(self.state)] = updated_Q

        # get action
        actions = self.get_action(next_state) # 這邊要改成 updated_Q
        self.state = next_state
        self.previous_reward = scene_info['score']

        return actions

    def reset(self):
        global pickle_file_path
        """
        Reset the status
        """
        # print("reset ml script")
        # dump q table
        # print("qtable", self.qtable)
        # print the len of qtable
        print("\nlen of qtable", len(self.qtable), "\n")
        # with open(pickle_file_path, "wb") as f:
        #     pickle.dump(self.qtable, f)
        with open(json_file_path, "w") as f:
            # TO JSON SERIALIZE numpy.float64
            f.write(orjson.dumps(self.qtable, option=orjson.OPT_SERIALIZE_NUMPY).decode())        
