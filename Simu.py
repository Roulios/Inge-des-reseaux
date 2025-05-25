import abc
import Utils
import Metrics
import random
import math
from enum import Enum
from MAB_signature import MAB
import MAB_UCB

# Constante pour décrire la vitesse de la transmission physique d'un message, pas vrai dans la réalité.
MESSAGE_SPEED = 0.005
WATTING_TIME = 0.00001 # Constante pour décaler un peu dans la timeline pour éviter les collisions.

# Constante pour décrire le nombre d'évènements de mouvement dans la timeline par utilisateur = Distance parcouru
NUMBER_OF_MOVEMENTS = 0

# Temps de la simulation en secondes
SIMULATION_TIME = 10.0

# Probabilité de succès d'une emission entre 2 véhicules (ratio entre la distance et la porté pour laquelle on part du principe que il n'y aura pas d'échec)
V2V_BASE_SUCCES_PROBABILITY = 0.5

# Probabilité de succès d'une emission entre un véhicule et une infrastructure
V2I_BASE_SUCCES_PROBABILITY = 0.8

# Nombre de voiture dans la simulation
NUMBER_OF_USERS = 100

# Nombre d'infrastructure dans la simulation
NUMBER_OF_INFRASTRUCTURES = 10

#Types de MAB a utiliser 
MAB_LIST = [MAB_UCB.UCB]

# Timeline de la simulation, sera utilisée pour stocker les évènements
timeline: Utils.Timeline = Utils.Timeline()

class Entity:
    def __init__(self, id: int, position: float, protocol, range: float, priority: int, buffer_capacity: int, treatment_speed: float, algorithm: Utils.Algorithm):
        self.id: int = id
        self.position: float = position                     # Position de l'entité sur le réseau (Position 1D)
        self.protocol: int = protocol 
        self.range: float = range                           # Porté de reception d'un message de l'entité
        self.priority: int = priority                       # Priorité de l'entité sur le réseau
        self.buffer_capacity: int = buffer_capacity 
        self.buffer: list[Message] = []                     # Buffer de l'entité
        self.treatment_speed: float = treatment_speed       # Vitesse de traitement des messages
        
        self.algorithm: Utils.Algorithm = algorithm               # Algorithme de communication de l'entité
        
        self.busy: bool = False # Variable pour savoir si l'entité est en traitement de message ou pas.
        
        # Ensemble de variable servant à stocker les métriques de l'entité
        self.metrics: Metrics.EntityMetrics = Metrics.EntityMetrics(entity_id=self.id)
    
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
                
            # Ajouter à la liste des messages dropés du sender car le buffer est plein
            message.origin.metrics.add_message_state(Metrics.MessageState.failed_during_reception)
            
        return False
    
    @abc.abstractmethod        
    def send_message(self, message):
        # Creer un event dans la timeline pour envoyer le message, la position du packet sera indiqué
        pass
    
class User(Entity):
    def __init__(self, id: int, position: float, protocol, range: float, priority: int, buffer_capacity: int, treatment_speed: float, mouvement_speed: float, algorithm: Utils.Algorithm, mab:MAB):
        super().__init__(id, position, protocol, range, priority, buffer_capacity, treatment_speed, algorithm)
        self.mouvement_speed: float = mouvement_speed       # Vitesse de mouvement de l'entité  
        self.mab = mab
    
    # Fonction qui permet de modifier la position d'un utilisateur  
    # param : movement => float : à quel distance on bouge l'utilisateur de sa position actuelle.
    def move(self):
        if self.position + self.mouvement_speed >= 0:
            self.position = self.position + self.mouvement_speed
        else:
            self.position = 0

    
class Infrastructure(Entity):
    def __init__(self, id: int, position: float, protocol, range: float, priority: int, buffer_capacity: int, treatment_speed: float, algorithm: Utils.Algorithm):
        super().__init__(id, position, protocol, range, priority, buffer_capacity, treatment_speed, algorithm)

class Message:
    def __init__(self, id: int,  origin: Entity, sender: Entity, receiver: int, size: float, priority: int, sent_from_origin_at: float):
        self.id = id                # Identifiant du message, surtout pour du debug
        self.sender = sender        # Entité qui envoie le message, pas forcément l'éméteur original du message
        self.receiver = receiver    # Entité qui doit recevoir le message
        self.size = size            # Taille du message
        self.priority = priority    # Priorité du message
        
        self.origin = origin   # Entité qui a émis le message
        self.sent_from_origin_at =  sent_from_origin_at # Timestamp d'envoie du message



# Liste de l'ensemble des utilisateurs sur notre réseau
users : list[User] = []

# Liste de l'ensemble des infrastructures sur notre réseau
infrastructures : list[Infrastructure] = []

entities : list[Entity] = []
       
       
# Event utilisé uniquement pour rendre le peuplement d'event de la simulation plus simple
# L'objectif est de détecter quels entité sont à une distance suffisament proche pour recevoir le message
# On évite ainsi d'envoyer des events emissions pour des objets qui sont situé à plusieurs kilomètres de distance
class TryEmission(Utils.Event):
    def __init__(self, timestamp: float, entity: Entity):
        super().__init__(timestamp)
        self.entity = entity
        
    def run(self, logs: bool=False):
        receivers : list[Entity] = []
        
        # Selection de la liste des entités qui peuvent recevoir le message (on regarde la distance entre l'émetteur et les autres entités)
        if self.entity.algorithm == Utils.Algorithm.V2V:
            receivers = list(filter(lambda x: (x.id != self.entity.id) and (abs(x.position - self.entity.position) < self.entity.range) , users))
        elif self.entity.algorithm == Utils.Algorithm.V2I:
            receivers = list(filter(lambda x: (x.id != self.entity.id) and (abs(x.position - self.entity.position) < self.entity.range) , infrastructures))     
      
        
        # Ajout dans la timeline une tentative d'emission d'un message à chaque candidat
        for receiver in receivers:
            # Calcul de la probabilité de succès d'une émission. Plus la distance est grande, plus la probabilité de succès est faible. V2I est censé être plus fiable.
            if self.entity.algorithm == Utils.Algorithm.V2V:
                fail_probability : float = 1-math.exp(-abs(self.entity.position - receiver.position) / self.entity.range) * V2V_BASE_SUCCES_PROBABILITY
            elif self.entity.algorithm == Utils.Algorithm.V2I:
                fail_probability : float = 1-math.exp(-abs(self.entity.position - receiver.position) / self.entity.range) * V2I_BASE_SUCCES_PROBABILITY
                
            
            
            timeline.append(Emission(timestamp=self.timestamp, fail_probability=fail_probability, message=Message(id=0, sender=self.entity, origin=self.entity, receiver=receiver.id, size=1, priority=self.entity.priority, sent_from_origin_at=self.timestamp)))

# Event emission d'un message.
class Emission(Utils.Event):
    
    def __init__(self, timestamp: float, message: Message, fail_probability: float):
        super().__init__(timestamp)
        self.message = message
        self.fail_probability = fail_probability
        
    def run(self, logs=False):
                
        if logs:
            print("Try sending message from ", self.message.origin.id, " to ", self.message.receiver, " with probability of fail: ", self.fail_probability*100 if self.fail_probability > 0 else 0, "%")
             
        # Traitement de la probabilité de succès d'une emission
        if random.random() > self.fail_probability:
            if logs:
                print("Message from ", self.message.origin.id, " to ", self.message.receiver, " is sent at time: ", self.timestamp)
                        
            # TODO: Faire un truc propre bruh
            distance = abs(self.message.sender.position - self.message.receiver)
            receiver = list(filter(lambda x: x.id == self.message.receiver, users + infrastructures))[0]
            
            # On lance un event reception pour chaque entité qui est dans la portée de l'émetteur
            timeline.append(Reception(timestamp=self.timestamp + distance*MESSAGE_SPEED, message=self.message, receiver=receiver))

        else:
            if logs:
                print("Message from ", self.message.origin.id, " to ", self.message.receiver, " is dropped : Failed during emission")
                
            # Ajouter à la liste des messages dropés du sender car l'émission a échoué
            self.message.origin.metrics.add_message_state(Metrics.MessageState.failed_during_emission)
        """
        selected_entities : list[User | Infrastructure] = []
        
        if self.message.sender.algorithm == Utils.Algorithm.V2V:
            selected_entities = users
        elif self.message.sender.algorithm == Utils.Algorithm.V2I:
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
                    print("Message from ", self.messagsender.id, " to ", entity.id, " is out of range")
                    
                # Ajouter à la liste des messages dropés du sende.er car la distance est trop grande
                self.message.origin.metrics.add_message_state(Metrics.MessageState.failed_during_emission)
        """     
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
                print("Message from ", message.origin.id, " to infrastructure ", self.entity.id, "is receveid and get retransmit at time: ", self.timestamp)
                
            # Calcul de la probabilité de succès de la réémission
            fail_probability : float = abs(self.entity.position - message.sender.position) / self.entity.range - V2I_BASE_SUCCES_PROBABILITY
            
            # On lance une tentative d'emission pour tout les utilisateurs à portée de l'infrastructure
            receivers : list[User] = list(filter(lambda x: (x.id != self.entity.id) and (abs(x.position - self.entity.position) < self.entity.range) , users))
            for receiver in receivers:
                # On lance une tentative d'emission pour chaque utilisateur à portée de l'infrastructure
                timeline.append(Emission(timestamp=self.timestamp + WATTING_TIME, fail_probability=fail_probability, message=Message(id=0, sender=self.entity, origin=message.origin ,receiver=receiver.id, size=message.size, priority=message.priority, sent_from_origin_at=message.sent_from_origin_at)))
           
        else:
            if logs:
                print("Message from ", message.sender.id, " to ", self.entity.id, " is received and get treated at time: ", self.timestamp)
                
            # On ajoute à la liste des messages reçus de l'émetteur et la latence calculé
            message.origin.metrics.add_message_state(Metrics.MessageState.received)
            message.origin.metrics.add_latency(self.timestamp - message.sent_from_origin_at)
            
            
        #if logs:
        #    print("Message from ", message.origin.id, " to ", self.entity.id, " is treated at time: ", self.timestamp)
        
        # On regarde si il reste des messages dans le buffer
        if len(self.entity.buffer) > 0:
            # On lance un event traitement
            timeline.append(Treatment(self.timestamp + (message.size / self.entity.treatment_speed), self.entity))
        else:
            self.entity.busy = False
            
# Event de mouvement d'un utilisateur          
class Movement(Utils.Event):
    def __init__(self, timestamp: float, user: User):
        super().__init__(timestamp)
        self.user = user
        
    def run(self, logs: bool=False):
        if not logs:
            print("User ", self.user.id, " is moving at time: ", self.timestamp, "and is now at position: ", self.user.position)
        
        # On bouge l'utilisateur à la vitesse qu'il possède
        self.user.move()
# Event pour declencher le choix d'un algorithme
class ChooseAlgorithm(Utils.Event):
    def __init__(self, timestamp: float, entity : User):
        super().__init__(timestamp)
        self.entity = entity
        self.mab = self.entity.mab
        self.entity.algorithm = self.mab.select_arm()
        

    def run(self, logs: bool=False):
        self.mab.update(self.entity.metrics,self.entity.algorithm) 
        self.entity.algorithm = self.mab.select_arm()
        if logs:
            print(f"choix de l'algorithme {self.entity.algorithm} at {self.timestamp}")          
# Initialisation de la liste des utilisateurs
for i in range(NUMBER_OF_USERS):
    users.append(User(id=i, position=random.uniform(0, 500), protocol=0, range=20, priority=0, buffer_capacity=10, treatment_speed=0.1, mouvement_speed=random.uniform(1, 5), algorithm=Utils.Algorithm.V2I, mab=MAB_LIST[i%len(MAB_LIST)](2,(1,1,1,1,1))))



for i in range (NUMBER_OF_INFRASTRUCTURES):
    infrastructures.append(Infrastructure(id=i + NUMBER_OF_USERS, position=i*100, protocol=0, range=100, priority=0, buffer_capacity=100, treatment_speed=0.1, algorithm=Utils.Algorithm.V2V))

# Fonction qui peuple de tentative d'emission de message dans la timeline
def populate_simulation():
    
    #timeline.append(Emission(timestamp=0.0, message=Message(id=0, sender=users[0], origin=users[0], receiver=1, size=5, priority=0)))
    #timeline.append(Emission(timestamp=0.0001, message=Message(id=1, sender=users[0], origin=users[1], receiver=1, size=1, priority=0)))
    #timeline.append(Emission(timestamp=0.6, message=Message(id=2, sender=users[2], origin=users[2], receiver=1, size=1, priority=0)))
        
    # Boucle peuplant l'ensemble des mouvements des véhicules
    for user in users:
        i = 0
        while i < SIMULATION_TIME:
            i = i + 1

            # Envoie du message à l'ensemble des utilisateurs sauf l'éméteur
            # TODO: Voir si y'a mieux, beaucoup d'evènements dans la timeline
            timeline.append(TryEmission(timestamp=i, entity=user))                
            
            # Mouvement de l'utilisateur
            timeline.append(Movement(timestamp=i, user=user))

            if(not i%10 and isinstance(user,User)):# les infra vont pas vraiment faire de V2V
                timeline.append(ChooseAlgorithm(timestamp=i,entity = user))


        
# Fonction qui lance la simulation    
def run_simulation(logs: bool = False):
    
    index: int = 0
    
    if logs:
        print("Lancement de la simulation")
    
    while index < timeline.length:
        
        event = timeline.pop()
        
        if logs:
            print(f"Event at time:{event.timestamp}({event.__class__.__name__}) is running")
            print("Remaining events: ", timeline.length)
            
        #TODO: Check for bugs
        event.run(logs=False)

        
    # Fin de la simulation, check les metriques pour du debug
    if logs:
        print("=============== Fin de la simulation ===============")
        for entity in users:# + infrastructures: On ne calcule pas les metriques des infra, ça ne nous interesse pas
            entity.metrics.show_metrics(verbose=True)
            if isinstance(entity,User):
                print(f"historique des choix{entity.mab.get_arm_history()}")

# Fonction qui calcule les métriques de toutes les entités sur le réseau
def calculate_metrics(logs: bool = False):
    
    for entity in users + infrastructures:
        if logs:
            print("Calcul des métriques de l'entité ", entity.id)
        
        entity.metrics.actualise_metrics(logs)

# Simulation
populate_simulation()

run_simulation(logs=True)

calculate_metrics(logs=False)
