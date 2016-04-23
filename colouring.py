import networkx as nx
import random as rd
import numpy as np
import os

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')  # for not popping up windows
all_colours = ["blue", "red", "yellow", "purple", "orange", "green", "grey", "cyan"]
m = len(all_colours)


class ColorGraph(object):
    def __init__(self):
        self.DIRECTORY = "plots/"
        self.NAME = "graphcolouring"
        self.graph = nx.Graph()
        self.colours = {}
        self.incidence_matrix = None

        if not os.path.exists(self.DIRECTORY):
            os.makedirs(self.DIRECTORY)

    def add_node(self, node):
        self.graph.add_node(node)
        self.colours.setdefault(node, 'white')

    def add_edge(self, node1, node2):
        self.graph.add_edge(node1, node2)
        self.colours.setdefault(node1, 'white')
        self.colours.setdefault(node2, 'white')

    def update_color(self, node, color):
        if self.colours.get(node) is None:
            return False
        self.colours[node] = color
        return True

    def get_incidence_matrix(self):
        """ Return the node-node-incidence matrix as a dct
        """
        incidence_matrix = {}
        for edge in self.graph.edges():
            incidence_matrix.setdefault(edge[0], set())
            incidence_matrix.setdefault(edge[1], set())
            incidence_matrix[edge[0]].add(edge[1])
            incidence_matrix[edge[1]].add(edge[0])
        return incidence_matrix

    def get_degree(self):
        """ return a dictionnary {node: degree}
        """
        incidence_matrix = self.get_incidence_matrix()
        degree = {node: sum(list(incidence_matrix[node])) for node in self.graph.nodes()}
        return degree

    def check_neighbours(self, node, colour):
        n = len(self.graph.nodes())
        assert(len(self.colours) >= n)
        assert(node in self.graph.nodes())
        assert(n >= 0)

        for j in self.graph.nodes():
            if ((node, j) in self.graph.edges() or (j, node) in self.graph.edges()) & (self.colours[j] == colour):
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
        rands = np.matrix([[rd.randint(0, 2) < 1 for i in range(nb_nodes)]
                          for j in range(nb_nodes)])
        # make the matrix symmetric
        for i in range(nb_nodes):
            rands[i, i] = True
            for j in range(i + 1, nb_nodes):
                rands[j, i] = rands[i, j]
        # make edges
        for i in range(nb_nodes):
            for j in range(i + 1, nb_nodes):
                if(rands[i, j]):
                    self.add_edge(i, j)
        self.incidence_matrix = rands

    def color_graph(self, save=False):
        degree = self.get_degree()
        # degree = [self.incidence_matrix[i, range(n)].sum() - 1 for i in range(n)]
        # sort by degree
        # sl = sorted(zip(degree, range(n)))
        sl = sorted([(dg, node) for node, dg in degree.iteritems()])
        lookup_order = [x[1] for x in sl]
        # revert??
        lookup_order = reversed(lookup_order)

        counter = 1
        for node in lookup_order:
            for col in all_colours:
                if self.check_neighbours(node, col):
                    self.colours[node] = col
                    self.draw(save=save, ind=counter)
                    counter += 1
                    break

        return self.colours


n = 16
G = ColorGraph()
G.build_rand_graph(nb_nodes=n)
G.draw(save=True, ind=0)
G.color_graph(save=True)

print(G.colours)

# convert to animation
os.system("convert -delay 70 -loop 0 plots/*jpg animated.gif")
