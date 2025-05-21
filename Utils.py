import heapq
import abc

# Classe définissant une timeline.
# Une timeline est une liste d'évènements ordonnée par leur timestamp.
# On utilise un tas à priorité pour stocker les évènements pour simuler une timeline sans avoir à littéralement
# attendre le temps de parcours de la timeline.
class Timeline():
    def __init__(self):
        self.length = 0
        self.__index = 0
        self.__data: heapq = []

    def append(self, event):
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


# Classe abstraite pour représenter un événement, implémente la méthode run qui sera implémentée par les classes filles
class Event():

    def __init__(self, timestamp: float ):
        self.timestamp = timestamp

    @abc.abstractmethod
    def run(self):
        pass
    

#enum qui représente l'un des 2 protocoles de communication, le V2V et le V2I
class Algorithm(Enum):
    V2V = 0
    V2I = 1

  
# Event emission d'un message.
