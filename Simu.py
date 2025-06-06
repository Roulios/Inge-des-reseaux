import Utils
import random
import math
from enum import Enum
from MAB_signature import MAB
import MAB_UCB
import MAB_epsilon
import MAB_Thompson
import FullV2I
import FullV2V
from Event import *
from Entity import *
from Message import *
import Exploit_simulation

# Constante pour décrire la vitesse de la transmission physique d'un message, pas vrai dans la réalité.
MESSAGE_SPEED = 100 #distance*temps**-1
WATTING_TIME = 0.00000001 # Constante pour décaler un peu dans la timeline pour éviter les collisions.

# Temps de la simulation en secondes
SIMULATION_TIME = 100.0

# Probabilité de succès d'une emission entre 2 véhicules (ratio entre la distance et la porté pour laquelle on part du principe que il n'y aura pas d'échec)
V2V_BASE_SUCCES_PROBABILITY = 0.4

# Probabilité de succès d'une emission entre un véhicule et une infrastructure
V2I_BASE_SUCCES_PROBABILITY = 0.9

# Nombre de voiture dans la simulation
NUMBER_OF_USERS = 20

# Nombre d'infrastructure dans la simulation
NUMBER_OF_INFRASTRUCTURES = 4

#Types de MAB a utiliser 
MAB_LIST = [MAB_UCB.UCB,
            FullV2I.ChoiceV2I,
            FullV2V.ChoiceV2V,
            MAB_epsilon.EpsilonGreedy,
            MAB_Thompson.Thompson]

#Epsilon de base pour epsilonGreedy
EPSILONGREEDY_BASE = 0.3
# Timeline de la simulation, sera utilisée pour stocker les évènements
timeline: Utils.Timeline = Utils.Timeline()

# Liste de l'ensemble des utilisateurs sur notre réseau
users : list[User] = []

# Liste de l'ensemble des infrastructures sur notre réseau
infrastructures : list[Infrastructure] = []

entities : list[Entity] = []
       
# Initialisation de la liste des utilisateurs
for i in range(NUMBER_OF_USERS):
    users.append(
        User(id=i, 
        position=random.uniform(0, 200), 
        range=20, 
        priority=0, 
        buffer_capacity=5, 
        treatment_speed=0.01, 
        mouvement_speed=random.uniform(0, 1), 
        algorithm=Utils.Algorithm.V2I, 
        mab=MAB_LIST[i%len(MAB_LIST)](
                                        n_arms=2,
                                        weight=(0.3,7,0.3),#le choix d'un trop grand poid pour les latences est peu judicieux: le V2I a dans la simulation bcp plus de latence => TODO: a corriger
                                        epsilon= EPSILONGREEDY_BASE*random.random(), # on va prendre plusieurs epsilon selon la simu
                                        true_probability = [0.4,0.6]
),
        timeline=timeline,users=users,
        infrastructures=infrastructures,
        V2I_BASE_SUCCES_PROBABILITY=V2I_BASE_SUCCES_PROBABILITY*random.random(),
        V2V_BASE_SUCCES_PROBABILITY=V2V_BASE_SUCCES_PROBABILITY*random.random(),
        MESSAGE_SPEED=MESSAGE_SPEED,
        WAITING_TIME=WATTING_TIME))

for i in range (NUMBER_OF_INFRASTRUCTURES):
    infrastructures.append(
        Infrastructure(
                    id=i + NUMBER_OF_USERS, 
                    position=i*50, 
                    range=50, 
                    priority=0, 
                    buffer_capacity=30, 
                    treatment_speed=1, 
                    timeline=timeline,
                    users=users,
                    infrastructures=infrastructures,
                    V2I_BASE_SUCCES_PROBABILITY=V2I_BASE_SUCCES_PROBABILITY,
                    V2V_BASE_SUCCES_PROBABILITY=V2V_BASE_SUCCES_PROBABILITY,
                    MESSAGE_SPEED=MESSAGE_SPEED,
                    WAITING_TIME=WATTING_TIME))

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
            timeline.append(
                TryEmission(
                    timestamp=i,
                    entity=user,
                    timeline=timeline, 
                    list_users = users, 
                    list_infrastructures = infrastructures, 
                    V2I_BASE_SUCCES_PROBABILITY=V2I_BASE_SUCCES_PROBABILITY,
                    V2V_BASE_SUCCES_PROBABILITY=V2V_BASE_SUCCES_PROBABILITY,
                    MESSAGE_SPEED=MESSAGE_SPEED
                    )
                )                
            
            # Mouvement de l'utilisateur
            timeline.append(
                Movement(timestamp=i, user=user, timeline=timeline)
                )

            if(not i%3 and isinstance(user,User)):# les infra vont pas vraiment faire de V2V
                timeline.append(
                    ChooseAlgorithm(timestamp=i,entity = user, timeline=timeline)
                    )
            timeline.append(AddStatistics(
                timestamp=i,timeline=timeline,entity=user
                )
            )

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
    d_lat_hist={mab.__name__:{}for mab in MAB_LIST}
    # for e in users:
    #     d = e.metrics.latency_history()
    #     d_lat_hist[e.mab.__class__.__name__][e.id] = (d["time"],d["latency"],d["mab"])
    Exploit_simulation.show_graph(users)
# Simulation
populate_simulation()

run_simulation(logs=False)

calculate_metrics(logs=False)
