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

import picos as pic
from booth.colouring import ColorGraph
from model.base_problem import BaseProblem


class ColouringGraphProblem(BaseProblem):
    def __init__(self):
        super(ColouringGraphProblem, self).__init__()
        self.colorGraph = ColorGraph()

    def set_graph(self, graph):
        self.graph = graph

    def build_graph(self, data):
        """ From a complete set of data, we extract the informations to construct the graph
            exams = nodes
            conflicts = edges
            colours = periods
        """
        for i in range(data.get('n', 0)):
            self.colorGraph.add_node(i)
        for i in range(data.get('n', 0)):
            for j in range(data.get('n', 0)):
                if data['Q'][i][j] >= 1:
                    self.colorGraph.add_edge(i, j)

    def build_dimensions(self, data):
        self.dimensions['n'] = data.get('n', 0)  # number of nodes
        self.dimensions['c'] = data.get('p', 0)  # number of colors
        if not self.dimensions['n'] or not self.dimensions['c']:
            self.logger.warning("%s: at least one variable is missing" % self.__class__.__name__)
            return False
        return True

    def build_constants(self, data):
        # e[i,j] = 1 represents the fact that there exists an edge between i and j
        self.build_graph(data)
        self.constants['e'] = {node1: {node2: 0 for node2 in self.colorGraph.graph.nodes()}
                               for node1 in self.colorGraph.graph.nodes()}
        for edge in self.colorGraph.graph.edges():
            if edge[0] != edge[1]:
                self.constants['e'][edge[0]][edge[1]] = 1
                self.constants['e'][edge[1]][edge[0]] = 1

    def build_variables(self):
        # x[i,j] = 1 represents that node i is colored with color j
        self.vars.setdefault('x', {})
        for node in range(self.dimensions['n']):
            for color in range(self.dimensions['c']):
                self.vars['x'][node, color] = self.problem.add_variable('x[%s, %s]' % (node, color), 1, vtype='binary')
        # y[j] = 1 represents taht color j is used at least one time
        self.vars.setdefault('y', {})
        for color in range(self.dimensions['n']):
            self.vars['y'][color] = self.problem.add_variable('y[%s]' % color, 1, vtype='binary')

    def build_constraints(self):
        # One color per node
        for node in range(self.dimensions['n']):
            self.problem.add_constraint(pic.sum([self.vars['x'][node, c] for c in range(self.dimensions['c'])]) == 1)
        # two neighbors has different colors
        for node1 in range(self.dimensions['n']):
            for node2 in range(self.dimensions['n']):
                for c in range(self.dimensions['c']):
                    self.problem.add_constraint(self.vars['x'][node1, c] + self.vars['x'][node2, c] <=
                                                2 - self.constants['e'][node1][node2])
        # Color is said to be used if at least onenode is colored with this color
        for node in range(self.dimensions['n']):
            for c in range(self.dimensions['c']):
                self.problem.add_constraint(self.vars['y'][c] >= 1 - self.vars['x'][node, c])

    def build_objectif(self):
        # we minimize the number of used colors
        crit = pic.sum(list(self.vars['y'].itervalues()))
        self.problem.set_objective('min', crit)

    def solve(self):
        self.problem.solve()
        # We convert the solution to a graph
        for key, var in self.vars['x'].iteritems():
            if float(str(var)) == 1.:
                self.colorGraph.update_color(key[0], key[1])