from Entity import *


class Message:
    def __init__(self, id: int,  origin: Entity, sender: Entity, receiver: int, size: float, priority: int, sent_from_origin_at: float):
        self.id = id                # Identifiant du message, surtout pour du debug
        self.sender = sender        # Entité qui envoie le message, pas forcément l'éméteur original du message
        self.receiver = receiver    # Entité qui doit recevoir le message
        self.size = size            # Taille du message
        self.priority = priority    # Priorité du message
        
        self.origin = origin   # Entité qui a émis le message
        self.sent_from_origin_at =  sent_from_origin_at # Timestamp d'envoie du message

