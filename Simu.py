import abc
import Utils
from enum import Enum

# Constante pour décrire la vitesse de la transmission physique d'un message, pas vrai dans la réalité.
MESSAGE_SPEED = 0.005
WATTING_TIME = 0.00001 # Constante pour décaler un peu dans la timeline pour éviter les collisions.

# Constante pour décrire le nombre d'évènements de mouvement dans la timeline par utilisateur = Distance parcouru
NUMBER_OF_MOVEMENTS = 10


# Timeline de la simulation, sera utilisée pour stocker les évènements
timeline: Utils.Timeline = Utils.Timeline()

#enum qui représente l'un des 2 protocoles de communication, le V2V et le V2I
class Algorithm(Enum):
    V2V = 0
    V2I = 1


class Entity:
    def __init__(self, id: int, position: float, protocol, range: float, priority: int, buffer_capacity: int, treatment_speed: float, algorithm: Algorithm):
        self.id: int = id
        self.position: float = position                     # Position de l'entité sur le réseau (Position 1D)
        self.protocol: int = protocol 
        self.range: float = range                           # Porté de reception d'un message de l'entité
        self.priority: int = priority                       # Priorité de l'entité sur le réseau
        self.buffer_capacity: int = buffer_capacity 
        self.buffer: list[Message] = []                     # Buffer de l'entité
        self.treatment_speed: float = treatment_speed       # Vitesse de traitement des messages
        
        self.algorithm: Algorithm = algorithm               # Algorithme de communication de l'entité
        
        self.busy: bool = False # Variable pour savoir si l'entité est en traitement de message ou pas.
    
    @abc.abstractmethod          
    def receive_message(self, timestamp: float, message, logs: bool = False):
        # Check si l'on peut stocker le message
        if(self.buffer_capacity > message.size):            
            self.buffer.append(message)
            self.buffer_capacity -= message.size
            
            # Si n'est pas en traitement on lance directement un event traitement.
            if not self.busy:
                self.busy = True
                timeline.append(Treatment(timestamp + WATTING_TIME, self))
                        
            return True
        
        else:
            if logs:
                print("Message from ", message.origin.id, " to ", self.id, " is dropped : Buffer full")
        return False
    
    @abc.abstractmethod        
    def send_message(self, message):
        # Creer un event dans la timeline pour envoyer le message, la position du packet sera indiqué
        pass
    
class User(Entity):
    def __init__(self, id: int, position: float, protocol, range: float, priority: int, buffer_capacity: int, treatment_speed: float, mouvement_speed: float, algorithm: Algorithm):
        super().__init__(id, position, protocol, range, priority, buffer_capacity, treatment_speed, algorithm)
        self.mouvement_speed: float = mouvement_speed       # Vitesse de mouvement de l'entité  

    
    # Fonction qui permet de modifier la position d'un utilisateur  
    # param : movement => float : à quel distance on bouge l'utilisateur de sa position actuelle.
    def move(self):
        if self.position + self.mouvement_speed >= 0:
            self.position = self.position + self.mouvement_speed
        else:
            self.position = 0

    
class Infrastructure(Entity):
    def __init__(self, id: int, position: float, protocol, range: float, priority: int, buffer_capacity: int, treatment_speed: float, algorithm: Algorithm):
        super().__init__(id, position, protocol, range, priority, buffer_capacity, treatment_speed, algorithm)

class Message:
    def __init__(self, id: int,  origin: Entity, sender: Entity, receiver: int, size: float, priority: int):
        self.id = id                # Identifiant du message, surtout pour du debug
        self.sender = sender        # Entité qui envoie le message, pas forcément l'éméteur original du message
        self.receiver = receiver    # Entité qui doit recevoir le message
        self.size = size            # Taille du message
        self.priority = priority    # Priorité du message
        
        # Si le sender est l'entité qui a initialement émis le message, on 
        self.origin = origin   # Entité qui a émis le message


# Liste de l'ensemble des utilisateurs sur notre réseau
users : list[User] = []

# Liste de l'ensemble des infrastructures sur notre réseau
infrastructures : list[Infrastructure] = []

entities : list[Entity] = []
       

# Event emission d'un message.
class Emission(Utils.Event):
    
    def __init__(self, timestamp: float, message: Message):
        super().__init__(timestamp)
        self.message = message
        
    def run(self, logs=False):
        selected_entities : list[User | Infrastructure] = []
        
        if self.message.sender.algorithm == Algorithm.V2V:
            selected_entities = users
        elif self.message.sender.algorithm == Algorithm.V2I:
            selected_entities = infrastructures
                
        for entity in selected_entities:
            distance = abs(self.message.sender.position - entity.position)
            
            if distance < entity.range and entity.id != self.message.sender.id:
                if logs:
                    print("Message from ", self.message.sender.id, " to ", entity.id, " is in range")
                    
                # On est a porté, création d'un event reception dans la timeline.
                timeline.append(Reception(self.timestamp + distance*MESSAGE_SPEED, self.message, entity))
            
            elif(distance > entity.range): 
                if logs:
                    print("Message from ", self.message.sender.id, " to ", entity.id, " is out of range")
class Reception(Utils.Event):
    def __init__(self, timestamp: float, message: Message, receiver: Entity):
        super().__init__(timestamp)
        self.message = message
        self.receiver = receiver
        
    def run(self, logs: bool=False):
        if logs:
            print("Message from ", self.message.origin.id, " to ", self.receiver.id, " is received at time: ", self.timestamp)
        
        # Tentative de reception du message par l'entité.
        self.receiver.receive_message(timestamp=self.timestamp, message=self.message, logs=logs)
        
class Treatment(Utils.Event):
    def __init__(self, timestamp: float, entity: Entity):
        super().__init__(timestamp)
        self.entity = entity
        
    def run(self, logs: bool=False):
        # Traitement du message
        message : Message = self.entity.buffer.pop(0)
        self.entity.buffer_capacity += message.size
        
        # Si l'entité est une station, on fait en sorte qu'elle rediffuse le message à l'ensemble des voitures à portée
        if isinstance(self.entity, Infrastructure):
            if logs:
                print("Message from ", message.origin.id, " to infrastructure ", self.entity.id, "is receveid and get retransmit")
            timeline.append(Emission(self.timestamp, message=Message(id=0, sender=self.entity, origin=message.origin ,receiver=1, size=message.size, priority=0))) #TODO: Je suis vraiment mais VRAIMENT pas certain du timestamp
            
        
        if logs:
            print("Message from ", message.origin.id, " to ", self.entity.id, " is treated at time: ", self.timestamp)
        
        # On regarde si il reste des messages dans le buffer
        if len(self.entity.buffer) > 0:
            # On lance un event traitement
            timeline.append(Treatment(self.timestamp + (message.size / self.entity.treatment_speed), self.entity))
        else:
            self.entity.busy = False
            
# Event de mouvement d'un utilisateur          
class Mouvement(Utils.Event):
    def __init__(self, timestamp: float, user: User):
        super().__init__(timestamp)
        self.user = user
        
    def run(self, logs: bool=False):
        if logs:
            print("User ", self.user.id, " is moving at time: ", self.timestamp, "and is now at position: ", self.user.position)
        
        # On bouge l'utilisateur à la vitesse qu'il possède
        self.user.move()
            
# Initialisation de la liste des utilisateurs
users = [
    User(id=0, position=0.0, protocol=0, range=20, priority=0, buffer_capacity=10, treatment_speed=0.1, mouvement_speed=1, algorithm=Algorithm.V2I),
    User(id=1, position=2.0, protocol=0, range=20, priority=0, buffer_capacity=10, treatment_speed=0.1, mouvement_speed=2, algorithm=Algorithm.V2I),
    User(id=2, position=40.0, protocol=0, range=20, priority=0, buffer_capacity=10, treatment_speed=0.1, mouvement_speed=3, algorithm=Algorithm.V2I), 
]

infrastructures = [
    Infrastructure(id=3, position=10.0, protocol=0, range=200, priority=0, buffer_capacity=100, treatment_speed=0.1, algorithm=Algorithm.V2V),
]

# Fonction qui peuple de tentative d'emission de message dans la timeline
def populate_simulation():
    timeline.append(Emission(timestamp=0.0, message=Message(id=0, sender=users[0], origin=users[0], receiver=1, size=5, priority=0)))
    #timeline.append(Emission(timestamp=0.0001, message=Message(id=1, sender=users[0], origin=users[1], receiver=1, size=1, priority=0)))
    #timeline.append(Emission(timestamp=0.6, message=Message(id=2, sender=users[2], origin=users[2], receiver=1, size=1, priority=0)))
    
    # Boucle peuplant l'ensemble des mouvements des véhicules
    for user in users:
        for i in range(0, NUMBER_OF_MOVEMENTS):
            timeline.append(Mouvement(timestamp=i, user=user))
        
    
def run_simulation(logs: bool = False):
    
    index: int = 0
    
    if logs:
        print("Lancement de la simulation")
    
    while index < timeline.length:
        
        event = timeline.pop()
        
        if logs:
            print("Event at time: ", event.timestamp, "is running")
            print("Remaining events: ", timeline.length)
            
        #TODO: Check for bugs
        event.run(logs=True)
        
# Simulation

populate_simulation()
run_simulation()