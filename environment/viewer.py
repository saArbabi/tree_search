import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

class Viewer():
    def __init__(self, env_config):
        self.env_config  = env_config
        self.fig = plt.figure(figsize=(7, 7))
        self.env_ax = self.fig.add_subplot(211)
        self.decision_bar_ax = self.fig.add_subplot(212)
        self.tree_info = None
        self.belief_info = None
        self.decision_counts = None
        #TODO: option to record video

    def draw_scene(self, ax, percept_origin):
        lane_cor = self.env_config['lane_width']*self.env_config['lane_count']
        ax.hlines(0, 0, self.env_config['lane_length'], colors='k', linestyles='solid')
        ax.hlines(lane_cor, 0, self.env_config['lane_length'],
                                                    colors='k', linestyles='solid')

        if self.env_config['lane_count'] > 1:
            lane_cor = self.env_config['lane_width']
            for lane in range(self.env_config['lane_count']-1):
                ax.hlines(lane_cor, 0, self.env_config['lane_length'],
                                                        colors='k', linestyles='--')
                lane_cor += self.env_config['lane_width']

        if percept_origin < self.env_config['percept_range']:
            ax.set_xlim(0, self.env_config['percept_range']*2)
        else:
            ax.set_xlim(percept_origin - self.env_config['percept_range'],
                                percept_origin + self.env_config['percept_range'])

        ax.set_yticks([])
        # plt.show()

    def draw_vehicles(self, ax, vehicles):
        xs = [veh.x for veh in vehicles if veh.id != 'sdv']
        ys = [veh.y for veh in vehicles if veh.id != 'sdv']
        ax.scatter(xs, ys, s=100, marker=">", color='grey')
        ax.scatter(vehicles[0].x, vehicles[0].y, s=100, marker=">", color='red')

    def draw_beliefs(self, ax):
        if self.belief_info:
            max_depth = len(self.belief_info)
            colors = cm.rainbow(np.linspace(1, 0, max_depth))
            depth = 1
            for c in colors:
                ax.scatter(self.belief_info[depth]['xs'], self.belief_info[depth]['ys'], color=c, s=10)
                depth += 1

    def draw_trees(self, ax):
        if self.tree_info:
            for itr in self.tree_info:
                ax.plot(itr['x'], itr['y'], '-o', \
                                            markersize=3, alpha=0.2, color='black')
                # self.env_ax.scatter(itr['x'], itr['y'])
    def draw_decision_counts(self, ax, sdv):
        if self.decision_counts:
            ax.clear()
            decisions = self.decision_counts['decisions']
            counts =  self.decision_counts['counts']

            poses = np.arange(len(self.decision_counts['decisions']))
            lat_labels = [sdv.OPTIONS.get(key) for key in self.decision_counts['decisions']]
            lat_labels = [item[0]+'_'+item[1] for item in lat_labels]


            colors = ['green' if val == max(self.decision_counts['counts']) else \
                                    'grey' for val in self.decision_counts['counts']]

            ax.set_xticks(poses)
            ax.set_xticklabels(lat_labels, rotation=90)
            fig_obj = ax.bar(poses, self.decision_counts['counts'], align='center', \
                                                    width=0.5, color=colors)

    def draw_env(self, ax, vehicles):
        sdv = vehicles[0]
        ax.clear()
        self.draw_scene(ax, percept_origin = sdv.x)
        self.draw_vehicles(ax, vehicles)
        self.draw_trees(ax)
        self.draw_beliefs(ax)

    def update_plots(self, vehicles):
        sdv = vehicles[0]
        self.draw_env(self.env_ax, vehicles)
        self.draw_decision_counts(self.decision_bar_ax, sdv)
        plt.pause(0.0001)
