import numpy as np

from mongodb import MongoDBHelper
from rabbitmq import RabbitMQHelper, ExperienceMessage
from influxdb import InfluxDBHelper, Metric_Reward
from logger import Logger
from game_env import GameEnv

from .knowledge import Knowledge
from .interpreter import Interpreter
from .actuator import Actuator
from .experiences import Experiences


class Agent():
    def __init__(
            self,
            logger: Logger,
            mongo: MongoDBHelper,
            rabbit: RabbitMQHelper,
            influx: InfluxDBHelper,
            env: GameEnv,
            agent_mode: str,
            model_name: str,
            model_version: str,
            host: str
    ):
        self.logger: Logger = logger
        self.mongo: MongoDBHelper = mongo
        self.rabbit: RabbitMQHelper = rabbit
        self.influx: InfluxDBHelper = influx
        self.env: GameEnv = env
        self.model_name: str = model_name
        if model_version is None:
            model_version = self.mongo.last_model_file_md5
        self.model_version: str = model_version
        self.agent_mode: str = agent_mode
        self.host: str = host

        self.action_space = self.env.action_space
        self.input_frames: int = 4
        self.output_model: int = (2 * self.env.action_space) + 1
        self.input_model: int = self.input_frames * self.env.observation_space

        self.knowledge: Knowledge = Knowledge(
            self.input_model,
            self.output_model,
            self.mongo.local_model_file_name
        )
        self.interpreter: Interpreter = Interpreter(
            frames=self.input_frames
        )
        self.actuator: Actuator = Actuator()
        self.experiences: Experiences = Experiences()

        self.episodes: int = 0
        self.total_steps: int = 0
        self.episode_steps: int = 0
        self.max_reward: int = 0
        self.rewards: list = []

    def get_action(self, observation):
        state = self.interpreter.obs_to_state(observation)
        agent_action, state_value = self.knowledge.get_action(state)

        return self.actuator.agent_to_env(agent_action), state_value

    def add_experience(self, observation, reward: float, env_action, next_observation, info=None):
        state = self.interpreter.obs_to_state(observation)
        agent_action = self.actuator.env_to_agent(env_action)
        next_state = self.interpreter.obs_to_state(next_observation)

        # if self.agent_mode == "learner":
        self.influx.send_reward(
            Metric_Reward(
                self.host,
                self.model_version,
                self.episodes,
                self.episode_steps,
                reward
            )
        )

        # if self.agent_mode == "collector":
        self.rabbit.send_experience(
            ExperienceMessage(
                self.host,
                state,
                agent_action,
                reward,
                next_state
            )
        )

        self.experiences.add(state, reward, agent_action, next_state)
        self.rewards.append(reward)

    def start_step(self):
        pass

    def end_step(self):
        self.episode_steps = self.episode_steps + 1
        self.total_steps = self.total_steps + 1
        pass

    def start_episode(self):
        self.episodes = self.episodes + 1
        self.episode_steps = 0

    def start_new_trajectory(self):
        print("new trajectory to load last model version")
        local_model_filename, self.model_version = self.mongo.wait_for_new_model_version(
            self.model_name,
            self.agent_mode
        )
        print(f"local model found [{local_model_filename}]")
        self.knowledge.load_model(local_model_filename)

    def end_episode(self):
        episode_reward = np.sum(np.array(self.rewards))
        if episode_reward > self.max_reward:
            self.max_reward = episode_reward
        print(f"Episode: { self.episodes}, Episode_reward: {episode_reward}, "
              f"Max_reward: {self.max_reward}, Episode_steps: {self.episode_steps}, "
              f"Total_steps: {self.total_steps}")
        self.rewards = []

    def train(self):
        if self.agent_mode == "learner":

            print("start training")

            experiences: list = self.rabbit.get_all_experiences()
            experience: ExperienceMessage

            for experience in experiences:
                self.experiences.add(
                    experience.state,
                    experience.reward,
                    experience.action,
                    experience.next_state
                )

            self.knowledge.train(self.experiences.get())

            print(
                f"finished training of {self.experiences.count()} experiences")

            self.mongo.save_model_version(self.model_name)

        self.experiences.reset()
