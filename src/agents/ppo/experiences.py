import numpy as np


class Experiences():
    def __init__(self):
        self.experiences = []

    def add(self, state, reward, agent_action, next_state):
        self.experiences.append(
            (state, reward, agent_action, next_state)
        )

    def get(self, batch_size=None):
        if not batch_size:
            return np.array(self.experiences)
        else:
            return np.array(self.experiences[batch_size])

    def reset(self):
        self.experiences = []

    def count(self):
        return len(self.experiences)
