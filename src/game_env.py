# Adapted from https://github.com/under-control/flytosky/blob/master/ksp_env.py
import math
import time

import numpy as np
import pandas as pd

from krpc_helper import KRPCHelper
from physics import angle_between_vectors
from settings import Settings


class GameEnv(object):
    def __init__(self, settings: Settings):
        self.kh = KRPCHelper(settings)
        self.settings = settings
        self.total_steps = 0

        self.action_space = 2
        self.observation_space = 3

        self.last_altitude = 0
        self.last_pitch = 0
        self.last_heading = 0
        self.max_altitude = 45000
        self.steps_limit = 450

        self.ground_truth = pd.read_csv("artifacts/groundtruth.csv")

    def step(self, action):
        done = False

        self.total_steps += 1

        self.kh.reset_controls()
        self.choose_action(action)

        state = self.get_state()
        reward = self.get_reward()
        done = self.epoch_ending()

        return state, reward, done, {}

    def choose_action(self, action):
        if action == 0:
            pass
        elif action == 1:
            self.kh.vessel.control.pitch = -1
        elif action == 2:
            self.kh.vessel.control.pitch = 1
        elif action == 3:
            self.kh.vessel.control.yaw = -1
        elif action == 4:
            self.kh.vessel.control.yaw = 1

    def epoch_ending(self):
        altitude = self.kh.get_telemetry().f_mean_altitude
        crew_count = self.kh.get_telemetry().crew_count()

        done = False
        if crew_count == 0:
            done = True
        elif self.total_steps > self.steps_limit:
            done = True
        elif altitude >= self.max_altitude:
            done = True

        return done

    def pre_launch_setup(self):
        self.kh.vessel.control.sas = False
        self.kh.vessel.control.rcs = False

        self.altitude_max = 0
        self.counter = 0
        self.prev_pitch = 90
    
    def activate_engine(self, throttle=1.0):
        self.kh.vessel.control.throttle = throttle
        self.kh.vessel.control.activate_next_stage()
        time.sleep(2)

    def reset(self):
        self.kh.load_game()
        self.pre_launch_setup()
        self.activate_engine()

        self.last_altitude = 0
        self.last_pitch = 0
        self.last_heading = 0
        self.total_steps = 0
        state = self.get_state()

        return state

    def get_state(self):
        altitude = self.kh.get_telemetry().f_mean_altitude
        heading = self.kh.get_telemetry().heading()
        pitch = self.kh.get_telemetry().pitch()

        state = [
            ((altitude + 0.2) / self.max_altitude) / 1.2,
            math.sin(math.radians(heading)) * (90 - pitch) / 90,
            math.cos(math.radians(heading)) * (90 - pitch) / 90,
        ]

        return state

    def get_reward(self):
        # Calculate the rewards related to GroundTruth - Altitude
        gt_altitude = self.ground_truth['altitude'].values[self.total_steps]
        altitude_rewards = (gt_altitude - self.last_altitude) / gt_altitude
        altitude_rewards = np.abs(altitude_rewards)

        # Calcultae the rewards related to GroundTruth - Pitch
        gt_pitch = self.ground_truth['pitch'].values[self.total_steps]
        pitch_rewards = (gt_pitch - self.last_pitch) / gt_pitch
        pitch_rewards = np.abs(pitch_rewards)

        reward = (0.5 * altitude_rewards) + (0.5 * pitch_rewards)
        reward = -reward

        return reward
