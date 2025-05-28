import numpy as np
from MAB_signature import MAB

class EpsilonGreedy(MAB):
  def __init__(self,n_arms,weight,epsilon,**kwargs):
    super().__init__(n_arms,weight)
    self.epsilon = epsilon



  @MAB.complete_arm_history
  @MAB.algorithm_choice
  def select_arm(self):

    if np.random.random() < self.epsilon:
      # Choix aléatoire du bras
      return np.random.randint(self.n_arms)
    else:
      # Choix du meilleur bras
      return np.argmax(self.values)

  def update(self, metrics, chosen_arm):
    # Calcul de la récompense
    reward = self.calculate_reward(metrics)
    # Maj de la valeur estimée du bra
    arm = chosen_arm.value
    self.counts[arm] += 1
    n = self.counts[arm]
    value = self.values[arm]
    # Mise à jour incrémentale de la moyenne
    self.values[arm] = ((n - 1) / n) * value + (1 / n) * reward
