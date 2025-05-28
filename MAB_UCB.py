import numpy as np
import math
from MAB_signature import MAB
import Utils

class UCB(MAB):
  def __init__(self,n_arms,weight,**kwargs):
    super().__init__(n_arms,weight)

  @MAB.complete_arm_history
  @MAB.algorithm_choice
  def select_arm(self):
    for arm in range(self.n_arms):
      if self.counts[arm] == 0:
        return arm

    ucb_values = [0.0 for arm in range(self.n_arms)]
    # Calcul n_t
    total_counts = sum(self.counts)
    for arm in range(self.n_arms):
      # Calcul de l'incertitude
      bonus = math.sqrt((2 * math.log(total_counts)) / float(self.counts[arm]))
      # Calcul de la nouvelle récompense 
      ucb_values[arm] = self.values[arm] + bonus
    # Choix du meilleur bras
    return ucb_values.index(max(ucb_values))

  def update(self, metrics, chosen_arm):
    # Calcul de la récompense
    reward = self.calculate_reward(metrics=metrics)
    # Maj N_t (a)
    self.counts[chosen_arm.value] += 1
    # Maj de la valeur estimée du bras
    n = self.counts[chosen_arm.value]
    value = self.values[chosen_arm.value]
    new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
    self.values[chosen_arm.value] = new_value
