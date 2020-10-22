import time
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
            _steps: int = 0
            while not done:
                self.agent.start_new_trajectory()

                # _trajectory_time = time.time()

                for _ in range(self.max_trajectory_steps):

                    # _old_time = time.time()
                    # _step_time = time.time()

                    _steps = _steps + 1

                    # print(f"elapsed_time_A[{time.time()-_old_time}]")
                    # _old_time = time.time()

                    self.agent.start_step()
                    action, value = self.agent.get_action(obs)

                    # print(f"elapsed_time_B[{time.time()-_old_time}]")
                    # _old_time = time.time()

                    next_obs, reward, done, info = self.env.step(action)
                    episode_reward += reward

                    # print(f"elapsed_time_C[{time.time()-_old_time}]")
                    # _old_time = time.time()

                    rewards.append(reward)
                    global_values.append(value.item())
                    self.agent.add_experience(
                        obs, reward, action, next_obs, info)

                    # print(f"elapsed_time_D[{time.time()-_old_time}]")
                    # _old_time = time.time()

                    obs = next_obs
                    self.agent.end_step()

                    # print(f"elapsed_time_E[{time.time()-_old_time}]")
                    # _old_time = time.time()

                    print(
                        f"episode[{current_episode}] step[{_steps}] episode_reward [{episode_reward}]")

                    if done is True:
                        break

                # print(f"trajectory time [{time.time()-_trajectory_time}]")

                _training_time = time.time()
                self.agent.train()
                print(f"training time [{time.time()-_training_time}]")

            done = False
            global_rewards.append(episode_reward)
            episode_reward = 0
            rewards = []
            obs = self.env.reset()
            self.agent.end_episode()
