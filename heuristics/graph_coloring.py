import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)


import networkx as nx
from booth.colouring import ColorGraph

def greedy_coloring(data, visiting_scheme):
    
    # TODO: Implement greedy graph coloring algorithm which uses room capacities as boundary conditions
    
    # TODO: Use ColoGraph API for this, please. Might come in handy!
    
    # TODO: Consider constraints for feasible rooms
    
    n = data['n']
    conflicts = data['conflicts']
    
    CG = ColorGraph(n_colors = n)
    for i in range(n):
        CG.add_node(i)
    for i in range(n):    
        for j in conflicts[i]:
            CG.add_edge(i,j)
            
    for i in visiting_scheme:
        
    coloring = range(data['n'])
    return coloring 








class ColorGraph(object):
    def __init__(self):
        self.DIRECTORY = "%sbooth/plots/" % PROJECT_PATH
        self.plotname = "graphcolouring"
        self.ALL_COLOURS = [str(i) for i in range(20)]

        self.graph = nx.Graph()
        self.colours = {}
        self.revert = True
        self.history = {}

        if not os.path.exists(self.DIRECTORY):
            os.makedirs(self.DIRECTORY)

    def add_node(self, node):
        """ @param node: node
        Add node to self.graph
        """
        self.graph.add_node(node)
        self.colours.setdefault(node, 'white')

    def add_edge(self, node1, node2):
        self.graph.add_edge(node1, node2)
        self.colours.setdefault(node1, 'white')
        self.colours.setdefault(node2, 'white')

    def reset_history(self):
        """ reinitialized self.history to an empty dictionnary
        """
        self.history = {}

    def reset_colours(self):
        """ Reset all the colours to white
        """
        for col in self.colours:
            self.colours[col] = 'white'

    def reset(self):
        """ do both reset_colours and reset_history
        """
        self.reset_colours()
        self.reset_history()

    def reinitialize(self):

    def update_color(self, node, color):
        """ @param node: node to consider in self.graph
            @param color: color to set to this node
            Set color to node in self.colours
        """

    def plot_history(self, save=True):

    def get_degree(self):
        """ return a dictionnary {node: degree}
        """
        
    def get_chromatic_number(self):
        """ return the number of colours used
        """
        
    def get_max_ind_set(self):
        """ for the given colouring give the maximum independant set size
        """
        
    def get_schedule_plan(self):
        """ Return a dictionnary of dependencies for each node
            e.g.: {1: [2, 3], 2: [1,4], 3: [1], 4: [2], 5: []}
        """
        
    def check_neighbours(self, node, colour):
        """ @param node: node to consider
            @param colour: colour to check
            We check for every neighbor of node if it has colour as colour
            If not we return true, else we return false
        """
        
    def get_history_node_ordered(self):
        