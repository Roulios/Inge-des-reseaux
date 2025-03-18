import random
import time
import queue
import csv

class Message:
    def __init__(self, sender_id, receiver_id, priority, size):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.priority = priority
        self.size = size
        self.timestamp = time.time()

class User:
    def __init__(self, id, protocol, range, processing_capacity, user_type):
        self.id = id
        self.protocol = protocol
        self.range = range
        self.processing_capacity = processing_capacity
        self.user_type = user_type
        self.queue = queue.PriorityQueue()

         # Define priority based on user type
        if self.user_type == 'Pedestrian':
            self.priority = 1  # Highest priority
        elif self.user_type == 'Motorcycle':
            self.priority = 2  # Second highest priority
        elif self.user_type == 'Car':
            self.priority = 3  # Lowest priority

    def send_message(self, receiver_id, message_priority, size):
        if size <= self.processing_capacity:
            message = Message(self.id, receiver_id, message_priority, size)
            # Combining user priority and message priority for overall priority
            overall_priority = self.priority + message_priority
            self.queue.put((overall_priority, message))
        else:
            print(f'Message size {size} exceeds processing capacity of {self.user_type} {self.id}.')
    
    def receive_message(self, message):
        delay = time.time() - message.timestamp
        return delay

    def process_queue(self, users):
        messages_per_receiver = {}  # Dictionnaire pour stocker les messages par destinataire
    
        while not self.queue.empty():
            _, message = self.queue.get()
            receiver = users.get(message.receiver_id, None)
            if receiver and self.within_range(receiver) and not self.protocol.network_load > 0.8:
                if receiver not in messages_per_receiver:
                    messages_per_receiver[receiver] = []  # Initialiser une nouvelle file d'attente pour le destinataire
                messages_per_receiver[receiver].append(message)  # Ajouter le message à la file d'attente du destinataire
    
        for receiver, messages in messages_per_receiver.items():
            messages.sort(key=lambda msg: msg.priority)  # Trier les messages par priorité
            for message in messages:
                transmission_delay = self.protocol.transmit_message(self, message, receiver)
                queue_delay = time.time() - message.timestamp
                metrics.update_metrics(transmission_delay, queue_delay, message.size, self.protocol.network_load)
                

    def move(self):
        self.id += random.randint(-1, 1)

    def within_range(self, other):
        distance = abs(self.id - other.id)
        return distance <= self.range

class Protocol:
    def __init__(self, name, network_load, packet_loss_rate, transmission_success_rate, transmission_time):
        self.name = name
        self.network_load = network_load
        self.packet_loss_rate = packet_loss_rate
        self.transmission_time = transmission_time
        self.transmission_success_rate = transmission_success_rate

    def transmit_message(self, sender, message, receiver):
        if receiver and random.random() < self.transmission_success_rate:  # Simulate packet loss
            # Calculate distance
            distance = abs(sender.id - receiver.id)
            # Add delay proportional to distance
            delay = self.transmission_time + 0.01 * distance  # Adjust the constant factor as needed
            time.sleep(delay)
            receiver.receive_message(message)
            self.update_network_load()
            return delay
        else:
            return None


    def update_network_load(self):
        self.network_load = random.random()  # Update network load based on random value for demonstration purposes

class Metrics:
    def __init__(self):
        self.total_transmission_delay = 0
        self.total_reception_delay = 0
        self.total_queue_delay = 0  # New variable for queue delay
        self.total_messages = 0
        self.lost_messages = 0
        self.total_network_load = 0

    def update_metrics(self, transmission_delay, queue_delay, message_size, network_load):
        if transmission_delay :
            self.total_transmission_delay += transmission_delay
            self.total_queue_delay += queue_delay
            self.total_messages += 1
            self.total_network_load += network_load
        else:
            self.lost_messages += 1

    def get_metrics(self):
        #average_transmission_delay = self.total_transmission_delay / self.total_messages if self.total_messages != 0 else None
        #average_reception_delay = self.total_reception_delay / self.total_messages if self.total_messages != 0 else None
        #average_queue_delay = self.total_queue_delay / self.total_messages if self.total_messages != 0 else None  # Calculate average queue delay
        total_delay = self.total_transmission_delay + self.total_queue_delay  # Calculate total delay
        average_delay = total_delay / self.total_messages if self.total_messages != 0 else None
        packet_loss_rate = self.lost_messages / (self.total_messages + self.lost_messages) if self.total_messages + self.lost_messages != 0 else None
        average_network_load = self.total_network_load / self.total_messages if self.total_messages != 0 else None
        return average_delay, packet_loss_rate, average_network_load


class Infrastructure:
    def __init__(self, id, protocol, processing_capacity):
        self.id = id
        self.protocol = protocol
        self.processing_capacity = processing_capacity
        self.user_type = 'Infrastructure'
        self.queue = queue.PriorityQueue()

    def send_message(self, receiver_id, message_priority, size):
        if size <= self.processing_capacity:
            message = Message(self.id, receiver_id, message_priority, size)
            overall_priority =  message_priority
            receiver = users.get(message.receiver_id, None)
            if receiver:
                receiver.queue.put((overall_priority, message))
                print(f'Infrastructure {self.id} has a new message for User {receiver_id} in queue.')
            else:
                print(f'Receiver User {receiver_id} not found.')
        else:
            print(f'Message size {size} exceeds processing capacity of Infrastructure {self.id}.')
    
    def receive_message(self, message):
        delay = time.time() - message.timestamp
        return delay

    def process_queue(self, users):
        transmission_delay = None
        queue_delay = None
        messages_per_receiver = {}  # Dictionnaire pour stocker les messages par destinataire

        while not self.queue.empty():
            _, message = self.queue.get()
            receiver = users.get(message.receiver_id, None)
            if receiver:
                if receiver not in messages_per_receiver:
                    messages_per_receiver[receiver] = []  # Initialiser une nouvelle file d'attente pour le destinataire
                messages_per_receiver[receiver].append(message)  # Ajouter le message à la file d'attente du destinataire
    
        for receiver, messages in messages_per_receiver.items():
            messages.sort(key=lambda msg: msg.priority)  # Trier les messages par priorité
            for message in messages:
                transmission_delay = self.transmit_message(message, receiver)
                queue_delay = time.time() - message.timestamp
                metrics.update_metrics(transmission_delay, queue_delay, message.size, self.protocol.network_load)
    

    def move(self):
        pass

    def within_range(self, user):
        distance = abs(self.id - user.id)
        return distance <= self.range


# Initialize protocol
protocolusers = Protocol('IEEE802.11p', 0.5, 0.1, 0.6, 0.01)
protocolinfra = Protocol('IEEE802.11p', 0.5, 0.1, 0.9, 0.01)

# Initialize users
users = {
    1: User(1, protocolusers, 5, 100, 'Pedestrian'),
    2: User(2, protocolusers, 10, 200, 'Motorcycle'),
    3: User(3, protocolusers, 15, 400, 'Car'),
    4: User(4, protocolusers, 5, 100, 'Pedestrian'),
    5: User(5, protocolusers, 10, 200, 'Motorcycle'),
    6: User(6, protocolusers, 15, 400, 'Car'),
    7: User(7, protocolusers, 5, 100, 'Pedestrian'),
    8: User(8, protocolusers, 10, 200, 'Motorcycle'),
    9: User(9, protocolusers, 15, 400, 'Car')
}

infrastructures = {
  1: Infrastructure(1, protocolinfra, 800),
  2: Infrastructure(2, protocolinfra, 800),
  3: Infrastructure(3, protocolinfra, 800),
  4: Infrastructure(4, protocolinfra, 800),
  5: Infrastructure(5, protocolinfra, 800),
  6: Infrastructure(6, protocolinfra, 800),
  7: Infrastructure(7, protocolinfra, 800),
  8: Infrastructure(8, protocolinfra, 800),
  9: Infrastructure(9, protocolinfra, 800)
}

# Initialize metrics
metrics = Metrics()

# Simulate V2V communication
users[1].send_message(2, 1, 50)
users[2].send_message(3, 1, 50)
users[3].send_message(1, 1, 50)



# Process queues and move vehicles
for _ in range(10):  # Simulate 10 time steps
     # Process users
    for user in users.values():
        result1 = user.process_queue(users)
        if result1:
            transmission_delay, queue_delay, message_size, network_load = result1
            metrics.update_metrics(transmission_delay, queue_delay, message_size, network_load)
        user.move()

     # Process infrastructures
    for infra in infrastructures.values():
        result2 = infra.process_queue(users)
        if result2:
            transmission_delay, queue_delay, message_size, network_load = result2
            metrics.update_metrics(transmission_delay, queue_delay, message_size, network_load)
        infra.move()

# Get metrics
average_delay, packet_loss_rate, average_network_load = metrics.get_metrics()
print(f'Average delay: {average_delay}, Packet loss rate: {packet_loss_rate}, Average network load: {average_network_load}')

# Save metrics to CSV file
filename = "simulation_metrics.csv"
header = []
data = [average_delay, packet_loss_rate, average_network_load]

with open(filename, "a", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerow(data)