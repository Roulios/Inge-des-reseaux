import numpy as np 
from scipy.stats import beta 


class Thompson: 
    def __init__(MAB, true_probability): 
        self.alpha = [1]* n_arms 
        self.beta = [1]* n_arms 
        
    def update(self, metrics,chosen_arm): 
        self.alpha[chosen_arm] += reward 
        self.beta[chosen_arm] += (1 - reward) 

    def select_arm(self):
        # Échantillonnage
        for arm in range(self.n_arms):
            self.values[arm] = np.random.beta(self.alpha[chosen_arm], self.beta[chosen_arm])
        # Choix du meilleur bras
        return np.argmax(self.values)