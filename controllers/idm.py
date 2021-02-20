import numpy as np

class IDMControl():
    def __init__(self, idm_param):
        self.idm_param = idm_param
        self.desired_v = idm_param['desired_v']
        self.desired_tgap = idm_param['desired_tgap']
        self.min_jamx = idm_param['min_jamx']
        self.max_acc = idm_param['max_acc']
        self.max_decc = idm_param['max_decc']

    def get_desired_gap(self, v_fv, v_lv):
        dv = v_lv - v_fv
        g = self.min_jamx + self.desired_tgap*v_fv+(v_fv*dv)/ \
                                        (2*np.sqrt(self.max_acc*self.max_decc))
        return g

    def act(state_fv, state_lv):
        """Outputs IDM's action for the current state. Note there is no lateral action.
        param: state_fv, state_lv contain relevant state info for the idm
        """
        # 'v_fv',
        # 'v_lv',
        # 'x',
        # dx =
        desired_gap = self.get_desired_gap(v_fv, v_lv)
        acc = self.max_acc*(1-(v_fv/self.desired_v)**4-\
                                            (desired_gap/dx)**2)

        return [acc, 0]
