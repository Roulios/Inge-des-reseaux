class MAB:
    def __init__(n_arms:int):
        self.arms = [0]*n_arms

    def select_arm()->int:
        """give the choosen arm given the actual status 
        @return integer between 1 and n_arms(included) corresponding to the chooseen arm
        """
        ...
    
    def update(reward:float,chosen_arm:int)->None:
        """update the status of the bandit
        """
        ...
