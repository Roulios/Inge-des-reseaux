import pandas as pd
import numpy as np

class EpsilonGreedy:
  def __init__(MAB):
    MAB.__init__(self)
    self.epsilon = EPSILON # Constantce


  def select_arm(self):
    if np.random.random() < self.epsilon:
      return np.random.randint(self.num_arms)
    else:
      return np.argmax(self.values)

  def update(self, chosen_arm,metrics):
    # Calcul de la récompense
    reward = 0
    for i in range len(weight):
      reward += self.weight[i]*1/metrics[i]
    
    # Mise à jour des valeurs des bras
    self.counts[chosen_arm] += 1
    n = self.counts[chosen_arm]
    value = self.values[chosen_arm]
    new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
    self.values[chosen_arm] = new_value
