
class Sensor():
    def __init__(self, observation):
        self.data = self.preprocess_obs(observation)

    def preprocess_obs(self, observation):
        # TODO - Normalize the input features?
        obs_preprocessed = observation
        return obs_preprocessed
