from MAB_signature import MAB
import Utils
from Metrics import EntityMetrics as Metrics
class ChoiceV2V(MAB):
    """Choisis le V2V a chaque fois"""
    def __init__(self,n_arms:int,weight:(float),**kwargs):
        """n_arms: le nombre de bras
        weight.len() ==  N_metrics
        """
        super().__init__(n_arms,weight)


    @MAB.complete_arm_history
    @MAB.algorithm_choice
    def select_arm(self)->Utils.Algorithm:
        """give the choosen arm given the actual status 
        @return 0 every time
        """
        return 0
    
    def update(self,metrics:Metrics,chosen_arm:int)->None:
        """update the status of the bandit
        """
        ...
