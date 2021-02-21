# from agents import Vehicle, EgoVehicle
from environment.env import Env
import numpy as np
from vehicles.sd_vehicle import SDVehicle

# from graphics import Viewer
# Highway_scene()
import matplotlib.pyplot as plt
# %%
# %%
from vehicles.idm_vehicle import IDMVehicle

env = Env()
# viewer = Viewer(env)
# viewer.plotlive()

# v1 = IDMVehicle(id=1, lane_id=3, x=18, v=10)
# v2 = IDMVehicle(id=2, lane_id=3, x=20, v=10)
env.sdv = SDVehicle(id='sdv', lane_id=5, x=20, v=10, env=env)
env.vehicles.append(env.sdv)
env.gen_idm_vehicles(gap_min=20, gap_max=30, v_min=10, v_max=12)

obs = env.reset()
env.render()

for i in range(30):
    # env.render()
    itr_trees = env.sdv.planner.plan(env, obs) # TODO, get visualisation outputs
    decision = env.sdv.planner.get_decision()
    env.viewer.itr_trees = itr_trees
    env.render()
    input("Press Enter to step to the next state ...")
    obs, reward, terminal = env.step(decision)

# %%

# %%
