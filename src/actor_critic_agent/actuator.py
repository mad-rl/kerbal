import numpy as np


ACTIONS_LABELS = [
    'NOTHING', 'PITCH-1', 'PITCH+1', 'ROLL-1', 'ROLL+1', 'YAW-1', 'YAW+1'
]


class Actuator():
    def __init__(self):
        self.action = 0

    def agent_to_env(self, agent_action):
        self.action = agent_action.item()
        return self.action

    def env_to_agent(self, env_action):
        return self.action
