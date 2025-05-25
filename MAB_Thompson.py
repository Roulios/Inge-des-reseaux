import numpy as np 
from scipy.stats import beta 
from MAB_signature import MAB


class Thompson(MAB): 
    def __init__(self,n_arms,weight, true_probability): 
        super().__init__(n_arms,weight)
        self.alpha = [1]* n_arms 
        self.beta = [1]* n_arms 


    def update(self, metrics,chosen_arm)->int: 
        self.alpha[chosen_arm] += reward 
        self.beta[chosen_arm] += (1 - reward) 

    @MAB.complete_arm_history 
    @MAB.algorithm_choice
    def select_arm(self):
        # Échantillonnage
        for arm in range(self.n_arms):
            self.values[arm] = np.random.beta(self.alpha[chosen_arm], self.beta[chosen_arm])
        # Choix du meilleur bras
        return np.argmax(self.values)