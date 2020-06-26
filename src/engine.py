import numpy as np
import os

import krpc

from actor_critic_agent.agent import Agent
from game_env import GameEnv


class Worker(object):
    def __init__(self, name, conn):
        self.conn = conn
        self.env = GameEnv(conn=self.conn)
        self.name = name

        self.agent = Agent(
            action_space=self.env.action_space.shape[0],
            observation_space=self.env.observation_space.shape[0])

    def work(self):
        global global_rewards, global_episodes

        max_episode_steps = 50
        obs = self.env.reset(self.conn)

        done = False
        episode_reward = 0
        total_steps = 0
        episode_steps = 0
        while not done:
            for _ in range(max_episode_steps):
                action = self.agent.get_action(obs)

                next_obs, reward, done, info = self.env.step(action)
                episode_reward += reward

                self.agent.add_experience(obs, reward, action, next_obs, info)

                obs = next_obs
                total_steps += 1
                episode_steps += 1

                if done:
                    global_rewards.append(episode_reward)
                    altitude = self.env.get_altitude()

                    print(f"{self.name} - Episode: {global_episodes:4} "
                        f"| Total Steps: {total_steps}"
                        f"| Episode Steps: {episode_steps}"
                        f"| Reward: {global_rewards[-1]:7.1f}" 
                        f"| Altitude: {altitude:7.1f}")

                    global_episodes += 1
                    episode_reward = 0
                    episode_steps = 0
                    obs = self.env.reset(self.conn)
                    done = False
                    break

            print("Training agent...")
            self.agent.train()


if __name__ == "__main__":
    name = "MAD_RL_Agent"
    conns = [
        {'name': name, "address": "127.0.0.1", "rpc_port": 50000, "stream_port": 50001},
    ]
    connections = [krpc.connect(**conns[0])]
    
    global_rewards = []
    global_episodes = 0

    print("Starting process")

    worker = Worker(name, connections[0])
    worker.work()
