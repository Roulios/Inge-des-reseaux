import abc

class MAB:
    def __init__(self,n_arms:int,weight:(float)):
        """n_arms: le nombre de bras
        weight.len() ==  N_metrics
        """
        self.n_arms = n_arms
        self.counts = [0] * n_arms
        self.values = [0.] * n_arms


    @abc.abstractmethod
    def select_arm(self)->int:
        """give the choosen arm given the actual status 
        @return integer between 1 and n_arms(included) corresponding to the chooseen arm
        """
        ...
    
    @abc.abstractmethod
    def update(self,metrics:tupple,chosen_arm:int)->None:
        """update the status of the bandit
        """
        ...
