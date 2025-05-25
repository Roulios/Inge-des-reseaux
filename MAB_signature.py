import abc
import Utils
from Metrics import EntityMetrics as Metrics
class MAB:
    def __init__(self,n_arms:int,weight:(float)):
        """n_arms: le nombre de bras
        weight.len() ==  N_metrics
        """
        self.n_arms = n_arms
        self.weight = weight
        self.counts = [0] * n_arms
        self.values = [0.] * n_arms
        self.history = []


    @abc.abstractmethod
    def select_arm(self)->Utils.Algorithm:
        """give the choosen arm given the actual status 
        @return algorithm from Utils.Algorithm corresponding to the chooseen arm
        """
        ...
    
    @abc.abstractmethod
    def update(self,metrics:Metrics,chosen_arm:int)->None:
        """update the status of the bandit
        """
        ...

    @staticmethod
    def complete_arm_history(f):
        """Usefull for adding decision to history"""
        def wrap(self,*args,**kwargs):
            arm = f(self,*args,**kwargs)
            self.history.append(arm)
            return arm
        return wrap

    def get_arm_history(self):
        """obtenir l'historique des choix"""
        return self.history