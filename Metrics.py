""" Module de gestion des métriques d'une entité. Implémentation de la classe EntityMetrics. 
    Permet de stocker les relevé de données des échanges entre les entités et d'en déduire des métriques.
"""

from enum import Enum

class MessageState(Enum):
    received = 0
    failed = 1


class EntityMetrics():
    def __init__(self):
        self.metrics = {
            "sent": 0,
            "received": 0,
            "latency": 0,
            "received_percentage": 0
        }
        self.latency_list: list[float] = []
        self.message_state_list: list = []

    # Ajoute dans la liste de latence la latence d'un message reçu
    def add_latency(self, message_latency: float):
        self.latency_list.append(message_latency)
    
    # Ajoute dans la liste l'état d'un message (entre Réussite et Echec)
    def add__message_state(self, state: MessageState):
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
    
    def actualise_metrics(self):
        self.metrics["latency"] = self.calculate_latency()
        self.metrics["received"] = self.calculate_received_percentage()