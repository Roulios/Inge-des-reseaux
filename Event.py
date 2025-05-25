import Utils
from Entity import *
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
