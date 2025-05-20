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
            "received_percentage": 0
        }
        self.latency_list: list[float] = []
        self.message_state_list: list[MessageState] = []
        
        self.entity_id = entity_id

    # Ajoute dans la liste de latence la latence d'un message reçu
    def add_latency(self, message_latency: float):
        self.latency_list.append(message_latency)
    
    # Ajoute dans la liste l'état d'un message (entre Réussite et Echec)
    def add_message_state(self, state: MessageState):        
        self.message_state_list.append(state)
        
    # Calcul la moyenne de la latence des paquets
    def calculate_latency(self):
        if len(self.latency_list) == 0:
            return 0
        return sum(self.latency_list) / len(self.latency_list)
    
    # Calcul le pourcentage de paquet qui on été correctement reçu
    def calculate_received_percentage(self):
        if len(self.message_state_list) == 0:
            return 0
        # Récupère la taille de la liste contenant uniquement les messages dont le statut est received                        
        return len([state for state in self.message_state_list if state == MessageState.received])
    
    def actualise_metrics(self, logs: bool = False):
        self.metrics["latency"] = self.calculate_latency()
        self.metrics["received"] = self.calculate_received_percentage()
        
        self.metrics["received_percentage"] = (self.metrics["received"] / len(self.message_state_list)) * 100 if len(self.message_state_list) > 0 else 0
        
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