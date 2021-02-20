import matplotlib.pyplot as plt


class Highway_scene():
    def __init__(self):
        self.default_config()
        self.draw_scene()
        #TODO: option to record video

    def default_config(self):
        self.config = {'lane_count':5,
                        'lane_width':3.7, # m
                        'lane_length':10000, # m
                        'percept_size':70, # m, front and back
                        }
        self.fig = plt.figure(figsize=(10, 2))
        self.ax = self.fig.add_subplot()

    def draw_scene(self):
        lane_cor = self.config['lane_width']*self.config['lane_count']
        self.ax.hlines(0, 0, self.config['lane_length'], colors='k', linestyles='solid')
        self.ax.hlines(lane_cor, 0, self.config['lane_length'],
                                                    colors='k', linestyles='solid')

        if self.config['lane_count'] > 1:
            lane_cor = self.config['lane_width']
            for lane in range(self.config['lane_count']-1):
                self.ax.hlines(lane_cor, 0, self.config['lane_length'],
                                                        colors='k', linestyles='--')
                lane_cor += self.config['lane_width']
        self.ax.set_xlim(0, self.config['percept_size']*2)

        self.ax.set_yticks([])
        plt.show()
