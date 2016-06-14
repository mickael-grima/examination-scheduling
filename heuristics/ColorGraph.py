#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import random as rd
from copy import deepcopy

import matplotlib
matplotlib.use('Agg')  # for not popping up windows
import matplotlib.pyplot as plt


plt.axis('off')


class ColorGraph(object):
    def __init__(self):
        self.DIRECTORY = "%sbooth/plots/" % PROJECT_PATH
        self.plotname = "graphcolouring"

        self.ALL_COLOURS = [i for i in range(2000)]
        self.WHITE = -1

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
        self.colours.setdefault(node, self.WHITE)

    def add_edge(self, node1, node2):
        self.graph.add_edge(node1, node2)
        self.colours.setdefault(node1, self.WHITE)
        self.colours.setdefault(node2, self.WHITE)

    def reset_history(self):
        """ reinitialized self.history to an empty dictionnary
        """
        self.history = {}

    def reset_colours(self):
        """
            Reset all the colours to white
        """
        for col in self.colours:
            self.colours[col] = self.WHITE

    def reset(self):
        """ do both reset_colours and reset_history
        """
        self.reset_colours()
        self.reset_history()

    def reinitialize(self):
        """ reinitialize everything
        """
        self.reset()
        self.graph = nx.Graph()

    def plot_history(self, save=True):
        for step in self.history:
            self.colours = self.history[step]
            self.draw(save=save, ind=step)

    def nodes(self):
        """ return a dictionnary {node: degree}
        """
        return self.graph.nodes()

    def get_degree(self):
        """ return a dictionnary {node: degree}
        """
        degree = {node: len(self.graph.neighbors(node)) for node in self.graph.nodes()}
        return degree

    def get_chromatic_number(self):
        """ return the number of colours used
        """
        return len(set([self.colours[x] for x in self.colours]))

    def get_max_ind_set(self):
        """ for the given colouring give the maximum independant set size
        """
        cols = {colour: len([node for node in self.graph.nodes() if self.colours[node] == colour])
                for colour in set([col for _, col in self.colours.iteritems()])}
        return max([value for _, value in cols.iteritems()])

    def get_schedule_plan(self):
        """ Return a dictionnary of dependencies for each node
            e.g.: {1: [2, 3], 2: [1,4], 3: [1], 4: [2], 5: []}
        """
        schedule_plan = {}
        for edge in self.graph.edges():
            schedule_plan.setdefault(edge[0], {})
            schedule_plan[edge[0]].setdefault('S%s' % edge[0], edge[1])
            schedule_plan.setdefault(edge[1], {})
            schedule_plan[edge[1]].setdefault('S%s' % edge[1], edge[0])
        return schedule_plan

    def check_neighbours(self, node, colour):
        """ @param node: node to consider
            @param colour: colour to check
            We check for every neighbor of node if it has colour as colour
            If not we return true, else we return false
        """
        if colour in [self.colours[x[1]] for x in self.graph.edges(node)]:
            return(False)
        return(True)

    def get_history_node_ordered(self):
        """ Give the list of node sorted such that first node was coloured first, ans so on
        """
        res = []
        for step, history in self.history.iteritems():
            for node, colour in history.iteritems():
                if colour != self.WHITE and node not in res:
                    res.append(node)
        return res

    def draw(self, save=False, with_labels=False, ind=0, ax=None, clf=False, colours={}, pos={}):
        """ @param save: do we save the picture
            @param with_labels: do we write the labels of the nodes on the picture
            @param ind: index of the picture
            @param ax: if we have an ax we draw on it
            @param clf: after saving we clean the figure if clf==True
            Draw the graph with the self.colours and save it if save==true
        """
        if not pos:
            pos = nx.spring_layout(self.graph)
        cols = [colour for _, colour in colours.iteritems()] or [colour for _, colour in self.colours.iteritems()]
        nx.draw(self.graph, pos, node_color=cols, with_labels=with_labels, ax=ax, node_size=1500,
                labels={node: "P%s" % node for node in self.graph.nodes()}, font_size=16)
        if save:
            filename = self.DIRECTORY + self.plotname
            if(ind < 10):
                filename = filename + '00'
            elif(ind < 100):
                filename = filename + '0'
            plt.savefig("%s%s.jpg" % (filename, ind))
        else:
            plt.show()
        if clf:
            plt.clf()

    def build_variable(self):
        """ we build the variable y = {(i, l): value} from the colouring solution we found
        """
        y = {}
        for i in range(len(self.graph.nodes())):
            for l in range(self.get_chromatic_number()):
                y[i, l] = 1.0 if self.colours[self.graph.nodes()[i]] == self.ALL_COLOURS[l] else 0.0
        return y

    def build_graph(self, nb_nodes, conflicts):
        """ @param data: dimensions of the problem and conflicts matrice
        """
        for i in range(nb_nodes):
            self.add_node(i)
            for j in conflicts[i]:
                if i != j:
                    self.add_edge(i, j)

    def build_rand_graph(self, nb_nodes=16, probability=0.5):
        """ @param nb_nodes: number of nodes of the constructed graph
            @param probability: the ratio of edge we want in expectation
            We build a graph with exactly nb_nodes and approximately #possible_edges*probability
        """
        # construct random node-node-incidence matrix
        rands = [rd.random() < probability for i in range(int(1 + 0.5 * nb_nodes * (nb_nodes - 1)))]

        # make edges
        counter = 0
        for i in range(nb_nodes):
            self.add_node(i)
            for j in range(i + 1, nb_nodes):
                if(rands[counter]):
                    self.add_edge(i, j)
                counter += 1

    def color_node(self, node):
        """ Check the colors of the neighbors, and color the node with a different color.
            If capacities is not empty, we color the node respecting the capacities room constraint
        """
        for col in self.ALL_COLOURS:
            # we check if every other neighbors don't have col as colour
            if self.check_neighbours(node, col):
                self.colours[node] = col
                break

    def color_graph(self):
        """ @param save: do we save the sequence?
            We solve the colouring graph problem with a greedy algorithm
            We take the node from the biggest degree to the lowest and we color them to have no conflict
            We try to have as little colours as possible
        """
        degree = self.get_degree()

        # sort by degree
        sl = sorted([(dg, node) for node, dg in degree.iteritems()])
        lookup_order = [x[1] for x in sl]
        if self.revert:
            lookup_order = reversed(lookup_order)

        # Save the state
        self.history[0] = deepcopy(self.colours)

        counter = 1
        for node in lookup_order:

            # respect initial condition
            if self.colours[node] != self.WHITE:
                continue

            self.color_node(node)

            # Save the state
            self.history[counter] = deepcopy(self.colours)

            counter += 1

        return self.colours

    def color_graph_rand(self):
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

        # Save the state
        self.history[0] = deepcopy(self.colours)

        counter = 1
        while lookup_order:
            rand, n, ind = rd.randint(0, sum(degree)), 0, 0
            while ind < len(degree):
                n += degree[ind]
                if n >= rand:
                    break
                ind += 1
            node = lookup_order[ind]
            self.color_node(node)
            # Save the state
            self.history[counter] = deepcopy(self.colours)

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
        colours, history, min_chromatic_number = {}, {}, []
        for i in range(it):
            self.reset()
            cols = deepcopy(self.color_graph_rand())
            max_ind_set = max([len([node for node, colour in cols.iteritems() if colour == col])
                              for col in self.ALL_COLOURS])
            nb_color = len(set([color for node, color in cols.iteritems()]))
            min_chromatic_number.append(len(set([color for node, color in colours.iteritems()])))
            # If too many rooms
            if max_room >= 0 and max_ind_set > max_room:
                continue
            # If the number of periods is larger
            if colours and nb_color >= len(set([color for node, color in colours.iteritems()])):
                continue
            colours = cols
            history = deepcopy(self.history)
        self.colours = colours
        self.history = history
        return colours
