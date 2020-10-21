import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from torch.distributions.categorical import Categorical


class PPO(torch.nn.Module):
    def __init__(self, num_inputs=12, num_outputs=4):
        super(PPO, self).__init__()

        self.num_inputs = num_inputs
        self.num_outputs = num_outputs

        self.model_structure()
        self.train()

    def model_structure(self):
        self.fc1 = nn.Linear(self.num_inputs, 120)
        self.fc2 = nn.Linear(120, 60)
        self.fc3 = nn.Linear(60, 30)

        self.relu = nn.ReLU()

        self.value = nn.Linear(30, 1)
        self.policy = nn.Linear(30, self.num_outputs)

    def forward(self, inputs):
        x = inputs.view(-1, self.num_inputs)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))

        return self.policy(x), self.value(x)


class Knowledge():
    def __init__(self, input_frames, action_space, local_model_file_name: str):
        self.input_frames = input_frames
        self.action_space = action_space
        self.local_model_file_name = local_model_file_name
        self.model = PPO(self.input_frames, self.action_space)
        self.model.double()
        self.model = self.model.to('cpu')

        self.gamma = 0.9
        self.tau = 1.0
        self.entropy_coef = 0.01
        self.learning_rate = 0.00001
        self.batch_size = 16
        self.epochs = 10
        self.clip_grad_norm = 0.5
        self.ppo_eps = 0.1

        self.optimizer = optim.Adam(self.model.parameters(),
                                    lr=self.learning_rate)

    def get_action(self, state):
        policy, value = self.model(torch.tensor(np.array(state)).unsqueeze(0))
        action = F.softmax(policy, -1).multinomial(num_samples=1)

        return action, value

    def load_model(self, filename: str):
        if filename is not None:
            self.model.load_state_dict(torch.load(filename))
            self.model.eval()

    def train(self, experiences):
        states = torch.tensor(experiences[:, 0].tolist()).double()
        rewards = torch.tensor(experiences[:, 1].tolist()).double()
        actions = torch.tensor(experiences[:, 2].tolist()).long()
        next_states = torch.tensor(experiences[:, 3].tolist()).double()

        logits, values = self.model(states)
        probs = F.softmax(logits, -1)
        log_probs = F.log_softmax(logits, -1)
        entropies = -(log_probs * probs).sum(1, keepdim=True)
        log_probs = log_probs.gather(1, actions.unsqueeze(1))

        _, value = self.model(next_states[-1].unsqueeze(0))
        values = torch.cat((values, value.data))

        # Calculate Generalized Advantage Estimation
        num_step = len(rewards)
        discounted_return = np.empty([num_step])
        R = values[-1]
        gae = torch.zeros(1, 1)
        for i in reversed(range(len(rewards))):
            delta_t = (rewards[i] +
                       self.gamma * values[i + 1].data -
                       values[i].data)

            gae = gae.double() * self.gamma * self.tau + delta_t
            discounted_return[i] = gae + values[i]

        # Calculate advantages for Actor
        adv = discounted_return - values.detach().numpy()

        with torch.no_grad():
            # for multiplying advantage
            policy_old, value_old = self.model(states)
            prob_distribution = Categorical(F.softmax(policy_old, dim=-1))
            log_prob_old = prob_distribution.log_prob(actions)

        sample_range = np.arange(len(states))
        for i in range(self.epochs):
            np.random.shuffle(sample_range)
            for j in range(int(len(states) / self.batch_size)):
                idx_from = self.batch_size * j
                idx_to = self.batch_size * (j + 1)
                sample_idx = sample_range[idx_from:idx_to]

                policy, value = self.model(states[sample_idx])
                prob_distribution = Categorical(F.softmax(policy, dim=-1))
                log_prob = prob_distribution.log_prob(actions[sample_idx])

                ratio = torch.exp(log_prob - log_prob_old[sample_idx])
                surr1 = ratio * adv[sample_idx]
                surr2 = (torch.clamp(ratio, 1.0 - self.ppo_eps, 1.0 + self.ppo_eps) * adv[sample_idx])

                actor_loss = -torch.min(surr1, surr2).mean()
                critic_loss = F.mse_loss(value.sum(1), discounted_return[sample_idx])

                self.optimizer.zero_grad()
                loss = actor_loss + critic_loss
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.clip_grad_norm)
                self.optimizer.step()

        torch.save(self.model.state_dict(), self.local_model_file_name)
