import matplotlib.pyplot as plt


class Viewer():
    def __init__(self, env_config):
        self.env_config  = env_config
        self.fig = plt.figure(figsize=(10, 2))
        self.ax = self.fig.add_subplot()
        self.itr_trees = None
        #TODO: option to record video

    def draw_scene(self, percept_origin):
        lane_cor = self.env_config['lane_width']*self.env_config['lane_count']
        self.ax.hlines(0, 0, self.env_config['lane_length'], colors='k', linestyles='solid')
        self.ax.hlines(lane_cor, 0, self.env_config['lane_length'],
                                                    colors='k', linestyles='solid')

        if self.env_config['lane_count'] > 1:
            lane_cor = self.env_config['lane_width']
            for lane in range(self.env_config['lane_count']-1):
                self.ax.hlines(lane_cor, 0, self.env_config['lane_length'],
                                                        colors='k', linestyles='--')
                lane_cor += self.env_config['lane_width']

        if percept_origin < self.env_config['percept_range']:
            self.ax.set_xlim(0, self.env_config['percept_range']*2)
        else:
            self.ax.set_xlim(percept_origin - self.env_config['percept_range'],
                                percept_origin + self.env_config['percept_range'])

        self.ax.set_yticks([])
        # plt.show()

    def draw_vehicles(self, vehicles):
        xs = [veh.x for veh in vehicles if veh.id != 'sdv']
        ys = [veh.y for veh in vehicles if veh.id != 'sdv']
        self.ax.scatter(xs, ys, s=100, marker=">", color='grey')
        self.ax.scatter(vehicles[0].x, vehicles[0].y, s=100, marker=">", color='red')

    def draw_trees(self):
        if self.itr_trees:
            for itr in self.itr_trees:
                self.ax.plot(itr['x'], itr['y'], '-o', \
                                            markersize=3, alpha=0.2, color='black')
                # self.ax.scatter(itr['x'], itr['y'])

    def draw_traffic(self, vehicles):
        ego = vehicles[0]
        self.ax.clear()
        self.draw_scene(percept_origin = ego.x)
        self.draw_vehicles(vehicles)
        self.draw_trees()
        # self.fig.show()
        plt.pause(0.0001)
