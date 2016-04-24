import networkx as nx
import random as rd
import numpy as np
import os, glob

import matplotlib
matplotlib.use('Agg')  # for not popping up windows
import matplotlib.pyplot as plt
all_colours = ["blue", "red", "yellow", "purple", "orange", "green", "grey", "cyan", "pink", "black"]
m = len(all_colours)

class ColorGraph(object):
    def __init__(self):
        self.DIRECTORY = "plots/"
        self.NAME = "graphcolouring"
        self.graph = nx.Graph()
        self.colours = {}
        self.revert = True

        if not os.path.exists(self.DIRECTORY):
            os.makedirs(self.DIRECTORY)
            
        # clear plot directory
        for f in glob.glob(self.DIRECTORY+"*"):
            os.remove(f)
    
    def add_node(self, node):
        self.graph.add_node(node)
        self.colours.setdefault(node, 'white')

    def add_edge(self, node1, node2):
        self.graph.add_edge(node1, node2)
        self.colours.setdefault(node1, 'white')
        self.colours.setdefault(node2, 'white')

    def reset_colours(self):
        for col in self.colours:
            self.colours[col] = 'white'
            
    def update_color(self, node, color):
        if self.colours.get(node) is None:
            return False
        self.colours[node] = color
        return True

    def get_degree(self):
        """ return a dictionnary {node: degree}
        """
        degree = {node: len(self.graph.edges(node)) for node in self.graph.nodes()}
        return degree
    
    def get_chromatic_number(self):
        """ return the number of colours used
        """
        return len(set([self.colours[x] for x in self.colours]))

    def check_neighbours(self, node, colour):
        if colour in [self.colours[x[1]] for x in self.graph.edges(node) ]:
            return(False)
        return(True)

    def draw(self, save=False, ind=0):
        colours = [colour for _, colour in self.colours.iteritems()]
        nx.draw_shell(self.graph, node_color=colours)
        if save:
            filename = self.DIRECTORY + self.NAME
            if(ind < 10):
                filename = filename + '00'
            elif(ind < 100):
                filename = filename + '0'
            plt.savefig("%s%d.jpg" % (filename, ind))

    def build_rand_graph(self, nb_nodes=16):
        # construct random node-node-incidence matrix
        rands = [rd.randint(0, 2) < 1 for i in range(int(1+0.5*nb_nodes*(nb_nodes-1)))]

        # make edges
        counter = 0
        for i in range(nb_nodes):
            for j in range(i + 1, nb_nodes):
                if(rands[counter]):
                    self.add_edge(i, j)
                counter += 1

    def color_graph(self, save=False):
        degree = self.get_degree()
        sl = sorted([(dg, node) for node, dg in degree.iteritems()])
        lookup_order = [x[1] for x in sl]
        if self.revert:
            lookup_order = reversed(lookup_order)

        counter = 1
        for node in lookup_order:
            
            # respect initial condition
            if self.colours[node] != 'white':
                continue
            
            for col in all_colours:
                if self.check_neighbours(node, col):
                    self.colours[node] = col
                    self.draw(save=save, ind=counter)
                    counter += 1
                    break
                
        self.draw(save=True, ind=counter)
        return self.colours


n = 16
G = ColorGraph()
G.revert = False
G.build_rand_graph(nb_nodes=n)
G.draw(save=True, ind=0)
G.color_graph(save=False)
print(G.get_chromatic_number())

G.reset_colours()
G.revert = True
G.color_graph(save=True)
print(G.get_chromatic_number())

print(G.colours)

# convert to animation        
import time
time.sleep(1) # delays for 5 seconds
os.system("convert -delay 70 -loop 0 plots/*jpg animated.gif")
