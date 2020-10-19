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
        max_steps: int
    ):
        self.logger: Logger = logger
        self.env: GameEnv = env
        self.agent: Agent = agent
        self.episodes: int = episodes
        self.max_steps: int = max_steps

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
            self.agent.start_episode()
            for _ in range(max_episode_steps):
                self.agent.start_step()
                action, value = self.agent.get_action(obs)

                next_obs, reward, done, info = self.env.step(action)
                episode_reward += reward

                rewards.append(reward)
                global_values.append(value.item())
                self.agent.add_experience(obs, reward, action, next_obs, info)

                obs = next_obs
                total_steps += 1
                episode_steps += 1

                self.agent.end_step()

                if done:
                    global_rewards.append(episode_reward)
                    global_episodes += 1
                    episode_reward = 0
                    episode_steps = 0
                    rewards = []
                    obs = self.env.reset()
                    done = False
                    break

            self.agent.end_episode()
            self.agent.train()
