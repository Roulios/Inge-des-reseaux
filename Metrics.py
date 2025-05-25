""" Module de gestion des métriques d'une entité. Implémentation de la classe EntityMetrics. 
    Permet de stocker les relevé de données des échanges entre les entités et d'en déduire des métriques.
"""

from enum import Enum

class MessageState(Enum):
    received = 0
    failed_during_emission = 1      # Echec durant l'émission du message
    failed_during_reception = 2     # Echec durant la réception du message


class EntityMetrics():
    def __init__(self, entity_id: int):
        self.metrics = {
            "sent": 0,
            "received": 0,# comme des ack mais en
            "latency": 0,
            "received_percentage": 0,
            "jitter": 0
        }
        self.latency_list: list[float] = []
        self.message_state_list: list[MessageState] = []
        
        self.entity_id = entity_id

    def add_metric_status(f):
        def exec(self,*args,**kwargs):
            result = f(self,*args,**kwargs)
            self.actualise_metrics()
            return result
        return exec

    
            


    def get_values(self):
        return [
            self.metrics["sent"],
            self.metrics["received"],
            self.metrics["latency"],
            self.metrics["received_percentage"],
            self.metrics["jitter"]
        ]

    @add_metric_status
    def add_latency(self, message_latency: float):
        """Ajoute dans la liste de latence la latence d'un message reçu"""
        self.latency_list.append(message_latency)
        
    
    @add_metric_status
    def add_message_state(self, state: MessageState):     
        """# Ajoute dans la liste l'état d'un message (entre Réussite et Echec)"""   
        self.message_state_list.append(state)
        
    def calculate_latency(self):
        """
        Calcul la moyenne glissante de la latence des paquets
        """
        if len(self.latency_list) == 0:
            return 100000000000 # ça evite des problemes de div par 0, une latence infinie
        return sum(self.latency_list[-10:]) / len(self.latency_list[-10:])
    
    def calculate_received_percentage(self):
        """
        Calcul le pourcentage de paquet qui on été correctement reçu
        """
        if len(self.message_state_list) == 0:
            return 0
        # Récupère la taille de la liste contenant uniquement les messages dont le statut est received                        
        return sum(1 for state in self.message_state_list if state == MessageState.received)/len(self.message_state_list)*100
    
    def calculate_jitter(self):
        """on calcule la gigue comme le max d'ecart successifs durant les 5 dernieres communication"""
        if len(self.latency_list)<2:
            return 0
        recent_latencies = self.latency_list[-10:]
        return max([abs(l1-l2) for l1,l2 in zip(recent_latencies[:-1],recent_latencies[1:])])

    def actualise_metrics(self, logs: bool = False):
        self.metrics["latency"] = self.calculate_latency()
        self.metrics["sent"] = sum(1 for message in self.message_state_list )
        self.metrics["received"] = sum(1 for message in self.message_state_list if message == MessageState.received)

        
        self.metrics["received_percentage"] = self.calculate_received_percentage()
        self.metrics["jitter"] = self.calculate_jitter()
        
        if logs:
            print("Latence :", self.metrics['latency'])
            print("Pourcentage de paquets reçus :", self.metrics['received_percentage'],"%")
            
    def show_metrics(self, verbose: bool = False):
        print("Entity ID :", self.entity_id)
        print("Métriques :")
        for key, value in self.metrics.items():
            print(f"{key} : {value}")
            
        if verbose:
            print("Liste des latences :", self.latency_list)
            print("Liste des états des messages :", self.message_state_list)

