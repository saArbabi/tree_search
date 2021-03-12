from environment.viewer import Viewer
import math
from vehicles.idm_vehicle import IDMVehicle
# from vehicles.sd_vehicle import SDVehicle
import numpy as np

class Env():
    RIGHT_LANE_REWARD = 0.1
    """The reward received when driving on the right-most lanes, linearly mapped to zero for other lanes."""

    HIGH_SPEED_REWARD = 0.4
    """The reward received when driving at full speed, linearly mapped to zero for lower speeds."""

    LANE_CHANGE_REWARD = -0.1
    """The reward received at each lane change decision."""

    COLLISION_REWARD = -10
    """The reward received when two cars collide."""

    def __init__(self):
        self.viewer = None
        self.vehicles = [] # all vehicles
        self.env_clock = 0 # time past since the episode's start
        self.sdv = None
        self.default_config()
        self.seed()

    def seed(self, seed_value=2021):
        for veh in self.vehicles:
            if veh.id != 'sdv':
                veh.seed(seed_value)

    def reset(self):
        if self.sdv:
            return  self.sdv.observe(self.vehicles)

    def default_config(self):
        self.config = {'lane_count':5,
                        'lane_width':3.7, # m
                        'lane_length':10000, # m
                        'percept_range':70, # m, front and back
                        }

    # def step(self, decision):
    #     self.sdv.time_budget = 1
    #     # low-level actions currently not obs dependant
    #     sdv_obs = self.sdv.observe(self.vehicles)
    #     sdv_action = self.sdv.act(decision, sdv_obs)
    #
    #     while self.sdv.time_budget > 0:
    #         self.sdv.step(sdv_action)
    #         for vehicle in self.vehicles:
    #             if vehicle.id == 'sdv':
    #                 continue
    #             obs = vehicle.observe(self.vehicles)
    #             action = vehicle.act(obs)
    #             vehicle.step(action)
    #         self.sdv.time_budget -= 0.1
    #     # self.env_clock += 0.1
    #     sdv_obs = self.sdv.observe(self.vehicles)
    #     terminal = self.check_terminal(sdv_obs)
    #     reward = self.get_reward(sdv_obs, terminal)
    #     return sdv_obs, reward, terminal

    def step(self, decision=None):
        # low-level actions currently not obs dependant

        for vehicle in self.vehicles:
            if vehicle.id == 'sdv':
                continue
            obs = vehicle.observe(self.vehicles)
            action = vehicle.act(obs)
            vehicle.step(action)


    def render(self):
        if self.viewer is None:
            self.viewer = Viewer(self.config)
            # self.viewer.PAUSE_CONTROL = PAUSE_CONTROL

        self.viewer.update_plots(self.vehicles)

    def random_value_gen(self, min, max):
        if min == max:
            return min
        val_range = range(min, max)
        return np.random.choice(val_range)

    def gen_idm_vehicles(self, gap_rane, v_range, max_vehicle_count):
        id = 0
        for lane in range(self.config['lane_count']):
        # for lane in range(self.config['lane_count']-1):
            random_x = 0
            while random_x < self.config['percept_range']*2 and id < max_vehicle_count:
                random_x += self.random_value_gen(gap_rane[0], gap_rane[1])
                random_v = self.random_value_gen(v_range[0], v_range[1])
                vehicle = IDMVehicle(id=id, lane_id=lane+1, x=random_x, v=random_v)
                self.vehicles.append(vehicle)
                id += 1


        # if self.viewer.PAUSE_CONTROL == 'on' and \
        #                 self.ego.remaining_budget == self.ego.available_budget:
        #     input("Press Enter to continue...")

    def check_terminal(self, obs):
        return obs['front_dx'] < 6 or obs['rear_dx'] < 10

    def get_reward(self, obs, terminal):
        reward = 0
        if terminal:
            reward += self.COLLISION_REWARD

        # reward -= sorted([-0.2, abs(self.sdv.v - 10), 0])[1]
        reward += -0.1*self.sdv.y
        # reward += sorted([-0.5, -0.1*self.sdv.y, 0])[1]
        return reward
