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
import logging

from ColorGraph import ColorGraph

from heuristics.schedule_times import schedule_times
from heuristics.tools import to_binary


# Responsible team member: MICKAEL

def time_heuristic(coloring, data, gamma=1):
    # create time schedule permuting the time solts for each coloring
    color_schedule, time_value = schedule_times(coloring, data, beta_0=0.01, max_iter=1e4)

    # if infeasible, return large objVal since we are minimizing
    if color_schedule is None:
        return None, sys.maxint

    # build binary variable
    time_schedule = to_binary(coloring, color_schedule, data['h'])

    return time_schedule, -time_value


def compute_weight(value, max_value, min_value, max_speed=4.0):
    if value < min_value:
        logging.warning("compute_weight: value has to be larger than min_value")
        return 1.0
    else:
        return 1.0 + max_speed * (max_value - value) / (max_value - min_value)


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
        self.starting_nodes.append(starting_node)

    def walk_to_next_node(self, edges_weight, black_list=[]):
        """ @option black_list: node to not visit. I node has no other neighbor than the one in black_list
                                we don't consider the black_list
            for a given weigths, we return the next node to visit
        """
        nodes = {nod: weight for nod, weight in edges_weight.iteritems() if nod not in black_list}
        nodes = nodes or {nod: weight for nod, weight in edges_weight.iteritems()}
        nb, n = 1.0 + rd.random() * (sum(nodes.itervalues()) - 1), 0
        for nod, weight in nodes.iteritems():
            n += weight
            if n >= nb:
                return nod
        return None

    def generate_coloring(self, graph, edges_weight, data={}):
        """ @param graph: graph to color
            @param edges_weight: weight on the edges for each node
            @cparam capacities: capacities of the rooms. If empty, we don't consider them
            generate a feasible coloring for this ant
        """
        # for each connex component
        for node in self.starting_nodes:
            # start to visit the graph for one ant
            visited, current_node, nb = set(), node, 0
            while nb < 2 or current_node not in visited:
                # color the node
                graph.color_node(current_node, data=data)
                visited.add(current_node)
                self.traces.append(current_node)
                nod = self.walk_to_next_node(edges_weight[node], black_list=visited)
                current_node = nod
                nb = nb + 1 if current_node in visited else nb
        return {n: c for n, c in graph.colours.iteritems()}


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
        self.num_ants = num_ants
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
                ant.set_starting_node(rd.choice(list(nodes)))
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
            colorings.append(ant.generate_coloring(self.graph, self.edges_weight, self.data))
            self.graph.reset_colours()
        return colorings

    def update(self, values, best_index, max_speed=5.0):
        """ @param values: for each ant, we provide an obj value. The best ant is the one with the minimal obj value
            @param best_index: best ant's index (obj value)
            @param max_speed: the maximal updating coefficient for edges
        """
        # search for best coloring
        edges = {}  # for each edge we attribute the sum of the ant's values who visited this edge
        for i in range(len(values)):
            ant, value = self.ants[i], values[i]
            for j in range(len(ant.traces) - 1):
                if self.graph.graph.has_edge(ant.traces[j], ant.traces[j + 1]):
                    edges.setdefault((ant.traces[j], ant.traces[j + 1]), 0)
                    edges[ant.traces[j], ant.traces[j + 1]] += value

        # Update the graph. update before the coefficient of each edge
        min_value = min([value for value in edges.itervalues()])
        max_value = max([value for value in edges.itervalues()])
        for edge in edges:
            edges[edge] = compute_weight(value, max_value, min_value, max_speed=max_speed)
        self.update_edges_weight(edges)

    def update_edges_weight(self, edges_weight):
        """ @param ant: bst ant, we update the weights function of its traces
            update the pheromone for each ant. We multiply the current weight on the visiting edge by coeff
        """
        for node, neighbors in self.edges_weight.iteritems():
            for neighbor, value in neighbors.iteritems():
                self.edges_weight[node][neighbor] = value * edges_weight.get((node, neighbor), 1.0)

    def optimize_time(self, epochs=100, gamma=1, reinitialize=False):
        # init best values
        y, objVal = None, sys.maxint

        # iterate
        for epoch in range(epochs):
            ys, objVals = dict(), dict()

            # Generate colourings
            colorings = self.generate_colorings()

            # evaluate all colorings
            for col, coloring in enumerate(colorings):
                ys[col], objVals[col] = time_heuristic(coloring, self.data, gamma)

            # search for best coloring
            # TODO: Replace by list() ??
            values = [objVals[col] for col in range(len(colorings))]
            best_index = np.argmax(values)

            # Update pheromone traces
            self.update(values, best_index)

            # save best value so far.. MINIMIZATION
            if values[best_index] < objVal:
                y, objVal = ys[best_index], values[best_index]
            print values, objVal

        return y, objVal


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
