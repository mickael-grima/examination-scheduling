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
        degree = {node: len(self.graph.neighbors(node)) for node in self.graph.nodes()}
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

    def draw(self, name, save=False, ind=0):
        colours = [colour for _, colour in self.colours.iteritems()]
        nx.draw_shell(self.graph, node_color=colours)
        if save:
            filename = self.DIRECTORY + name
            if(ind < 10):
                filename = filename + '00'
            elif(ind < 100):
                filename = filename + '0'
            plt.savefig("%s%d.jpg" % (filename, ind))

    def reinitialized(self):
        """ reinitialized all colour to 'white'
        """
        self.colours = {node: 'white' for node in self.colours.iterkeys()}

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
            self.add_node(i)
            for j in range(i + 1, nb_nodes):
                if(rands[i, j]):
                    self.add_edge(i, j)
        self.incidence_matrix = rands

    def color_node(self, node):
        """ Check the colors of the neighbors, and color the node with a different color
        """
        for col in all_colours:
            if self.check_neighbours(node, col):
                self.colours[node] = col
                break

    def color_graph(self, save=False):
        degree = self.get_degree()
        # sort by degree
        sl = sorted([(dg, node) for node, dg in degree.iteritems()])
        lookup_order = [x[1] for x in sl]
        # revert??
        lookup_order = reversed(lookup_order)

        fig, ax = plt.subplots()

        counter = 1
        for node in lookup_order:
            self.color_node(node)
            # Save the pictures
            self.draw("graphcolouring", save=save, ind=counter)
            counter += 1

        return self.colours

    def color_graph_rand(self, save=False):
        """ @ param max_room: max number of room. If -1 then we can take as many rooms as we want
        We color the graph choosing randomly a node at each step
        """
        degree = self.get_degree()
        # sort by degree
        sl = sorted([(dg, node) for node, dg in degree.iteritems()])
        lookup_order = [x[1] for x in sl]
        degree = [x[0] for x in sl]
        # revert??
        lookup_order = list(reversed(lookup_order))

        fig, ax = plt.subplots()

        while lookup_order:
            rand, n, ind = rd.randint(0, sum(degree)), 0, 0
            while ind < len(degree):
                n += degree[ind]
                if n >= rand:
                    break
                ind += 1
            counter, node = 1, lookup_order[ind]
            self.color_node(node)
            # Save the pictures
            if save:
                self.draw("graphcolouring", save=save, ind=counter)
            counter += 1
            del lookup_order[ind]
            del degree[ind]

        return self.colours

    def color_graph_rand_iter(self, max_room=-1, it=10, save=False):
        """ @ param max_room: max number of room. If -1 then we can take as many rooms as we want
        We color the graph choosing randomly a node at each step
        We do the coloration it times, and we keep the graph wich has not more rooms than max_room, and with
        the minimum number of color
        """
        colours = {}
        for i in range(it):
            self.reinitialized()
            cols = self.color_graph_rand(save=save)
            max_ind_set = max([len([node for node, colour in cols.iteritems() if colour == col])
                              for col in all_colours])
            nb_color = len(set([color for node, color in cols.iteritems()]))
            # If too many rooms
            if max_room >= 0 and max_ind_set > max_room:
                continue
            # If the number of periods is larger
            if colours and nb_color >= len(set([color for node, color in colours.iteritems()])):
                continue
            colours = cols
        self.colours = colours
        return colours

    def draw_calendar(self, save=False):
        counter_colors = {color: 0 for color in all_colours}
        fig, ax = plt.subplots()
        for node in self.graph.nodes():
            color_ind = [i for i in range(len(all_colours)) if all_colours[i] == self.colours[node]][0]
            ax.bar(color_ind * 100, 40, width=100, bottom=counter_colors[self.colours[node]] * 50,
                   color=self.colours[node])
            counter_colors[self.colours[node]] += 1
        if save:
            fig.savefig("%scalendar.jpg" % self.DIRECTORY)
        else:
            plt.show()


n = 16
G = ColorGraph()
G.build_rand_graph(nb_nodes=n)
# G.color_graph_rand_iter(save=False)
G.color_graph(save=True)
G.draw_calendar(save=True)

print(G.colours)

# convert to animation
os.system("convert -delay 70 -loop 0 plots/graphcolouring*.jpg animated.gif")
