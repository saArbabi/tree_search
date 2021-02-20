from controllers.idm import IDMControl
from vehicles.vehicle import Vehicle

class IDMVehicle(Vehicle):
    def __init__(self, lane_id, x, v, idm_param=None):
        super().__init__(lane_id, x, v)
        if not idm_param:
            self.default_config()

        else:
            self.idm_param = idm_param

        self.leader = None # specify before acting
        self.controller = IDMControl(self.idm_param)
        # TODO params can also be learned
    def default_config(self):
        # TODO nonstationary params
        self.idm_param = {
                        'desired_v':self.v, # m/s
                        'desired_tgap':2.8, # s
                        'min_jamx':0, # m
                        'max_acc':3, # m/s^2
                        'max_decc':3, # m/s^2
                        }
    def act(self):
        return self.controller.act(self.state , self.leader.state)
