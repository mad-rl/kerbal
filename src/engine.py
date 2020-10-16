import numpy as np
import os

from agents.actor_critic.agent import Agent
from game_env import GameEnv
from logger import Logger
from settings import Settings


class Worker(object):
    def __init__(self):
        self.settings: Settings = Settings(os.getenv("SETTINGS_PATH"))
        self.env = GameEnv(self.settings)
        self.logger: Logger = Logger(self.settings)

        self.agent = Agent(
            action_space=self.env.action_space,
            observation_space=self.env.observation_space)

    def run(self):
        global_rewards: list = []
        global_values: list = []
        global_episodes: int = 0

        done: bool = False
        rewards: list = []
        episode_reward: int = 0
        episode_steps: int = 0
        total_steps: int = 0

        max_episode_steps = 50
        obs = self.env.reset()

        while not done:
            for _ in range(max_episode_steps):
                action, value = self.agent.get_action(obs)

                next_obs, reward, done, info = self.env.step(action)
                episode_reward += reward

                rewards.append(reward)
                global_values.append(value.item())
                self.agent.add_experience(obs, reward, action, next_obs, info)

                obs = next_obs
                total_steps += 1
                episode_steps += 1

                if done:
                    global_rewards.append(episode_reward)
                    altitude = self.env.last_altitude

                    self.logger.print({
                            "global_episodes": global_episodes,
                            "total_steps": total_steps,
                            "global_rewards": global_rewards,
                            "episode_steps": episode_steps,
                            "episode_reward": episode_steps,
                            "altitude": altitude
                        })

                    global_episodes += 1
                    episode_reward = 0
                    episode_steps = 0
                    rewards = []
                    obs = self.env.reset()
                    done = False
                    break

            self.agent.train()


if __name__ == "__main__":
    worker = Worker()
    worker.run()
