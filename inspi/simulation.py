import abc
import random
from enum import Enum
import utils
import matplotlib.pyplot as plt
import numpy as np


NUMBER_DEVICE = 5

# utile pour calculer le routage statique hierarchique
CA_NUMBER = 3

# index des machines dans la matrice d'adjacence :
# 0 -> CA1
# 1 -> CA2
# 2 -> CA3
# 3 -> CTS1
# 4 -> CTS2
# nombres = nombre d'appels max par lien
CONGESTION_MATRIX = [0, 10, 0, 100, 100,
                     10, 0, 10, 100, 100,
                     0, 10, 0, 100, 100,
                     100, 100, 100, 0, 1000,
                     100, 100, 100, 1000, 0]

CAPACITY_MATRIX = np.array([[0, 10, 0, 100, 100],
                            [10, 0, 10, 100, 100],
                            [0, 10, 0, 100, 100],
                            [100, 100, 100, 0, 1000],
                            [100, 100, 100, 1000, 0]])

# Tous les temps du projet sont en secondes
LAST_CALL_INSTANT = 1 * 60 * 60  # simulation sur une heure
CALLS_NUMBER = 6000

# Nombre de points pour faire la moyenne
MEAN_NUMBER = 10

# Liste des liens entre les CA et les CTS, index pour CA
CA_CTS_LINK = [3, 4, 4]

# Durée des appels minimum et maximum
MIN_CALL_DURATION = 1 * 60
MAX_CALL_DURATION = 5 * 60

# Classe destiné à la gestion d'un réseau, implémente les opérations élémentaires pour administrer correctement le réseau
class Network():

    def __init__(self):
        self.nb_failed_calls = 0
        self.__congestion_matrix = CONGESTION_MATRIX.copy()
    
    # Récupère la liste des voisins d'une machine
    def get_neighbors(self, source: int) -> list[int]:
        return np.where(CAPACITY_MATRIX[source] > 0)[0].tolist()

    # Récupère le nombre d'appel en cours sur le réseau
    def get_call_count(self):
        calls = 0
        for i in range(NUMBER_DEVICE):
            for j in range(i + 1, NUMBER_DEVICE):
                total_capacity = self.get_link_capacity(i, j)
                remaining_capacity = self.get_available_link_capacity(i, j)
                calls += total_capacity - remaining_capacity
        return calls

    # Retourne la capacité d'un lien entre deux machines
    def get_link_capacity(self, source: int, destination: int):
        return CONGESTION_MATRIX[source * NUMBER_DEVICE + destination]

    # Retourne la capacité disponible d'un lien entre deux machines
    def get_available_link_capacity(self, source, destination):
        return self.__congestion_matrix[source * NUMBER_DEVICE + destination]

    # Retourne la charge d'un lien entre deux machines en pourcentage
    def get_link_usage_percentage(self, source: int, destination: int):
        #Si lien non nul, on retourne le pourcentage d'utilisation, sinon retourne 0 car pas de lien
        if self.get_link_capacity(source, destination) > 0:
            total_capacity = self.get_link_capacity(source, destination)
            remaining_capacity = self.get_available_link_capacity(source, destination)
            return (total_capacity - remaining_capacity) / total_capacity
        return 0

    # Alloue un lien entre deux machines, renvoie si l'opération s'est bien passé
    def allocate_link(self, source: int, destination: int):
        if self.get_available_link_capacity(source, destination):
            # Communication dans les deux sens d'ou la double réduction
            self.__congestion_matrix[source * NUMBER_DEVICE + destination] -= 1
            self.__congestion_matrix[destination * NUMBER_DEVICE + source] -= 1
            return True
        return False
    
    # Libère un lien entre deux machines
    def free_link(self, source: int, destination: int):
        self.__congestion_matrix[source * NUMBER_DEVICE + destination] += 1
        self.__congestion_matrix[destination * NUMBER_DEVICE + source] += 1


# Classe pour la mise en place d'un appel.
class Call():

    def __init__(self, source: int, destination: int, starts_at: int, duration: int, algorithm: utils.RoutingAlgorithm):
    
        self.route = [] # Route de l'appel

        self.source = source # ID de la machine source de l'appel
        self.destination = destination # ID de la machine destination de l'appel
        self.starts_at = starts_at # Instant de début de l'appel
        self.duration = duration # Durée de l'appel
        self.algorithm = algorithm # Algorithme de routage sélectionné pour la mise en place de l'appel

    def init_call(self, network: Network):
        selected_route = self.algorithm.find_route(self.source, self.destination)
        if selected_route:
            self.route.append(selected_route[0])


            for i in range(1, len(selected_route)):
                if not network.allocate_link(self.route[-1], selected_route[i]):
                    self.free_call(network)
                    return False
                self.route.append(selected_route[i])
            return True
        else:
            # pas de route trouvée par find_route
            return False

    # Libère les ressources de l'appel, libère en premier les liens de la tête du chemin
    def free_call(self, network: Network):
        fst_elem = self.route.pop()
        # Tant que la route n'est pas vide, on libère les liens
        while len(self.route) > 0:
            snd_elem = self.route.pop()
            network.free_link(snd_elem, fst_elem)
            fst_elem = snd_elem

    def ends_at(self) -> int:
        return self.starts_at + self.duration


# Classe abstraite pour représenter un événement, implémente la méthode run qui sera implémentée par les classes filles
class Event():

    def __init__(self, timestamp: int, call: Call):
        self.call = call
        self.timestamp = timestamp

    @abc.abstractmethod
    def run(self, network: Network):
        pass

def random_timestamp() -> int:
    return random.randint(0, LAST_CALL_INSTANT)


def random_call(routing_method: utils.RoutingAlgorithm) -> Call:
    # Selection de 2 CA aléatoires différentes
    source = random.randint(0, CA_NUMBER - 1)
    dest = (source + random.randint(1, CA_NUMBER - 1)) % CA_NUMBER
    # Création d'un évènement d'appel
    return Call(source=source,
                destination=dest,
                starts_at=random_timestamp(),
                duration=random.randint(MIN_CALL_DURATION, MAX_CALL_DURATION),
                algorithm=routing_method,
                )


def populate_simulation(algorithm: utils.RoutingAlgorithm) -> list[Event]:
    timeline: utils.Timeline = utils.Timeline()
    for index in range(CALLS_NUMBER):
        call = random_call(algorithm)
        # mettre un nouvel appel dans la timeline
        utils.EventNewCall(call, timeline)
    return timeline

def run_simulation(timeline: list[Event], network: Network, show_more_logs: bool = False, ax=None, simulation_name: str=None) -> None:
    N = 0 # sert au calcul de la moyenne
    count_current_call: int= 0  
    maximum_current_call: int = 0
    if show_more_logs:
        usage_matrix = np.zeros((NUMBER_DEVICE, NUMBER_DEVICE)) 
        time = list(range(LAST_CALL_INSTANT + 10 * 60))
    for action in timeline:
        if show_more_logs:
            while action.timestamp > time[0]:
                N += 1
                time.pop(0)
                for i in range(NUMBER_DEVICE):
                    for j in range(i + 1, NUMBER_DEVICE):         
                        usage_matrix[i, j] = usage_matrix[i, j] + network.get_link_usage_percentage(i, j)

                nb_calls = network.get_call_count()
                count_current_call += nb_calls
                maximum_current_call = max(maximum_current_call, nb_calls)
        action.run(network)
    if show_more_logs:
        utilisation = sum([sum(utilisation[i]) for i in range(NUMBER_DEVICE)])
        print("========= RESULTAT DE LA SIMULATION : ", simulation_name, "=========")
        print("Appels en moyenne sur le réseau = ", (count_current_call / N))
        print("Appels maximum sur le réseau = ", (maximum_current_call))


class RoutingAlgorithmType(Enum):
    HIERARCHIQUE = 1
    PARTAGE_CHARGE = 2
    ADAPTATIF = 3

# Classe pour générer la simulation en fonction de l'algorithme de routage indiqué
class GenerateSimulation():

    def __init__(self, algorithm_type: RoutingAlgorithmType):
        self.algorithm_type = algorithm_type

    def get_failed_call_count(self, show_more_logs: bool = False, ax=None) -> None:
        
        # Création du réseau
        network = Network()
        
        # Création d'une timeline que l'on va peupler et ensuite exectuer pour la simulation
        timeline: list[Event] = None
        
        # Peuplement et execution de la simulation en fonction de l'algorithme de routage
        if self.algorithm_type == RoutingAlgorithmType.HIERARCHIQUE:
            timeline = populate_simulation(utils.RoutageHierarchique(network))
            run_simulation(timeline, network, show_more_logs=show_more_logs, ax=ax, simulation_name="HIERARCHIQUE")
        elif self.algorithm_type == RoutingAlgorithmType.PARTAGE_CHARGE:
            timeline = populate_simulation(utils.RoutagePartageCharge(network))
            run_simulation(timeline, network, show_more_logs=show_more_logs, ax=ax, simulation_name="PARTAGE_CHARGE")
        elif self.algorithm_type == RoutingAlgorithmType.ADAPTATIF:
            timeline = populate_simulation(utils.RoutageAdaptatif(network))
            run_simulation(timeline, network, show_more_logs=show_more_logs, ax=ax, simulation_name="ADAPTATIF")
        return network.nb_failed_calls


# Lancement de la simulation
x = []
y_routage_hierarchique = []
y_routage_adaptatif = []
y_routage_partage = []

figure = plt.figure(constrained_layout=True)
# Ajout autre figure pour les logs?
(figure0) = figure.subfigures(1, 1)
(ax) = figure0.subplots()

figure0.suptitle(("Utilisation du support par algo"))

for calls in range(100, 10000, 1000):
    
    #Dégueu, on modif une constante ici car on ne peut pas passer de paramètre à la fonction get_failed_call_count
    CALLS_NUMBER = calls   
    x.append(calls)
    
    list_simu_fail_call_h: list [int] = []
    list_simu_fail_call_p: list [int] = []
    list_simu_fail_call_a: list [int] = []

    #On utilisera ici du multiprocessing dans l'objectif de rendre les calculs pour rapide
    
    # Simulation pour le routage hiérarchique
    simulation = GenerateSimulation(RoutingAlgorithmType.HIERARCHIQUE)
    for i in range(MEAN_NUMBER):
        list_simu_fail_call_h.append(simulation.get_failed_call_count(show_more_logs=False))
        
    moy_fail_call = sum(list_simu_fail_call_h) / MEAN_NUMBER
    y_routage_hierarchique.append(moy_fail_call / calls)
    #print("Fin de la simulation routage hiérarchique avec ", calls, " appels")
    
    # Simulation pour le routage par partage de charge
    simulation = GenerateSimulation(RoutingAlgorithmType.PARTAGE_CHARGE)
    for i in range(MEAN_NUMBER):
        list_simu_fail_call_p.append(simulation.get_failed_call_count(show_more_logs=False))
        
    moy_fail_call = sum(list_simu_fail_call_p) / MEAN_NUMBER
    y_routage_partage.append(moy_fail_call / calls)
    #print("Fin de la simulation routage partage charge avec ", calls, " appels")

    # Simulation pour le routage adaptatif
    simulation = GenerateSimulation(RoutingAlgorithmType.ADAPTATIF)
    for i in range(MEAN_NUMBER):
        list_simu_fail_call_a.append(simulation.get_failed_call_count(show_more_logs=False))
        
    moy_fail_call = sum(list_simu_fail_call_a) / MEAN_NUMBER
    y_routage_adaptatif.append(moy_fail_call / calls)
    #print("Fin de la simulation routage adaptatif avec ", calls, " appels")


print("x = ", x)
print("y_routage_hierarchique = ", y_routage_hierarchique)
print("y_routage_partage = ", y_routage_partage)
print("y_routage_adaptatif = ", y_routage_adaptatif)
ax.plot(x, y_routage_hierarchique, label='routage hiérachique')
ax.plot(x, y_routage_partage, label='routage par partage de charge')
ax.plot(x, y_routage_adaptatif, label='routage adaptatif')
ax.set_xlabel("Appels")
ax.set_ylabel("Appels refusés (%)")
ax.set_title('Appels refusés en fonction du nombre d\'appels pour les 3 algorithmes')

plt.legend()
plt.show()
