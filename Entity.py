import Utils
import abc
from MAB_signature import MAB
import Metrics
import Event
import random

class Entity:
    def __init__(self, 
                id: int, 
                position: float, 
                range: float, 
                priority: int, 
                buffer_capacity: int, 
                treatment_speed: float, 
                timeline:Utils.Timeline,
                users,
                infrastructures,
                V2V_BASE_SUCCES_PROBABILITY,
                V2I_BASE_SUCCES_PROBABILITY,
                MESSAGE_SPEED,
                WAITING_TIME):
        self.id: int = id
        self.position: float = position                     # Position de l'entité sur le réseau (Position 1D)
        self.range: float = range                           # Porté de reception d'un message de l'entité
        self.priority: int = priority                       # Priorité de l'entité sur le réseau
        self.buffer_capacity: int = buffer_capacity 
        self.buffer: list[Message] = []                     # Buffer de l'entité
        self.treatment_speed: float = treatment_speed       # Vitesse de traitement des messages
        self.timeline = timeline
        self.WATTING_TIME = WAITING_TIME
        self.V2V_BASE_SUCCES_PROBABILITY = V2V_BASE_SUCCES_PROBABILITY
        self.V2I_BASE_SUCCES_PROBABILITY = V2I_BASE_SUCCES_PROBABILITY
        self.MESSAGE_SPEED = MESSAGE_SPEED
        self.users = users
        self.infrastructures = infrastructures
        self.noise = random.uniform(-0.50,0.50)
                
        
        
        self.busy: bool = False # Variable pour savoir si l'entité est en traitement de message ou pas.
        
        # Ensemble de variable servant à stocker les métriques de l'entité
        self.metrics: Metrics.EntityMetrics = Metrics.EntityMetrics(entity_id=self.id)
    
    def receive_message(self, timestamp: float, message, logs: bool = False):
        # Check si l'on peut stocker le message
        if(self.buffer_capacity > message.size):            
            self.buffer.append(message)
            self.buffer_capacity -= message.size
            
            # Si n'est pas en traitement on lance directement un event traitement.
            if not self.busy:
                self.busy = True
                self.timeline.append(Event.Treatment(timestamp + self.WATTING_TIME, self,V2I_BASE_SUCCES_PROBABILITY=self.V2I_BASE_SUCCES_PROBABILITY))
                        
            return True
        
        else:
            if logs:
                print("Message from ", message.origin.id, " to ", self.id, " is dropped : Buffer full")
                
            # Ajouter à la liste des messages dropés du sender car le buffer est plein
            message.origin.metrics.add_message_state(Metrics.MessageState.failed_during_reception,timestamp)
            
        return False
    
    
    @abc.abstractmethod        
    def send_message(self, message):
        """T'es sur que cette méthode abstraite sert a qqchose?
        """
        # Creer un event dans la timeline pour envoyer le message, la position du packet sera indiqué
        pass
    
class User(Entity):
    def __init__(self, id: int,
                position: float,
                range: float,
                priority: int,
                buffer_capacity: int,
                treatment_speed: float,
                mouvement_speed: float,
                algorithm: Utils.Algorithm,
                mab:MAB,
                timeline: Utils.Timeline,
                users,
                infrastructures,
                V2V_BASE_SUCCES_PROBABILITY,
                V2I_BASE_SUCCES_PROBABILITY,
                MESSAGE_SPEED,                
                WAITING_TIME):
        super().__init__(id, position, range, priority, buffer_capacity, treatment_speed,timeline,users,infrastructures,V2V_BASE_SUCCES_PROBABILITY,V2I_BASE_SUCCES_PROBABILITY,MESSAGE_SPEED,WAITING_TIME)
        self.mouvement_speed: float = mouvement_speed       # Vitesse de mouvement de l'entité  
        self.mab = mab
        self.algorithm: Utils.Algorithm = algorithm               # Algorithme de communication de l'entité
        
    
    # Fonction qui permet de modifier la position d'un utilisateur  
    # param : movement => float : à quel distance on bouge l'utilisateur de sa position actuelle.
    def move(self):
        if self.position + self.mouvement_speed >= 0:
            self.position = self.position + self.mouvement_speed
        else:
            self.position = 0

    
class Infrastructure(Entity):
    def __init__(self, id: int,
                position: float, 
                range: float, 
                priority: int, 
                buffer_capacity: int, 
                treatment_speed: float,
                timeline: Utils.Timeline,
                users,
                infrastructures,
                V2V_BASE_SUCCES_PROBABILITY,
                V2I_BASE_SUCCES_PROBABILITY,
                MESSAGE_SPEED,
                WAITING_TIME):
        super().__init__(id, position, range, priority, buffer_capacity, treatment_speed,timeline,users, infrastructures,V2V_BASE_SUCCES_PROBABILITY,V2I_BASE_SUCCES_PROBABILITY,MESSAGE_SPEED, WAITING_TIME)
