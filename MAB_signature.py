class MAB:
    def __init__(n_arms:int,weight:(float)):
        """n_arms: le nombre de bras
        weight.len() ==  N_metrics
        """
        self.arms = [0]*n_arms

    def select_arm()->int:
        """give the choosen arm given the actual status 
        @return integer between 1 and n_arms(included) corresponding to the chooseen arm
        """
        ...
    
    def update(metrics:tupple,chosen_arm:int)->None:
        """update the status of the bandit
        """
        ...
