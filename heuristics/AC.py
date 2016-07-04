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

from ConstrainedColorGraph import ConstrainedColorGraph, EqualizedColorGraph

from heuristics.schedule_times import schedule_times
from heuristics.tools import to_binary


# Responsible team member: MICKAEL

def time_heuristic(coloring, data, gamma=1):
    # create time schedule permuting the time solts for each coloring
    color_schedule, time_value = schedule_times(coloring, data, beta_0=0.01, max_iter=300)

    # if infeasible, return large objVal since we are minimizing
    if color_schedule is None:
        return None, sys.maxint

    # build binary variable
    time_schedule = to_binary(coloring, color_schedule, data['h'])

    return time_schedule, -time_value


def compute_weight(value, **kwards):
    """ function that make value positiv and that is decreasing when value increases
    """
    if kwards.get('max_value') is not None:
        max_value = kwards['max_value']
        return max_value - value


class Ant(object):
    """ Represent an ant for the colouring graph

        starting_nodes:    nodes where to start. one node represent a connex composent.
        name:              name of the ant
        traces:            list of nodes visited in this order
    """
    def __init__(self, starting_node=None, name='Ant'):
        self.name = name
        self.starting_nodes = {}
        self.traces = []
        self.has_feasible_colouring = True

    def set_starting_node(self, starting_node, neighbors):
        self.starting_nodes[starting_node] = neighbors

    def walk_to_next_node(self, node, edges_weight, white_list=[]):
        """ @option black_list: node to not visit. I node has no other neighbor than the one in white_list
                                we consider only the white_list
            for a given weigths, we return the next node to visit
        """
        nodes = {nod: weight for nod, weight in edges_weight.iteritems() if nod in white_list}
        nodes = nodes or {nod: weight for nod, weight in edges_weight.iteritems()}
        nb, n = rd.random() * sum(nodes.itervalues()), 0
        for nod, weight in nodes.iteritems():
            n += weight
            if n >= nb:
                return nod
        return None

    def generate_coloring(self, graph, edges_weight, data={}, mode=0):
        """ @param graph: graph to color
            @param edges_weight: weight on the edges for each node
            @cparam capacities: capacities of the rooms. If empty, we don't consider them
            generate a feasible coloring for this ant
        """
        # for each connex component
        if not self.starting_nodes:
            logging.warning("%s.generate_coloring: try to colour graph, but no starting nodes found"
                            % self.__class__.__name__)
        count_node = {}
        for node, neighbors in self.starting_nodes.iteritems():
            # start to visit the graph for one ant
            not_seen, current_node = set(neighbors), node
            while not_seen:
                # color the node
                if current_node is None:
                    raise Exception("current_node is None")
                if current_node in not_seen:
                    graph.color_node(current_node, data=data, mode=mode)
                    not_seen.remove(current_node)
                count_node.setdefault(current_node, 0)
                count_node[current_node] += 1
                self.traces.append(current_node)
                current_node = self.walk_to_next_node(current_node, edges_weight[current_node], white_list=not_seen)
        res = {}
        for n, c in graph.colours.iteritems():
            if c < 0:
                return {}
            res[n] = c
        return res


class AC:
    '''
        Optimize the examination scheduling problem using ant colony optimisation.

        data:        dictionary containing all relevant data
        gamma:       weighting factor for objectives
        ants:        ants of the algorithm
        graph:       graph of the algorithm

        returns x_ik y_il, objVal
    '''
    def __init__(self, data, gamma=1.0, num_ants=50, n_colors=2000):
        self.data = data
        self.gamma = gamma
        self.ants = [Ant(name='Ant%s' % i) for i in range(num_ants)]
        self.num_ants = num_ants
        print "AC: setting n_colors to data['p']!"
        n_colors = data['p']
        self.graph = EqualizedColorGraph(n_colours=n_colors)
        self.edges_weight = {}  # weight on the edges

        self.initialize()

    def initialize(self):
        """ initialize the graph and build the the random coefficient of the edges
        """
        # build the graph function of the data
        self.graph.build_graph(self.data['n'], self.data['conflicts'])
        components = [comp for comp in nx.connected_components(self.graph.graph)]

        # for each ant, we add a starting node for each connex component
        for ant in self.ants:
            for nodes in components:
                ant.set_starting_node(rd.choice(list(nodes)), nodes)

        # initialize the weight on edges
        for node in self.graph.graph.nodes():
            self.edges_weight.setdefault(node, {})
            for neighbor in self.graph.graph.neighbors(node):
                if node != neighbor:
                    self.edges_weight[node][neighbor] = 100.0

    def generate_colorings(self, mode=0):
        """ Generate a feasible coloring for each ant
        """
        colorings = []
        for ant in self.ants:
            colorings.append(ant.generate_coloring(self.graph, self.edges_weight, self.data,
                             mode=mode))
            self.graph.reset_colours()
        return filter(bool, colorings)

    def update(self, values, best_index=None, time_slots=None, max_speed=1.1, nb_ants=-1, evaporating_factor=0.5):
        """ @param values: for each ant, we provide an obj value. The best ant is the one with the minimal obj value
            @param best_index: best ant's index (obj value)
            @param max_speed: the maximal updating coefficient for edges
            @param nb_ants: how many ants do we consider to modify the edges' weight? if -1 we consider each of them
        """
        # We first decrease the weight on the edges with evaporating parameter
        for node, nodes in self.edges_weight.iteritems():
            for n in nodes:
                self.edges_weight[node][n] *= evaporating_factor

        # We add the objective value we found to the edges' weight
        nb_iter = min(nb_ants if nb_ants >= 0 else sys.maxint, len(self.ants), len(values))
        max_value = max([v for v in values])
        for i in range(nb_iter):
            ant, value = self.ants[i], values[i]
            if ant.has_feasible_colouring:
                visited = set()
                for j in range(len(ant.traces) - 1):
                    node, next_node = ant.traces[j], ant.traces[j + 1]
                    if self.graph.graph.has_edge(node, next_node) and (node, next_node) not in visited:
                        visited.add((node, next_node))
                        visited.add((next_node, node))
                        self.edges_weight[node][next_node] += compute_weight(value, max_value=max_value)

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
    ac = AC(data, num_ants=num_ants)
    y, obj = ac.optimize_time()
