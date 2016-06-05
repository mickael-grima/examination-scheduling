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


import numpy as np
import networkx as nx
import random as rd

from model.instance import force_data_format

from heuristics.best_time_schedule import best_time_schedule, easy_time_schedule
from heuristics.schedule_rooms import schedule_rooms

from model.objectives import obj1, obj2

from booth.colouring import ColorGraph
from heuristics.graph_coloring import greedy_coloring


class Ant(object):
    """ Represent an ant for the colouring graph

        starting_nodes:    nodes where to start. one node represent a connex composent.
        name:              name of the ant
        traces:            list of nodes visited in this order
    """
    def __init__(self, starting_node=None, name='Ant'):
        self.name = name
        self.starting_nodes = []
        self.traces = []

    def set_starting_node(self, starting_node):
        self.starting_node.append(starting_node)

    def walk_to_next_node(self, edges_weight, black_list=[]):
        """ @option black_list: node to not visit. I node has no other neighbor than the one in black_list
                                we don't consider the black_list
            for a given weigths, we return the next node to visit
        """
        nodes = {nod: weight for nod, weight in edges_weight.iteritems() if nod not in black_list}
        nodes = nodes or {nod: weight for nod, weight in edges_weight.iteritems()}
        nb, n = rd.randint(1, sum(nodes.itervalues())), 0
        for nod, weight in nodes.iteritems():
            n += weight
            if n >= nb:
                return nod
        return None

    def generate_coloring(self, graph, edges_weight):
        # for each connex component
        for node in self.starting_nodes:
            # start to visit the graph for one ant
            visited, current_node, nb = set(), node, 0
            while nb < 2 or current_node not in visited:
                # color the node
                graph.color_node(current_node)
                visited.add(current_node)
                self.traces.append(current_node)
                nod = self.walk_to_next_node(edges_weight[node], black_list=visited)
                current_node = nod
                nb = nb + 1 if current_node in visited else nb
        return {n: c for n, c in graph.colours.iteritems()}


# TODO: MICKAEL
class AC:
    '''
        Optimize the examination scheduling problem using ant colony optimisation.

        data:        dictionary containing all relevant data
        gamma:       weighting factor for objectives
        ants:        ants of the algorithm
        graph:       graph of the algorithm

        returns x_ik y_il, objVal
    '''
    def __init__(self, data, gamma=1.0, num_ants=50):
        self.data = data
        self.gamma = gamma
        self.ants = [Ant(name='Ant%s' % i) for i in range(num_ants)]
        self.graph = ColorGraph()
        self.edges_weight = {}  # weight on the edges

        self.initialize()

    def initialize(self):
        """ initialize the graph and build the the random coefficient of the edges
        """
        # build the graph function of the data
        self.graph.build_graph(self.data['n'], self.data['Q'])
        components = [comp for comp in nx.connected_components(self.graph.graph)]
        # for each ant, we add a starting node for each connex component
        for ant in self.ants:
            for nodes in components:
                ant.set_starting_node(rd.choice(nodes))
        # initialize the weight on edges
        for node in self.graph.graph.nodes():
            self.edges_weight.setdefault(node, {})
            weight = len(self.graph.graph.neighbors(node))
            for neighbor in self.graph.graph.neighbors(node):
                self.edges_weight[node][neighbor] = weight

    def generate_colorings(self):
        """ Generate a feasible coloring for each ant
        """
        colorings = []
        for ant in self.ants:
            colorings.append(ant.generate_coloring(self.graph, self.edges_weight))
            self.graph.reset_colours(self)
        return colorings

    def heuristic(self, coloring):
        # create preliminary feasible time schedule
        y = easy_time_schedule(coloring, self.data['h'])

        # create room plan for the fixed exams
        x = schedule_rooms(self.data, y)

        # if infeasible, return large objVal
        if x is None:
            return None, None, 1e10

        # create time schedule permuting the time solts for each coloring
        y = best_time_schedule(coloring, self.data['h'])

        # evaluate combined objectives
        objVal = obj1(self.data, x) - self.gamma * obj2(self.data, y)

        return x, y, objVal

    def update_edges_weight(self, ant, coeff=2):
        """ @param ant: bst ant, we update the weights function of its traces
            update the pheromone for each ant. We multiply the current weight on the visiting edge by coeff
        """
        for i in range(len(ant.traces) - 1):
            node = ant.traces[i]
            next_node = ant.traces[i + 1]
            if next_node not in ant.starting_nodes:
                self.edges_weight[node][next_node] *= coeff

    def optimize(self, epochs=100, reinitialize=False):
        # TODO: Initialise using meaningful values
        # ...
        #
        x, y, objVal = None, None, 1e10

        for epoch in range(epochs):
            xs, ys, objVals = dict(), dict(), dict()

            # Generate colourings
            colorings = self.generate_colorings()

            # evaluate all colorings
            for col in range(len(colorings)):
                xs[col], ys[col], objVals[col] = self.heuristic(colorings[col])

            # search for best coloring
            values = [objVals[col] for col in range(len(colorings))]
            best_index = max(range(len(values)), key=lambda i: values[i])

            # Update pheromone traces
            self.update_edges_weight(self.ants[best_index])

            # save best value so far.. MINIMIZATION
            if values[best_index] < objVal:
                x, y, objVal = xs[best_index], ys[best_index], values[best_index]

        return x, y, objVal


if __name__ == '__main__':
    n = 10
    r = 10
    p = 10
    tseed = 295

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed)

    # TODO: Construct meaningful tests
    num_ants = 10
    ac = AC(data)
    colorings = ac.generate_colorings(num_ants)
    print ac.heuristic(colorings[0])
    print (ac.optimize(num_ants))[2]
    print (ac.optimize(num_ants))[2]
