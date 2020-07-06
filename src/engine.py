import os 
from agents.actor_critic_agent.agent import Agent
from game_env import GameEnv
from settings import Settings
from logger import Logger


class Worker(object):
    def __init__(self):
        self.settings: Settings = Settings(os.getenv("SETTINGS_PATH"))
        self.env = GameEnv(self.settings)

        self.logger: Logger = Logger()

        self.agent = Agent(
            action_space=self.env.action_space.shape[0],
            observation_space=self.env.observation_space.shape[0])

    def run(self):
        global_rewards: list = []
        global_episodes: list = []

        done: bool = False
        reward: int = 0
        episode_reward: int = 0
        total_steps: int = 0
        episode_steps: int = 0
        next_obs: list = []
        info: dict = {}
        action: int = 0

        obs = self.env.reset()

        while not done:
            for _ in range(self.settings.max_episode_steps):
                action = self.agent.get_action(obs)

                next_obs, reward, done, info = self.env.step(action)
                episode_reward += reward

                self.agent.add_experience(obs, reward, action, next_obs, info)

                obs = next_obs
                total_steps += 1
                episode_steps += 1

                if done:
                    global_rewards.append(episode_reward)

                    self.logger.print({
                        "global_episodes": global_episodes,
                        "total_steps": total_steps,
                        "global_rewards": global_rewards,
                        "episode_steps": episode_steps,
                        "episode_reward": episode_steps
                    })

                    global_episodes += 1
                    episode_reward = 0
                    episode_steps = 0
                    obs = self.env.reset()
                    done = False
                    break

            self.agent.train()


if __name__ == "__main__":
    worker = Worker()
    worker.work()
