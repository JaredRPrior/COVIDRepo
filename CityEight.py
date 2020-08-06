import networkx as nx
import random
import osmnx as ox

BETA = .5 # Infection probability
SIGMA = 4 # Number of days someone stays in Exposed state
MU = 16 # Number of days someone stays in Infected State

# Possible states that a node could be in
SUSCEPTIBLE_STATE = "Susceptible"
EXPOSED_STATE = "Exposed"
INFECTED_STATE = "Infected"
REMOVED_STATE = "Removed"

class City:
    def __init__(self, location, number_initial_infections, network, density):
        self.city_name = location
        self.network = network
        self.density = density
        self.beta = BETA
        self.sigma = SIGMA
        self.mu = MU
        self.number_infected = 0
        self.number_exposed = 0
        self.number_removed = 0
        self.cumulative_infections = 0
        self.init_graph()
        self.network_keys = list(self.network.nodes())
        self.init_infections = number_initial_infections
        self.init_infection(self.init_infections)
        self.deaths = 0
        self.color_map = []

    def init_graph(self):
        """Improve the functionality of our graph """
        one_percent_of_nodes = self.network.number_of_nodes() * .01
        num_swaps = round(one_percent_of_nodes * (self.density/10))
        #self.network = nx.double_edge_swap(self.network, nswap=num_swaps,max_tries=num_swaps*10)

    def init_infection(self, number_initial_infections):
        """Initially infect a certain number of nodes in a network"""
        nx.set_node_attributes(self.network, SUSCEPTIBLE_STATE, 'state') #Everyone starts succeptible
        nx.set_node_attributes(self.network, float('inf'), 'duration')
        while (self.number_infected < number_initial_infections):
            initial_infect_index = self.network_keys[random.randint(0, len(self.network_keys) - 1)] # get an initial sick node
            self.network.nodes(data=True)[initial_infect_index]['state'] = INFECTED_STATE #infect that node
            self.network.nodes(data=True)[initial_infect_index]['duration'] = self.mu
            self.number_infected += 1
            
    def refresh_city(self):
        """Clean slate"""
        self.number_exposed = 0
        self.number_removed = 0
        self.number_infected = 0
        for node_index in self.network_keys: # for every node
            if self.network.nodes[node_index]['state'] != SUSCEPTIBLE_STATE:
                self.network.nodes[node_index]['state'] = SUSCEPTIBLE_STATE
        self.init_infection(self.init_infections)
    
    def run_seir(self, number_of_steps, SD, b):
        """ Method to run an SEIR Model on the city network for a given number of steps"""
        #loop through infection process 
        for step in range(number_of_steps): #loop through the number of steps
            #print("Starting SEIR Time Step: ", step)
            
            for node_index in self.network_keys: # for every node
                if self.network.nodes[node_index]['state'] == INFECTED_STATE: #If that node is infected
                    self.network.nodes[node_index]['duration'] -= 1
                    if (self.network.nodes[node_index]['duration']) == 0:
                        self.network.nodes[node_index]['state'] = REMOVED_STATE
                        if random.random()<0.007:
                            self.deaths+=1
                        self.number_removed += 1
                        self.number_infected -= 1

                    for neighbor in list(self.network.neighbors(node_index)): #Loop through all the neighbors of that node
                        threshold = self.beta
                        if SD == True: # if social distancing
                            threshold=self.beta*b # reduce probability of infection by some factor
                        if(random.random() <= threshold and self.network.nodes[neighbor]['state'] == SUSCEPTIBLE_STATE): # If some random number is greater than beta and the person is not immune then we will infect the neighbor
                            self.network.nodes[neighbor]['state'] = EXPOSED_STATE #infect Neighbor
                            self.network.nodes[neighbor]['duration'] = self.sigma + random.randint(-2,2)
                            self.number_exposed += 1
                        
                elif self.network.nodes[node_index]['state'] == EXPOSED_STATE:
                    self.network.nodes[node_index]['duration'] -= 1
                    if (self.network.nodes[node_index]['duration']) == 0:
                        self.network.nodes[node_index]['state'] = INFECTED_STATE
                        self.network.nodes[node_index]['duration'] = self.mu + random.randint(-1, 8)
                        self.number_infected += 1
                        self.cumulative_infections += 1

    def introduce_infected_node(self):
        """Method to infect a random node"""
        infect_index = random.randint(0, len(self.network_keys) - 1)
        infect_index = self.network_keys[infect_index]
        while (self.network.nodes[infect_index]['state'] != SUSCEPTIBLE_STATE):
            infect_index = self.network_keys[random.randint(0, len(self.network_keys) - 1)]
        self.network.nodes[infect_index]['state'] = EXPOSED_STATE #infect that node
        self.network.nodes[infect_index]['duration'] = self.sigma + random.randint(-1, 0)
        self.number_exposed += 1