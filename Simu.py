import abc

# Variable pour décrire la vitesse de la transmission physique d'un message, pas vrai dans la réalité.
MESSAGE_SPEED = 0.005

class Entity:
    def __init__(self, id: int, position: float, protocol, range: float, priority: int, buffer_capacity: int):
        self.id: int = id
        self.position: float = position
        self.protocol: int = protocol
        self.range: float = range
        self.priority: int = priority
        self.buffer_capacity: int = buffer_capacity
        self.buffer: list[Message] = []
        
        self.busy: bool = False # Variable pour savoir si l'entité est en traitement de message ou pas.
    
    @abc.abstractmethod          
    def receive_message(self, message: Message):
        # Check si l'on peut stocker le message
        if(self.buffer_capacity > message.size):
            self.buffer.append(message)
            self.buffer_capacity -= message.size
            
            # Si n'est pas en traitement on lance directement un event traitement.
            if not self.busy:
                self.busy = True
                # Lancer un event d'emission
            
                        
            return True
        return False
    
    @abc.abstractmethod        
    def send_message(self, message: Message):
        # Creer un event dans la timeline pour envoyer le message, la position du packet sera indiqué
        pass
    
class User(Entity):
    def __init__(self, id: int, position: float, protocol, range: float, priority: int, buffer_capacity: int):
        super.__init__(id, position, protocol, range, priority, buffer_capacity)

class Infrastructure(Entity):
    def __init__(self, id: int, position: float, protocol, range: float, priority: int, buffer_capacity: int):
        super.__init__(id, position, protocol, range, priority, buffer_capacity)

class Message:
    def __init__(self, id: int, sender: Entity, receiver: int, size: int, priority: int):
        self.id = id
        self.sender = sender
        self.size = size
        self.priority = priority

# Liste de l'ensemble des utilisateurs sur notre réseau
Users : list[User] = []

# Liste de l'ensemble des infrastructures sur notre réseau
Infrastructures : list[Infrastructure] = []

Entities : list[Entity] = []
       

# Classe abstraite pour représenter un événement, implémente la méthode run qui sera implémentée par les classes filles
class Event():

    def __init__(self, timestamp: float ):
        self.timestamp = timestamp

    @abc.abstractmethod
    def run(self):
        pass
    
    
# Event emission d'un message.
class Emission(Event):
    
    def __init__(self, timestamp: float, message: Message):
        super().__init__(timestamp)
        self.message = message
        
    def run(self):    
        for entity in Entities:
            
            distance = abs(self.message.sender.position - entity.position)
            
            if distance < entity.range:
                # On est a porté, création d'un event reception dans la timeline.
                Reception(self.timestamp + distance*MESSAGE_SPEED, self.message, entity)
                
class Reception(Event):
    def __init__(self, timestamp: float, message: Message, receiver: Entity):
        super().__init__(timestamp)
        self.message = message
        
    def run(self):
        # Tentative de reception du message par l'entité.
        self.message.receiver.receive_message(self.message)
        
class Treatment(Event):
    def __init__(self, timestamp: float, entity: Entity):
        super().__init__(timestamp)
        self.entity = entity
        
    def run(self):
        # Traitement du message
        message = self.entity.buffer.pop(0)
        self.entity.buffer_capacity += message.size
        
        # On regarde si il reste des messages dans le buffer
        if len(self.entity.buffer) > 0:
            # On lance un event traitement
            Treatment(self.timestamp + 1, self.entity)
        else:
            self.entity.busy = False