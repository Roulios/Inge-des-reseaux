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
    
    @staticmethod
    def algorithm_choice(f):
        """Util for returning the good value type"""
        def wrap(self,*args,**kwargs)->Utils.Algorithm:
            return Utils.Algorithm(f(self,*args,**kwargs))
        return wrap

    def get_arm_history(self):
        """obtenir l'historique des choix"""
        return self.history
    
    
    def calculate_reward(self, metrics:Metrics)-> float:
        """calculating rewards"""
        reward = 0
        values = metrics.get_values()
        try:
            reward += self.weight[0]/values[0]#la latence doit etre le plus petite possible, elle est entre 0 et x dans  R+
        except ZeroDivisionError:
            ...
        reward += self.weight[1]*values[1]**2# le pourcentage reçu doit être grand
        try:
            reward += self.weight[2]/values[2] # la jigue doit etre le plus petite possible
        except ZeroDivisionError:
            ...
        return reward