import numpy as np 
from scipy.stats import beta
from MAB_signature import MAB


class Thompson(MAB): 
    def __init__(self,n_arms,weight,true_probability,**kwargs):
        super().__init__(n_arms,weight)
        self.true_probability = true_probability
        self.alpha = [1]* n_arms 
        self.beta = [1]* n_arms 
        
    def update(self, metrics,chosen_arm):
        # Calcul de la récompense
        reward = self.calculate_reward(metrics=metrics)
        # Avec Thompson, la récompense est un échec (0) ou une réussite (1)
        reward =  reward < self.true_probability[chosen_arm.value] #Le rewrad oscille autour de 0.5 pour respecter proba autour de 0.5
        # Mise à jour des paramètres
        self.alpha[chosen_arm.value] += reward 
        self.beta[chosen_arm.value] += (1 - reward) 
    
    
    @MAB.complete_arm_history
    @MAB.algorithm_choice
    def select_arm(self):
        # Échantillonnage
        for arm in range(self.n_arms):
            self.values[arm] = np.random.beta(self.alpha[arm], self.beta[arm])
        # Choix du meilleur bras
        return np.argmax(self.values)