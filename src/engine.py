from agents.actor_critic.agent import Agent
from game_env import GameEnv
from logger import Logger


class Engine():
    def __init__(
        self,
        logger: Logger,
        env: GameEnv,
        agent: Agent,
        episodes: int,
        max_trajectory_steps: int
    ):
        self.logger: Logger = logger
        self.env: GameEnv = env
        self.agent: Agent = agent
        self.episodes: int = episodes
        self.max_trajectory_steps: int = max_trajectory_steps

    def run(self):
        global_rewards: list = []
        global_values: list = []

        done: bool = False
        rewards: list = []
        episode_reward: int = 0

        obs = self.env.reset()

        current_episode: int = 0
        for current_episode in range(self.episodes):
            current_episode = current_episode + 1
            self.agent.start_episode()
            while not done:
                self.agent.start_new_trajectory()
                for _ in range(self.max_trajectory_steps):
                    self.agent.start_step()
                    action, value = self.agent.get_action(obs)

                    next_obs, reward, done, info = self.env.step(action)
                    episode_reward += reward

                    rewards.append(reward)
                    global_values.append(value.item())
                    self.agent.add_experience(
                        obs, reward, action, next_obs, info)

                    obs = next_obs
                    self.agent.end_step()

                    if done is True:
                        break

                self.agent.train()

            done = False
            global_rewards.append(episode_reward)
            episode_reward = 0
            rewards = []
            obs = self.env.reset()
            self.agent.end_episode()
