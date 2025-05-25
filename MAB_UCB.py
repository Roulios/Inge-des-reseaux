import numpy as np
import math
from MAB_signature import MAB

import Utils

class UCB(MAB):
  def __init__(self,n_arms,weight):
    super().__init__(n_arms,weight)

  @MAB.complete_arm_history
  def select_arm(self):
    for arm in range(self.n_arms):
      if self.counts[arm] == 0:
        return Utils.Algorithm(arm)

    ucb_values = [0.0 for arm in range(self.n_arms)]
    total_counts = sum(self.counts)
    for arm in range(self.n_arms):
      bonus = math.sqrt((2 * math.log(total_counts)) / float(self.counts[arm]))
      ucb_values[arm] = self.values[arm] + bonus
    return Utils.Algorithm(ucb_values.index(max(ucb_values)))

  def update(self, metrics, chosen_arm):
    # Calcul de la récompense
    reward = 0
    for i in range(len(self.weight)):
      try:
        reward += self.weight[i]/metrics.get_values()[i]
      except ZeroDivisionError:
        reward +=0 

    self.counts[chosen_arm.value] += 1
    n = self.counts[chosen_arm.value]
    value = self.values[chosen_arm.value]
    new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
    self.values[chosen_arm.value] = new_value
