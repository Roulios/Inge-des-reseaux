import pandas as pd
import numpy as np
import math

class UCB:
  def __init__(self, num_arms):
    self.num_arms = num_arms
    self.counts = [0] * num_arms
    self.values = [0.] * num_arms

  def select_arm(self):
    for arm in range(self.num_arms):
      if self.counts[arm] == 0:
        return arm

    ucb_values = [0.0 for arm in range(self.num_arms)]
    total_counts = sum(self.counts)
    for arm in range(self.num_arms):
      bonus = math.sqrt((2 * math.log(total_counts)) / float(self.counts[arm]))
      ucb_values[arm] = self.values[arm] + bonus
    return ucb_values.index(max(ucb_values))

  def update(self, chosen_arm, reward):
    self.counts[chosen_arm] += 1
    n = self.counts[chosen_arm]

    value = self.values[chosen_arm]
    new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
    self.values[chosen_arm] = new_value

# Load data
data = pd.read_csv('simulation_metrics.csv', sep=',', header=None)
print(data)


# Extract V2V and V2I metrics
v2v_delay = data.iloc[0, 0]
v2v_loss_rate = data.iloc[0, 1]
v2v_load = data.iloc[0, 2]

v2i_delay = data.iloc[1, 0]
v2i_loss_rate = data.iloc[1, 1]
v2i_load = data.iloc[1, 2]

# Invert metrics to use as rewards
v2v_delay = 1 / v2v_delay
v2v_loss_rate = 1 / v2v_loss_rate
v2v_load = 1 / v2v_load

v2i_delay = 1 / v2i_delay
v2i_loss_rate = 1 / v2i_loss_rate
v2i_load = 1 / v2i_load

# Initialize UCB for each metric
ucb_v2v_delay = UCB(1)
ucb_v2v_loss_rate = UCB(1)
ucb_v2v_load = UCB(1)

ucb_v2i_delay = UCB(1)
ucb_v2i_loss_rate = UCB(1)
ucb_v2i_load = UCB(1)

# Update UCB with rewards for each metric
ucb_v2v_delay.update(0, v2v_delay)
ucb_v2v_loss_rate.update(0, v2v_loss_rate)
ucb_v2v_load.update(0, v2v_load)

ucb_v2i_delay.update(0, v2i_delay)
ucb_v2i_loss_rate.update(0, v2i_loss_rate)
ucb_v2i_load.update(0, v2i_load)

# Select best arm for each metric
best_v2v_delay = ucb_v2v_delay.select_arm()
best_v2v_loss_rate = ucb_v2v_loss_rate.select_arm()
best_v2v_load = ucb_v2v_load.select_arm()

best_v2i_delay = ucb_v2i_delay.select_arm()
best_v2i_loss_rate = ucb_v2i_loss_rate.select_arm()
best_v2i_load = ucb_v2i_load.select_arm()

# Define weights for each metric
weight_delay = 1.0
weight_loss_rate = 1.0
weight_load = 0.2

# Get the chosen communication mode based on the best arms and their weights
v2v_score = weight_delay * ucb_v2v_delay.values[best_v2v_delay] + weight_loss_rate * ucb_v2v_loss_rate.values[best_v2v_loss_rate] + weight_load * ucb_v2v_load.values[best_v2v_load]
v2i_score = weight_delay * ucb_v2i_delay.values[best_v2i_delay] + weight_loss_rate * ucb_v2i_loss_rate.values[best_v2i_loss_rate] + weight_load * ucb_v2i_load.values[best_v2i_load]

chosen_mode = 'V2V' if v2v_score > v2i_score else 'V2I'

print("Chosen Communication Mode:", chosen_mode)