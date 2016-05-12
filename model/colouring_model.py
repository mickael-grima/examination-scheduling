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
        self.problem = pic.Problem()

    def build_dimensions(self, data):
        self.dimensions['n'] = data.get('n', 0)  # number of nodes
        self.dimensions['c'] = data.get('c', 0)  # number of colors
        self.dimensions['e'] = data.get('e', 0)  # number of edges
        if not self.dimensions['n'] or not self.dimensions['c'] or self.dimensions['e']:
            self.logger.warning("%s: at least one variable is missing" % self.__class__.__name__)
            return False
        return True

    def build_constants(self, data):
        # e[i,j] = 1 represents the fact that there exists an edge between i and j
        e = {ns: {nt: 0 for nt in self.colorGraph.graph.nodes()} for ns in self.colorGraph.graph.nodes()}
        for edge in self.colorGraph.graph.edges():
            if edge[0] != edge[1]:
                e[edge[0]][edge[1]] = 1
                e[edge[1]][edge[0]] = 1

    def build_variables(self):
        # x[i,j] = 1 represents that node i is colored with color j
        self.vars.setdefault('x', {})
        for node in self.colorGraph.graph.nodes():
            for color in self.colorGraph.graph.nodes():
                self.vars['x'][node, color] = self.problem.add_variable('x[%s, %s]' % (node, color), 1, vtype='binary')
        # y[j] = 1 represents taht color j is used at least one time
        self.vars.setdefault('y', {})
        for color in self.colorGraph.graph.nodes():
            self.vars['y'][color] = self.problem.add_variable('y[%s]' % color, 1, vtype='binary')

    def build_constraints(self):
        pass

    def build_objectif(self):
        pass

    def build_problem(self):
        """ From self.graph build the linear-problem
        """
        # ----------------- VARIABLES ------------------
        # x[i,j] = 1 represents that node i is colored with color j
        x = {}
        for node in self.colorGraph.graph.nodes():
            x.setdefault(node, [])
            for color in self.colorGraph.graph.nodes():
                x[node].append(self.problem.add_variable('x[{0}]'.format((node, color)), 1, vtype='binary'))
        # y[j] = 1 represents taht color j is used at least one time
        y = []
        for color in self.colorGraph.graph.nodes():
            y.append(self.problem.add_variable('y[{0}]'.format(color), 1, vtype='binary'))

        # ----------------- CONSTANTS ------------------
        # e[i,j] = 1 represents the fact that there exists an edge between i and j
        e = {ns: {nt: 0 for nt in self.colorGraph.graph.nodes()} for ns in self.colorGraph.graph.nodes()}
        for edge in self.colorGraph.graph.edges():
            if edge[0] != edge[1]:
                e[edge[0]][edge[1]] = 1
                e[edge[1]][edge[0]] = 1

        # ----------------- CONSTRAINTS ------------------
        # One color per node
        for node in self.colorGraph.graph.nodes():
            self.problem.add_constraint(pic.sum(x[node]) == 1)
        # two neighbors has different colors
        for node1 in self.colorGraph.graph.nodes():
            for node2 in self.colorGraph.graph.nodes():
                for c in range(len(self.colorGraph.graph.nodes())):
                    self.problem.add_constraint(x[node1][c] + x[node2][c] <= 2 - e[node1][node2])
        # Color is said to be used if at least onenode is colored with this color
        for node in self.colorGraph.graph.nodes():
            for c in range(len(self.colorGraph.graph.nodes())):
                self.problem.add_constraint(y[c] >= 1 - x[node][c])

        # ----------------- CRITERIA ------------------
        # we minimize the number of used colors
        crit = pic.sum(y)
        self.problem.set_objective('min', crit)
