import Utils
from Entity import *
from Message import *
import math
import random
# Event utilisé uniquement pour rendre le peuplement d'event de la simulation plus simple
# L'objectif est de détecter quels entité sont à une distance suffisament proche pour recevoir le message
# On évite ainsi d'envoyer des events emissions pour des objets qui sont situé à plusieurs kilomètres de distance
class TryEmission(Utils.Event):
    def __init__(self, timestamp: float, timeline, entity: Entity, list_users, list_infrastructures,V2I_BASE_SUCCES_PROBABILITY,V2V_BASE_SUCCES_PROBABILITY,MESSAGE_SPEED):
        super().__init__(timestamp,timeline)
        self.entity = entity
        self.users = list_users
        self.infrastructures = list_infrastructures    
        self.V2V_BASE_SUCCES_PROBABILITY = V2V_BASE_SUCCES_PROBABILITY
        self.V2I_BASE_SUCCES_PROBABILITY = V2I_BASE_SUCCES_PROBABILITY
        self.MESSAGE_SPEED = MESSAGE_SPEED    

    def run(self, logs: bool=False):
        receivers : list[Entity] = []
        
        # Selection de la liste des entités qui peuvent recevoir le message (on regarde la distance entre l'émetteur et les autres entités)
        if self.entity.algorithm == Utils.Algorithm.V2V:
            receivers = list(filter(lambda x: (x.id != self.entity.id) and (abs(x.position - self.entity.position) < max(self.entity.range,x.range)) , self.users))
        elif self.entity.algorithm == Utils.Algorithm.V2I:
            receivers = list(filter(lambda x: (x.id != self.entity.id) and (abs(x.position - self.entity.position) < max(self.entity.range,x.range)) , self.infrastructures))     
      
        
        # Ajout dans la timeline une tentative d'emission d'un message à chaque candidat
        for receiver in receivers:
            # Calcul de la probabilité de succès d'une émission. Plus la distance est grande, plus la probabilité de succès est faible. V2I est censé être plus fiable.
            if self.entity.algorithm == Utils.Algorithm.V2V:
                fail_probability : float = 1-math.exp(-abs(self.entity.position - receiver.position) / max(self.entity.range,receiver.range)) * self.V2V_BASE_SUCCES_PROBABILITY
            elif self.entity.algorithm == Utils.Algorithm.V2I:
                fail_probability : float = 1-math.exp(-abs(self.entity.position - receiver.position) / max(self.entity.range,receiver.range)) * self.V2I_BASE_SUCCES_PROBABILITY
                
            #on ajoute du bruit 
            fail_probability =max(min(1.0,fail_probability+self.entity.noise),0) 
            self.timeline.append(
                Emission(
                    timestamp=self.timestamp,
                    timeline=self.timeline,  
                    list_users=self.users,
                    list_infrastructures=self.infrastructures,
                    fail_probability=fail_probability, 
                    message=Message(
                        id=0, 
                        sender=self.entity, 
                        origin=self.entity, 
                        receiver=receiver.id, 
                        size=1, 
                        priority=self.entity.priority, 
                        sent_from_origin_at=self.timestamp
                        ),
                    MESSAGE_SPEED=self.MESSAGE_SPEED
                    )
                )


# Event emission d'un message.
class Emission(Utils.Event):
    
    def __init__(self, timestamp: float, timeline, message: Message, fail_probability: float,list_users, list_infrastructures,MESSAGE_SPEED):
        super().__init__(timestamp,timeline)
        self.message = message
        self.fail_probability = fail_probability
        self.users = list_users
        self.infrastructures = list_infrastructures   
        self.MESSAGE_SPEED = MESSAGE_SPEED
        
    def run(self, logs=False):
                
        if logs:
            print("Try sending message from ", self.message.origin.id, " to ", self.message.receiver, " with probability of fail: ", self.fail_probability*100 if self.fail_probability > 0 else 0, "%")
             
        # Traitement de la probabilité de succès d'une emission
        if random.random() > self.fail_probability:
            if logs:
                print("Message from ", self.message.origin.id, " to ", self.message.receiver, " is sent at time: ", self.timestamp)
                        
            # TODO: Faire un truc propre bruh
            receiver = list(filter(lambda x: x.id == self.message.receiver, self.users + self.infrastructures))[0]

            distance = abs(self.message.sender.position - receiver.position)
            
            # On lance un event reception pour chaque entité qui est dans la portée de l'émetteur
            self.timeline.append(
                Reception(timestamp=self.timestamp + distance/self.MESSAGE_SPEED, 
                timeline= self.timeline,
                message=self.message, 
                receiver=receiver
                )
            )

        else:
            if logs:
                print("Message from ", self.message.origin.id, " to ", self.message.receiver, " is dropped : Failed during emission")
                
            # Ajouter à la liste des messages dropés du sender car l'émission a échoué
            self.message.origin.metrics.add_message_state(Metrics.MessageState.failed_during_emission,self.timestamp)
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
    def __init__(self, timestamp: float, timeline, message: Message, receiver: Entity):
        super().__init__(timestamp,timeline)
        self.message = message
        self.receiver = receiver
        
    def run(self, logs: bool=False):
        if logs:
            print("Message from ", self.message.origin.id, " to ", self.receiver.id, " is received at time: ", self.timestamp)
        
        # Tentative de reception du message par l'entité.
        self.receiver.receive_message(timestamp=self.timestamp, message=self.message, logs=logs)
        
class Treatment(Utils.Event):
    """le traitement d'un message par une infrastructure"""
    def __init__(self, timestamp: float, entity: Entity,V2I_BASE_SUCCES_PROBABILITY):
        super().__init__(timestamp,entity.timeline)
        self.entity = entity
        self.users = entity.users
        self.infrastructures = entity.infrastructures
        self.V2I_BASE_SUCCES_PROBABILITY = V2I_BASE_SUCCES_PROBABILITY
        self.WAITING_TIME = entity.WATTING_TIME
        self.MESSAGE_SPEED = entity.MESSAGE_SPEED
        
    def run(self, logs: bool=False):
        # Traitement du message
        message : Message = self.entity.buffer.pop(0)
        self.entity.buffer_capacity += message.size
        
        # Si l'entité est une station, on fait en sorte qu'elle rediffuse le message à l'ensemble des voitures à portée
        if isinstance(self.entity, Infrastructure):
            if logs:
                print("Message from ", message.origin.id, " to infrastructure ", self.entity.id, "is receveid and get retransmit at time: ", self.timestamp)
                
            # Calcul de la probabilité de succès de la réémission
            fail_probability : float = abs(self.entity.position - message.sender.position) / self.entity.range - self.V2I_BASE_SUCCES_PROBABILITY
            
            # On lance une tentative d'emission pour tout les utilisateurs à portée de l'infrastructure
            receivers : list[User] = list(filter(lambda x: (x.id != self.entity.id) and (abs(x.position - self.entity.position) < self.entity.range) , self.users))
            for receiver in receivers:
                # On lance une tentative d'emission pour chaque utilisateur à portée de l'infrastructure
                self.timeline.append(
                    Emission(
                        timestamp=self.timestamp + self.WAITING_TIME,
                        timeline=self.timeline, 
                        list_users=self.users,
                        list_infrastructures = self.infrastructures,
                        fail_probability=fail_probability,
                        message=Message(
                            id=0, 
                            sender=self.entity, 
                            origin=message.origin ,
                            receiver=receiver.id, 
                            size=message.size, 
                            priority=message.priority, 
                            sent_from_origin_at=message.sent_from_origin_at
                        ),
                        MESSAGE_SPEED=self.MESSAGE_SPEED
                    )
                )
           
        else:
            if logs:
                print("Message from ", message.sender.id, " to ", self.entity.id, " is received and get treated at time: ", self.timestamp)
                
            # On ajoute à la liste des messages reçus de l'émetteur et la latence calculé
            message.origin.metrics.add_message_state(Metrics.MessageState.received,self.timestamp)
            message.origin.metrics.add_latency(
                                self.timestamp - message.sent_from_origin_at,
                                self.timestamp,
                                message.origin.algorithm
                            )
            
            
        #if logs:
        #    print("Message from ", message.origin.id, " to ", self.entity.id, " is treated at time: ", self.timestamp)
        
        # On regarde si il reste des messages dans le buffer
        if len(self.entity.buffer) > 0:
            # On lance un event traitement
            self.timeline.append(
                Treatment(
                    timestamp=self.timestamp + (message.size / self.entity.treatment_speed), 
                    entity=self.entity,
                    V2I_BASE_SUCCES_PROBABILITY=self.V2I_BASE_SUCCES_PROBABILITY
                    )
                )
        else:
            self.entity.busy = False
            
# Event de mouvement d'un utilisateur          
class Movement(Utils.Event):
    def __init__(self, timestamp: float, timeline, user: User):
        super().__init__(timestamp,timeline)
        self.user = user
        
    def run(self, logs: bool=False):
        if not logs:
            print("User ", self.user.id, " is moving at time: ", self.timestamp, "and is now at position: ", self.user.position)
        
        # On bouge l'utilisateur à la vitesse qu'il possède
        self.user.move()
# Event pour declencher le choix d'un algorithme
class ChooseAlgorithm(Utils.Event):
    def __init__(self, timestamp: float, timeline, entity : User):
        super().__init__(timestamp,timeline)
        self.entity = entity
        self.mab = self.entity.mab
        self.entity.algorithm = self.mab.select_arm()
        

    def run(self, logs: bool=False):
        self.mab.update(self.entity.metrics,self.entity.algorithm) 
        self.entity.algorithm = self.mab.select_arm()
        if logs:
            print(f"choix de l'algorithme {self.entity.algorithm} at {self.timestamp}")          

class AddStatistics(Utils.Event):
    def __init__(self, timestamp: float, timeline, entity : User):
        super().__init__(timestamp,timeline)
        self.entity = entity
        
        

    def run(self, logs: bool=False):
        self.entity.metrics.actualise_history(self.timestamp,self.entity.algorithm)
        if logs:
            print(f"new history added at {self.timestamp}")          
