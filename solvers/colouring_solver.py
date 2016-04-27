#!/usr/bin/env python
# -*- coding: utf-8 -*-

import picos as pic
from colouring import ColorGraph


class ColouringGraphProblem(object):
    def __init__(self):
        self.colorGraph = ColorGraph()
        self.problem = pic.Problem()

    def set_graph(self, graph):
        self.graph = graph
        self.problem = pic.Problem()

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
