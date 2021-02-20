
class Vehicle(object):
    STEP_SIZE = 0.1 # s update rate - used for dynamics
    def __init__(self, lane_id, x, v):
        self.v = v # longitudinal speed [m/s]
        self.lane_id = lane_id # inner most right is 1
        self.y = 0 # lane relative
        self.x = x # global coordinate

    def act(self):
        """
        :param high-lev decision of the car
        """
        pass

    def update_lane(self):
        if self.y >= 1.85 and action[1] > 0:
            self.lane_id += 1
            self.y = -self.y + y_delta

        if self.y <= -1.85 and action[1] < 0:
            self.lane_id -= 1
            self.y = -self.y + y_delta

    def act(self):
        raise NotImplementedError

    def step(self, action):
        """Defines simple vehicle dynamics.
        param: action: [long_acc, lat_speed]
        """
        self.x = self.x + self.v * self.step_size \
                                    + 0.5 * action[0] * self.step_size **2

        y_delta = action[1]*self.step_size
        self.y += y_delta
        self.v = self.v + action[0] * self.step_size
        self.update_lane(self)
