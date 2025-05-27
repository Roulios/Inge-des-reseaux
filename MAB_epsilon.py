import numpy as np
from MAB_signature import MAB

class EpsilonGreedy(MAB):
  def __init__(self,n_arms,weight,epsilon,**kwargs):
    super().__init__(n_arms,weight)
    self.epsilon = epsilon

  def change_epsilon(epsilon) :
    self.epsilon = epsilon
   

  @MAB.complete_arm_history
  @MAB.algorithm_choice
  def select_arm(self):
    if np.random.random() < self.epsilon:
      return np.random.randint(self.n_arms)
    else:
      return np.argmax(self.values)

  def update(self, metrics, chosen_arm):
    # Calcul de la récompense
    reward = self.calculate_reward(metrics=metrics)
        
    # Mise à jour des valeurs des bras
    self.counts[chosen_arm.value] += 1
    # n = self.counts[chosen_arm]
    # value = self.values[chosen_arm]
    # new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
    # self.values[chosen_arm] = new_value
