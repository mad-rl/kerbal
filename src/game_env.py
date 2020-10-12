
import numpy as np
from gym import spaces


class GameEnv(object):
    def __init__(self, logger, krpc, saved_game_name: str):
        self.logger = logger
        self.krpc = krpc
        self.saved_game_name = saved_game_name

        self.max_alt = 45000
        action_low = np.array([-1, -1, -1])
        action_high = np.array([1, 1, 1])
        self.action_space = spaces.Box(
            action_low,
            action_high,
            dtype=np.float32
        )
        low = np.array([0, -1, -1])
        high = np.array([1, 1, 1])
        self.observation_space = spaces.Box(
            low,
            high,
            dtype=np.float32
        )

        self.last_altitude = 0

    def step(self, action):
        done = False

        self.krpc.reset_controls()

        self.choose_action(action)

        state = self.get_state()
        reward = self.get_reward()
        done = self.epoch_ending()

        return state, reward, done, {}

    def choose_action(self, action):
        if action == 0:  # do nothing action, wait
            pass
        elif action == 1:
            self.krpc.vessel.control.pitch = -1
        elif action == 2:
            self.krpc.vessel.control.pitch = 1
        elif action == 3:
            self.krpc.vessel.control.roll = -1
        elif action == 4:
            self.krpc.vessel.control.roll = 1
        elif action == 5:
            self.krpc.vessel.control.yaw = -1
        elif action == 6:
            self.krpc.vessel.control.yaw = 1
        elif action == 7:
            self.krpc.vessel.control.throttle = 0
        elif action == 8:
            self.krpc.vessel.control.throttle = 1
        elif action == 9:
            self.krpc.vessel.activate_next_stage()

    def epoch_ending(self, done):
        if self.crew() == 0:
            reward = -1
            done = True
            print('crew is dead :(')
        return reward, done

    def get_reward(self):
        reward = -0.1
        if self.krpc.get_telemetry().f_mean_altitude > self.last_altitude:
            reward = 0.1
        self.last_altitude = self.krpc.get_telemetry().f_mean_altitude
        return reward

    def reset(self):
        print(f"loading {self.saved_game_name}")
        self.krpc.load_game(self.saved_game_name)
        self.last_altitude = 0
        state = self.get_state()
        return state

    def get_state(self):
        telemetry = self.krpc.get_telemetry()
        state = telemetry.__dict__
        return state
