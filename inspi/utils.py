
import abc
import random
import heapq



# Liste des liens entre les CA et les CTS, index pour CA
CA_CTS_LINK = [3, 4, 4]



class RoutingAlgorithm():

    def __init__(self, network):
        self.network = network

    @abc.abstractmethod
    def find_route(self, source: int, destination: int) -> list[int]:
        pass

# Classe implémentant l'algorithme de routage hiérarchique (statique)
class RoutageHierarchique(RoutingAlgorithm):
    def find_route(self, source: int, destination: int) -> list[int]:
        route: list[int] = []
        
        #Ajout de la source dans le chemin
        route.append(source)

        #Ajout du CTS lié au CA source
        route.append(CA_CTS_LINK[source])
        route.append(destination)

        return route

# Fonction qui permet de choisir une machine aléatoire en fonction de la capacité max des liens
def random_choices(possible_machine: list[int], weights: list[int]) -> int:
    # Pour qu'on selectionne il faut que la somme des poids dépasse un objectif fixé = choix aléatoire
    random_weights_sum_goal = random.randint(0, sum(weights))
    sum_weight = 0
    for i in range(len(possible_machine)):
        sum_weight += weights[i]
        if random_weights_sum_goal <= sum_weight:
            return possible_machine[i]

# Classe implémentant l'algorithme de routage par répartition de charge, comme le routage par partage de charge mais on prends ici pour poids la charge disponible
class RoutagePartageCharge(RoutingAlgorithm):
    def find_route(self, source: int, destination: int) -> list[int]:
        route: list[int] = [] # Chemin de l'appel
        visited_ids: list[int] = [] # Liste des machines visitées
        weights: list[int] = [] # Poids des liens pour le choix aléatoire
        route.append(source)
        visited_ids.append(source)
        
        # Bouclera tant que l'on arrive pas a selectionner la machine destination
        while route[-1] != destination:
            neighbors = self.network.get_neighbors(route[-1])
            neighbors = list(filter(lambda node_id: node_id not in visited_ids, neighbors))
            # On se limite à 3 sauts car des chemins plus longs ne sont pas pertinents
            if len(route) >= 3 and destination in neighbors:
                route.append(destination)
                return route
            
            # Calculs des poids en fonction de la capacité maximum des liens
            weights = [self.network.get_link_capacity(route[-1], i) for i in neighbors]
            next_hop = random_choices(neighbors, weights)
            route.append(next_hop)
            visited_ids.append(next_hop)
        return route


# Classe implémentant l'algorithme de routage par répartition de charge, comme le routage par partage de charge mais on prends ici pour poids la charge disponible
class RoutageAdaptatif(RoutingAlgorithm):
    def find_route(self, source: int, destination: int) -> list[int]:
        route: list[int] = [] # Chemin de l'appel
        visited_ids: list[int] = [] # Liste des machines visitées
        weights: list[int] = [] # Poids des liens pour le choix aléatoire
        route.append(source) # Ajout de la source dans le chemin
        visited_ids.append(source) # Ajout de la source dans les machines visitées

        # Bouclera tant que l'on arrive pas a selectionner la machine destination
        while route[-1] != destination:
            # Selection des voisins des voisins de la tête du chemin
            neighbors = self.network.get_neighbors(route[-1])
            neighbors = list(filter(lambda node_id: node_id not in visited_ids, neighbors))
            weights = [self.network.get_available_link_capacity(route[-1], i) for i in neighbors]
            # On se limite à 3 sauts car des chemins plus longs ne sont pas pertinents
            if len(route) > 2 and destination in neighbors:
                route.append(destination)
                return route
            
            # Calculs des poids en fonction de la capacité disponible des liens
            next_hop = random_choices(neighbors, weights)
            route.append(next_hop)
            visited_ids.append(next_hop)
        return route
    
# Classe abstraite pour représenter un événement, implémente la méthode run qui sera implémentée par les classes filles
class Event():

    def __init__(self, timestamp: int, call):
        self.call = call
        self.timestamp = timestamp

    @abc.abstractmethod
    def run(self, network):
        pass

    
# Event de début d'appel, on essaye de mettre en place une communication
class EventNewCall(Event):

    def __init__(self, call, timeline: list[Event]):
        super().__init__(timestamp=call.starts_at, call=call)
        timeline.append(self)
        self.timeline = timeline

    def run(self, network):
        # Si l'appel est initialisé, on ajoute un évènement de fin d'appel
        if self.call.init_call(network):
            self.timeline.append(EventEndCall(timestamp=self.call.ends_at(),
                                              call=self.call))
        else:
            # Echec de la tentative de mise en place de l'appel
            network.nb_failed_calls += 1

# Event de fin d'appel, on libère juste les ressources de l'appel
class EventEndCall(Event):
    def run(self, network):
        self.call.free_call(network)


# Utilisation d'une structure headqueue pour gérer les évènements
# Gain de temps considérable par rapport à une liste
class Timeline():
    def __init__(self):
        self.length = 0
        self.__index = 0
        self.__data: heapq = []

    def append(self, event: Event):
        heapq.heappush(self.__data, (event.timestamp, self.__index, event))
        self.length += 1
        self.__index += 1

    def pop(self):
        value = heapq.heappop(self.__data)[2]
        self.length -= 1
        return value

    def __iter__(self):
        return self

    def __next__(self):
        if self.length:
            return self.pop()
        else:
            raise StopIteration
