import abc
import Utils

# Variable pour décrire la vitesse de la transmission physique d'un message, pas vrai dans la réalité.
MESSAGE_SPEED = 0.005
WATTING_TIME = 0.00001 # Constante pour décaler un peu dans la timeline pour éviter les collisions.

# Timeline de la simulation, sera utilisée pour stocker les évènements
timeline: Utils.Timeline = Utils.Timeline()

class Entity:
    def __init__(self, id: int, position: float, protocol, range: float, priority: int, buffer_capacity: int, treatment_speed: float):
        self.id: int = id
        self.position: float = position                     # Position de l'entité sur le réseau (Position 1D)
        self.protocol: int = protocol 
        self.range: float = range                           # Porté de reception d'un message de l'entité
        self.priority: int = priority                       # Priorité de l'entité sur le réseau
        self.buffer_capacity: int = buffer_capacity 
        self.buffer: list[Message] = []                     # Buffer de l'entité
        self.treatment_speed: float = treatment_speed       # Vitesse de traitement des messages
        
        self.busy: bool = False # Variable pour savoir si l'entité est en traitement de message ou pas.
    
    @abc.abstractmethod          
    def receive_message(self, timestamp: float, message):
        # Check si l'on peut stocker le message
        if(self.buffer_capacity > message.size):
            self.buffer.append(message)
            self.buffer_capacity -= message.size
            
            # Si n'est pas en traitement on lance directement un event traitement.
            if not self.busy:
                self.busy = True
                Treatment(timestamp + WATTING_TIME, self)
                        
            return True
        return False
    
    @abc.abstractmethod        
    def send_message(self, message):
        # Creer un event dans la timeline pour envoyer le message, la position du packet sera indiqué
        pass
    
class User(Entity):
    def __init__(self, id: int, position: float, protocol, range: float, priority: int, buffer_capacity: int, treatment_speed: float):
        super.__init__(id, position, protocol, range, priority, buffer_capacity, treatment_speed)

class Infrastructure(Entity):
    def __init__(self, id: int, position: float, protocol, range: float, priority: int, buffer_capacity: int, treatment_speed: float):
        super.__init__(id, position, protocol, range, priority, buffer_capacity, treatment_speed)

class Message:
    def __init__(self, id: int, sender: Entity, receiver: int, size: float, priority: int):
        self.id = id
        self.sender = sender
        self.receiver = receiver
        self.size = size
        self.priority = priority

# Liste de l'ensemble des utilisateurs sur notre réseau
users : list[User] = []

# Liste de l'ensemble des infrastructures sur notre réseau
infrastructures : list[Infrastructure] = []

entities : list[Entity] = []
       

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
        for entity in entities:
            
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
        message : Message = self.entity.buffer.pop(0)
        self.entity.buffer_capacity += message.size
        
        # On regarde si il reste des messages dans le buffer
        if len(self.entity.buffer) > 0:
            # On lance un event traitement
            Treatment(self.timestamp + (message.size / self.entity.treatment_speed), self.entity)
        else:
            self.entity.busy = False
            
# Initialisation de la liste des utilisateurs

# def __init__(self, id: int, position: float, protocol, range: float, priority: int, buffer_capacity: int, treatment_speed: float):


entities = [
    User(id=0, position=0.0, protocol=0, range=20, priority=0, buffer_capacity=10, treatment_speed=0.1),
    User(id=1, position=2.0, protocol=0, range=20, priority=0, buffer_capacity=10, treatment_speed=0.1),
    User(id=2, position=4.0, protocol=0, range=20, priority=0, buffer_capacity=10, treatment_speed=0.1),
]

# Fonction qui peuple de tentative d'emission de message dans la timeline
def populate_simulation():
    timeline.append(Emission(timestamp=0.0, message=Message(id=0, sender=entities[0], receiver=1, size=10, priority=0)))
    timeline.append(Emission(timestamp=0.3, message=Message(id=1, sender=entities[0], receiver=1, size=10, priority=0)))
    timeline.append(Emission(timestamp=0.6, message=Message(id=2, sender=entities[2], receiver=1, size=10, priority=0)))
    
def run_simulation(show_logs: bool = False):
    if show_logs:
        print("Lancement de la simulation")
    
    for event in timeline:
        print("Event at time: ", event.timestamp, "is running")
        
        #TODO: Check for bugs
        event.run()
        
# Simulation

populate_simulation()
run_simulation()