import numpy as np
import time
from gym.utils import seeding
from factory import safe_deepcopy_env
from abstract import AbstractPlanner, Node

class MCTSDPW(AbstractPlanner):
    """
       An implementation of Monte-Carlo Tree Search with Upper Confidence Tree exploration
       and Double Progressive Widenning.
    """
    def __init__(self):
        """
            New MCTSDPW instance.

        :param config: the mcts configuration. Use default if None.
        :param rollout_policy: the rollout policy used to estimate the value of a leaf node
        """
        self.config = self.default_config()
        super(MCTSDPW, self).__init__()

    @classmethod
    def default_config(cls):
        cfg = super().default_config()
        cfg.update({
            "temperature": 1,
            "closed_loop": True,
            "k_state": 1,
            "alpha_state": 0.3,
            "k_decision": 1,
            "alpha_decision": 0.3,
            "horizon": 7

        })
        return cfg

    def reset(self):
        self.root = DecisionNode(parent=None, planner=self)

    def get_available_decisions(self, state):
        # while abs(state.sdv.lane_offset) > 0.3:
        # if state.sdv.lane_id == 1:
        #     # most right lane
        #     return [0, 1, 2, 3, 4, 5]
        # elif state.sdv.lane_id == state.config['lane_count']:
        #     # most left lane
        #     return [0, 1, 2, 6, 7, 8]
        # else:
        return [0, 1, 2, 3, 4, 5, 6, 7, 8]
        # return [2, 8]

    def extract_belief_info(self, state, depth):
        if depth not in self.belief_info:
            self.belief_info[depth] = {}
            self.belief_info[depth]['xs'] = [veh.x for veh in state.vehicles if veh.id != 'sdv']
            self.belief_info[depth]['ys'] = [veh.y for veh in state.vehicles if veh.id != 'sdv']
        self.belief_info[depth]['xs'].extend([veh.x for veh in state.vehicles if veh.id != 'sdv'])
        self.belief_info[depth]['ys'].extend([veh.y for veh in state.vehicles if veh.id != 'sdv'])

    def extract_tree_info(self, tree_states):
        self.tree_info.append(tree_states)
            # tree_states['x'].append(state.sdv.x)
            # tree_states['y'].append(state.sdv.y)
    def run(self, state, observation):
        """
            Run an iteration of MCTSDPW, starting from a given state
        :param state: the initial environment state
        :param observation: the corresponding observation
        """
        decision_node = self.root
        total_reward = 0
        depth = 0

        state.seed(self.np_random.randint(2**30))
        terminal = False
        tree_states = {'x':[], 'y':[]}
        while depth < self.config['horizon'] and \
                (decision_node.count != 0 or decision_node == self.root) and not terminal:

            tree_states['x'].append(state.sdv.x)
            tree_states['y'].append(state.sdv.y)

            # perform an decision followed by a transition
            chance_node, decision = decision_node.get_child(state, temperature=self.config['temperature'])
            observation, reward, terminal = self.step(state, decision)
            node_observation = observation if self.config["closed_loop"] else None
            decision_node = chance_node.get_child(node_observation)

            total_reward += self.config["gamma"] ** depth * reward
            depth += 1
            self.extract_belief_info(state, depth)

        self.extract_tree_info(tree_states)

        if not terminal:
            total_reward = self.evaluate(state, total_reward, depth=depth)
        # Backup global statistics
        decision_node.backup_to_root(total_reward)

    def evaluate(self, state, total_reward=0, depth=0):
        """
            Run the rollout policy to yield a sample of the value of being in a given state.

        :param state: the leaf state.
        :param total_reward: the initial total reward accumulated until now
        :param depth: the initial simulation depth
        :return: the total reward of the rollout trajectory
        """
        for h in range(depth, self.config["horizon"]):
            decision = self.np_random.choice(self.get_available_decisions(state))
            observation, reward, terminal = self.step(state, decision)
            total_reward += self.config["gamma"] ** h * reward
            if terminal:
                break
        return total_reward


    def plan(self, state, observation):
        self.reset()
        self.tree_info = []
        self.belief_info = {}
        for i in range(100):
            self.run(safe_deepcopy_env(state), observation)

    def get_decision(self):
        """Only return the first decision, the rest is conditioned on observations"""
        chosen_decision, decision_counts = self.root.selection_rule()
        return chosen_decision, decision_counts

class DecisionNode(Node):
    K = 1.0
    """ The value function first-order filter gain"""

    def __init__(self, parent, planner):
        super(DecisionNode, self).__init__(parent, planner)
        self.value = 0
        self.k_decision = self.planner.config["k_decision"]
        self.alpha_decision = self.planner.config["alpha_decision"]

    def unexplored_decisions(self, state):
        if state is None:
            raise Exception("The state should be set before expanding a node")
        try:
            decisions = self.planner.get_available_decisions(state)
        except AttributeError:
            decisions = self.planner.get_available_decisions(state)
        return set(self.children.keys()).symmetric_difference(decisions)

    def expand(self, state):
        decision = self.planner.np_random.choice(list(self.unexplored_decisions(state)))
        self.children[decision] = ChanceNode(self, self.planner)
        return self.children[decision], decision

    def get_child(self, state, temperature=None):
        if len(self.children) == len(self.planner.get_available_decisions(state)) \
                or self.k_decision*self.count**self.alpha_decision < len(self.children):
            # select one of previously expanded decisions
            return self.selection_strategy(temperature)
        else:
            # insert a new aciton
            return self.expand(state)

    def backup_to_root(self, total_reward):
        """
            Update the whole branch from this node to the root with the total reward of the corresponding trajectory.

        :param total_reward: the total reward obtained through a trajectory passing by this node
        """
        self.update(total_reward)
        if self.parent:
            self.parent.backup_to_root(total_reward)

    def update(self, total_reward):
        """
            Update the visit count and value of this node, given a sample of total reward.

        :param total_reward: the total reward obtained through a trajectory passing by this node
        """
        self.count += 1
        self.value += 1 / self.count * (total_reward - self.value)

    def selection_strategy(self, temperature):
        """
            Select an decision according to UCB.

        :param temperature: the exploration parameter, positive or zero.
        :return: the selected decision with maximum value and exploration bonus.
        """

        decisions = list(self.children.keys())
        indexes = []
        for a in decisions:
            ucb_val = self.children[a].value +  temperature * np.sqrt(np.log(self.count / (self.children[a].count)))
            indexes.append(ucb_val)

        decision = decisions[self.random_argmax(indexes)]
        return self.children[decision], decision

    def selection_rule(self):
        if not self.children:
            return None
        # Tie best counts by best value
        decisions = list(self.children.keys())
        counts = Node.all_argmax([self.children[a].count for a in decisions])
        decision_counts = {'decisions':decisions,
                                        'counts':[self.children[a].count for a in decisions]}


        return decisions[max(counts, key=(lambda i: self.children[decisions[i]].value))], decision_counts

class ChanceNode(Node):
    K = 1.0
    """ The value function first-order filter gain"""
    def __init__(self, parent, planner):
        assert parent is not None
        super().__init__(parent, planner)
        # state progressive widenning parameters
        self.k_state = self.planner.config["k_state"]
        self.alpha_state = self.planner.config["alpha_state"]
        self.value = 0

    def expand(self, obs_id):
        self.children[obs_id] = DecisionNode(self, self.planner)

    def get_child(self, observation):
        import hashlib
        obs_id = hashlib.sha1(str(observation).encode("UTF-8")).hexdigest()[:5]
        # print(len(self.children))
        # print(observation)
        if obs_id not in self.children:
            if self.k_state*self.count**self.alpha_state < len(self.children):
                obs_id = self.planner.np_random.choice(list(self.children))
                return self.children[obs_id]
            else:
                # Add observation to the children set
                self.expand(obs_id)

        return self.children[obs_id]

    def backup_to_root(self, total_reward):
        """
            Update the whole branch from this node to the root with the total reward of the corresponding trajectory.

        :param total_reward: the total reward obtained through a trajectory passing by this node
        """
        assert self.children
        assert self.parent
        self.update(total_reward)
        self.parent.backup_to_root(total_reward)

    def update(self, total_reward):
        """
            Update the visit count and value of this node, given a sample of total reward.

        :param total_reward: the total reward obtained through a trajectory passing by this node
        """
        self.count += 1
        self.value += 1 / self.count * (total_reward - self.value)
