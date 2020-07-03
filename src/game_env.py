from krpc_helper import KRPCHelper
from settings import Settings


class GameEnv(object):
    def __init__(self, settings: Settings):
        self.kh = KRPCHelper(settings)
        self.settings = settings
        self.action_space  # TODO: Define Action Space
        self.observation_space  # TODO: Define Observation Space

        self.last_altitude = 0

    def step(self, action):
        done = False

        self.kh.reset_controls()

        self.choose_action(action)

        state = self.get_state()
        reward = self.get_reward()
        done = self.epoch_ending()

        return state, reward, done, {}

    def choose_action(self, action):
        if action == 0:  # do nothing action, wait
            pass
        elif action == 1:
            self.kh.vessel.control.pitch = -1
        elif action == 2:
            self.kh.vessel.control.pitch = 1
        elif action == 3:
            self.kh.vessel.control.roll = -1
        elif action == 4:
            self.kh.vessel.control.roll = 1
        elif action == 5:
            self.kh.vessel.control.yaw = -1
        elif action == 6:
            self.kh.vessel.control.yaw = 1
        elif action == 7:
            self.kh.vessel.control.throttle = 0
        elif action == 8:
            self.kh.vessel.control.throttle = 1
        elif action == 9:
            self.kh.vessel.activate_next_stage()

    def epoch_ending(self, done):
        if self.crew() == 0:
            reward = -1
            done = True
            print('crew is dead :(')
        return reward, done

    def get_reward(self):
        reward = -0.1
        if self.kh.get_telemetry().f_mean_altitude > self.last_altitude:
            reward = 0.1
        self.last_altitude = self.kh.get_telemetry().f_mean_altitude
        return reward

    def reset(self):
        self.kh.load_game()
        self.last_altitude = 0
        state = self.get_state()
        return state

    def get_state(self):
        telemetry = self.kh.get_telemetry()
        state = telemetry.__dict__
        return state
