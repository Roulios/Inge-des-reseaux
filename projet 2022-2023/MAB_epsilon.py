import pandas as pd
import numpy as np

class EpsilonGreedy:
  def __init__(self, num_arms, epsilon):
    self.num_arms = num_arms
    self.epsilon = epsilon
    self.counts = [0] * num_arms
    self.values = [0.] * num_arms

  def select_arm(self):
    if np.random.random() < self.epsilon:
      return np.random.randint(self.num_arms)
    else:
      return np.argmax(self.values)

  def update(self, chosen_arm, reward):
    self.counts[chosen_arm] += 1
    n = self.counts[chosen_arm]
    value = self.values[chosen_arm]
    new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
    self.values[chosen_arm] = new_value

# Load data
data = pd.read_csv('simulation_metrics.csv', header=None)
print(data)

# Extract V2V and V2I metrics
# Extract V2V metrics
v2v_delay = data.iloc[0, 0]
v2v_loss_rate = data.iloc[0, 1]
v2v_load = data.iloc[0, 2]

# Extract V2I metrics
v2i_delay = data.iloc[1, 0]
v2i_loss_rate = data.iloc[1, 1]
v2i_load = data.iloc[1, 2]

# Invert metrics to use as rewards and apply weights
# Weights
delay_weight = 1
loss_rate_weight = 1
load_weight = 0.2

# V2V
v2v_delay_reward = delay_weight / v2v_delay
v2v_loss_rate_reward = loss_rate_weight / v2v_loss_rate
v2v_load_reward = load_weight / v2v_load

# V2I
v2i_delay_reward = delay_weight / v2i_delay
v2i_loss_rate_reward = loss_rate_weight / v2i_loss_rate
v2i_load_reward = load_weight / v2i_load

# Initialize Epsilon-Greedy for each mode
epsilon = 0.1  # Adjust the epsilon value as needed
eg_v2v = EpsilonGreedy(3, epsilon)  # 3 arms for delay, loss rate, and load
eg_v2i = EpsilonGreedy(3, epsilon)  # 3 arms for delay, loss rate, and load

# Update Epsilon-Greedy with rewards for each mode
eg_v2v.update(0, v2v_delay_reward)
eg_v2v.update(1, v2v_loss_rate_reward)
eg_v2v.update(2, v2v_load_reward)

eg_v2i.update(0, v2i_delay_reward)
eg_v2i.update(1, v2i_loss_rate_reward)
eg_v2i.update(2, v2i_load_reward)

# Select best arm for each mode
best_v2v = eg_v2v.select_arm()
best_v2i = eg_v2i.select_arm()

# Get the chosen communication mode based on the best arms
chosen_mode = 'V2V' if eg_v2v.values[best_v2v] > eg_v2i.values[best_v2i] else 'V2I'

print("Chosen Communication Mode:", chosen_mode)
