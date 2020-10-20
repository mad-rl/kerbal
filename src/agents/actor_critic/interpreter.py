import numpy as np

from .sensor import Sensor


class Interpreter():
    def __init__(self, n_features=3, frames=4):
        self.n_features = n_features
        self.frames = frames
        self.state = np.zeros([self.frames, self.n_features])

    def obs_to_state(self, observation):
        sensor = Sensor(observation)
        if len(self.state) == 0:
            for i in range(self.frames):
                self.state[i, :] = sensor.data
        else:
            self.state[:self.frames - 1, :] = self.state[1:, :]
            self.state[self.frames - 1, :] = sensor.data

        return self.state.tolist()

    def reset(self):
        self.state = np.zeros([self.frames, self.n_features])
