import numpy as np 
from scipy.stats import beta 


class Thompson: 
    def __init__(MAB, true_probability):
        self.true_probability = true_probability
        self.alpha = [1]* n_arms 
        self.beta = [1]* n_arms 
        
    def update(self, metrics,chosen_arm):
        # Calcul de la récompense
        reward = 0
        for i in range(len(self.weight)):
        try:
            reward += self.weight[i]/metrics.get_values()[i]
        except ZeroDivisionError:
            reward +=0
        # Avec Thompson, la récompense est un échec (0) ou une réussite
        reward =  reward < true_probability[chosen_arm] #faudrait que reward soit entre 0 et 1 pour le comparer à une proba
        self.alpha[chosen_arm] += reward 
        self.beta[chosen_arm] += (1 - reward) 

    def select_arm(self):
        # Échantillonnage
        for arm in range(self.n_arms):
            self.values[arm] = np.random.beta(self.alpha[chosen_arm], self.beta[chosen_arm])
        # Choix du meilleur bras
        return np.argmax(self.values)