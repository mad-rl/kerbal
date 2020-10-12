import numpy as np

from .knowledge import Knowledge
from .interpreter import Interpreter
from .actuator import Actuator
from .experiences import Experiences

from logger import Logger
from mongodb import MongoDBHelper
from game_env import GameEnv


class Agent():
    def __init__(
        self,
        logger: Logger,
        mongo: MongoDBHelper,
        mode: str,
        env: GameEnv,
        model_version: str
    ):
        self.logger: Logger = logger
        self.mongo: MongoDBHelper = mongo
        self.mode: str = mode
        self.env: GameEnv = env
        self.model_version: str = model_version

        self.input_frames = 4
        # 3 actions with two moves and None action
        self.output_model = (2 * self.env.action_space.shape[0]) + 1
        self.input_model = self.input_frames * \
            self.env.observation_space.shape[0]

        self.knowledge = Knowledge(self.input_model, self.output_model)
        self.interpreter = Interpreter(frames=self.input_frames)
        self.actuator = Actuator()
        self.experiences = Experiences()

        self.total_steps = 0
        self.max_reward = 0
        self.rewards = []

    def get_action(self, observation):
        state = self.interpreter.obs_to_state(observation)
        agent_action = self.knowledge.get_action(state)

        return self.actuator.agent_to_env(agent_action)

    def add_experience(self, observation, reward, env_action, next_observation, info=None) -> dict:
        state = self.interpreter.obs_to_state(observation)
        agent_action = self.actuator.env_to_agent(env_action)
        next_state = self.interpreter.obs_to_state(next_observation)

        self.experiences.add(state, reward, agent_action, next_state)
        self.rewards.append(reward)

        return {'state': state, 'action': agent_action, 'next_state': next_state}

    def start_step(self, current_step):
        pass

    def end_step(self, current_step):
        self.episode_steps = self.episode_steps + 1
        self.total_steps = self.total_steps + 1
        pass

    def start_episode(self, current_episode):
        self.episode_steps = 0
        pass

    def end_episode(self, current_episode):
        episode_reward = np.sum(np.array(self.rewards))
        if episode_reward > self.max_reward:
            self.max_reward = episode_reward
        print(f"Episode: {current_episode}, Episode_reward: {episode_reward}, "
              f"Max_reward: {self.max_reward}, Episode_steps: {self.episode_steps}, "
              f"Total_steps: {self.total_steps}")
        self.rewards = []

    def train(self):
        if self.mode == 'learner':
            self.knowledge.train(self.experiences.get())
            self.experiences.reset()
