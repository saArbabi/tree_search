import numpy as np

"""
np.arrange(0, 20)
np.random.choice(range(20), 10)
random_x = np.random.choice(range(1, 21), 10)
sorted_x = np.sort(random_x)

sorted_x
np.diff(sorted_x)
indx = np.argwhere(np.diff(sorted_x)>3)

"""
class SimVehicles():
    def __init__(self):
        self.default_config()

    def default_config(self):
        self.config = {
                        'min_spacing':20, # m
                        'min_speed':12,
                        'max_speed':15,
                        }
    def scene_initialisation():
        """
        Initiates the scene for a given specification.
        return: dataframe with randomly generated vehicles.
        {veh_id, follower, leader, lane, x, y, v,IDM-param}
        TODO: Add vehicles' observation - it will be needed eventually for learned IDM.
        """
        random_x = np.random.choice(range(1, 21), 10)
        sorted_x = np.sort(random_x)

import pandas as pd
df = pd.DataFrame()
df['id'] = [1,2,3,4]
df['x'] = [1,2,3,4]
df
