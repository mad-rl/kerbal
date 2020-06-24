import numpy as np
import os

import krpc

from game_env import GameEnv

conns = [
   {'name': "Test", "address": "127.0.0.1", "rpc_port": 50000, "stream_port": 50001},
]

N_WORKERS = len(conns)
MAX_EP_STEP = 200000
GLOBAL_NET_SCOPE = 'Global_Net'
UPDATE_GLOBAL_ITER = 10
GAMMA = 0.90
ENTROPY_BETA = 0.01
LR_A = 0.0001
LR_C = 0.001

print(conns)
connections = [krpc.connect(**conns[i]) for i in range(N_WORKERS)]


class Worker(object):
    def __init__(self, name, conn):
        self.conn = conn
        self.env = GameEnv(conn=self.conn)
        self.name = name

    def work(self):
        global global_rewards, global_episodes
        total_step = 1
        buffer_s, buffer_a, buffer_r = [], [], []

        done = False
        while not done:
            s = self.env.reset(self.conn)
            ep_r = 0
            self.env.activate_engine()

            for ep_t in range(MAX_EP_STEP):
                a = np.random.randint(4, size=1)[0]

                s_, r, done, info = self.env.step(a)  # make step in environment
                print("Action: ", a)
                print("State: ", s)
                print("Reward: ", r)
                print("Next state: ", s_)

                ep_r += r
                buffer_s.append(s)
                buffer_a.append(a)
                buffer_r.append(r)

                s = s_
                total_step += 1
                print(ep_t)
                if done:
                    global_rewards.append(ep_r)
                    self.save_results(ep_r, global_episodes, global_rewards)
                    global_episodes += 1
                    done = False
                    break

    def save_results(self, ep_r, global_episodes, global_rewards):
        altitude = self.env.get_altitude()

        print(
            self.name,
            "Episode: {:4}".format(global_episodes),
            "| Reward: {:7.1f}".format(global_rewards[-1]),
            "| Altitude: {:7.1f}".format(altitude)
        )


if __name__ == "__main__":
    global_rewards = []
    global_episodes = 0

    print("Launching testing process")

    test_worker = Worker("Test", connections[0])
    test_worker.work()
