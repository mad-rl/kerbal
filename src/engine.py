from agents.actor_critic.agent import Agent
from game_env import GameEnv
from logger import Logger
from rabbitmq import RabbitMQHelper, ExperienceMessage
from influxdb import InfluxDBHelper, Metric_Reward


class Engine():
    def __init__(
        self,
        logger: Logger,
        rabbit: RabbitMQHelper,
        influx: InfluxDBHelper,
        env: GameEnv,
        agent: Agent,
        episodes: int,
        max_steps: int
    ):
        self.logger: Logger = logger
        self.rabbit: RabbitMQHelper = rabbit
        self.influx: InfluxDBHelper = influx
        self.env: GameEnv = env
        self.agent: Agent = agent
        self.episodes: int = episodes
        self.max_steps: int = max_steps

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

        episode: int = 0
        while episode < self.episodes:
            episode = episode + 1
            step = 0
            while not done and step < self.max_steps:
                step = step + 1

                action = self.agent.get_action(obs)

                next_obs, reward, done, info = self.env.step(action)
                episode_reward += reward

                self.influx.send_reward(Metric_Reward(
                    self.agent.model_version,
                    'exp001',
                    episode,
                    step,
                    reward
                ))

                experience: dict = self.agent.add_experience(
                    obs, reward, action, next_obs, info)

                self.rabbit(ExperienceMessage(
                    episode,
                    step,
                    experience['state'],
                    experience['action'],
                    reward,
                    0  # TODO: add value
                ))

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
