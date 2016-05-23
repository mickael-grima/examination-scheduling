#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
paths = os.getcwd().split('/')
path = ''
for p in paths:
    path += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(path)

import unittest
from booth.colouring import ColorGraph


class TestColouring(unittest.TestCase):
    """ Test for testing colouring graph script
    """

    def testBuildRandGraph(self):
        """ We first check that the build graph has the right number of nodes,
        then we compare it with some other to check if it is random
        """
        n = 16
        cgraph = ColorGraph()
        cgraph.build_rand_graph(nb_nodes=n)
        # Verify if we have the right number of nodes
        self.assertEqual(len(cgraph.graph.nodes()), n)
        # We build 10 other graphs and we check how many have the same edges
        nb_same = 0
        for i in range(n):
            cg = ColorGraph()
            cg.build_rand_graph(nb_nodes=n)
            if set(cg.graph.edges()) == set(cgraph.graph.edges()):
                nb_same += 1
        self.assertNotEqual(nb_same, n)

    def testColorGraph(self):
        """ We check if two neighbors don't have the same color
        """
        n = 16
        for i in range(n):
            cgraph = ColorGraph()
            cgraph.build_rand_graph(nb_nodes=n)
            cgraph.color_graph()
            is_correct = True
            for edge in cgraph.graph.edges():
                if cgraph.colours[edge[0]] == cgraph.colours[edge[1]]:
                    is_correct = False
            self.assertTrue(is_correct)

    def testHistoryOneRand(self):
        """ We check that at each step exactly one white node is colored
        """
        n = 16
        for i in range(n):
            cgraph = ColorGraph()
            cgraph.build_rand_graph(nb_nodes=n)
            cgraph.color_graph_rand()
            nb_white = len(cgraph.colours)
            for i in range(len(cgraph.history)):
                nb_white_hist = len([w for n, w in cgraph.history[i].iteritems() if w == 'white'])
                self.assertEqual(nb_white_hist, nb_white - i)
            for node in cgraph.graph.nodes():
                self.assertEqual(cgraph.colours[node], cgraph.history[len(cgraph.history) - 1][node])

    def testHistoryRandIter(self):
        """ We check that at each step exactly one white node is colored
        """
        n = 16
        for i in range(n):
            cgraph = ColorGraph()
            cgraph.build_rand_graph(nb_nodes=n)
            cgraph.color_graph_rand_iter(it=10, save=False)
            nb_white = len(cgraph.colours)
            for i in range(len(cgraph.history)):
                nb_white_hist = len([w for n, w in cgraph.history[i].iteritems() if w == 'white'])
                self.assertEqual(nb_white_hist, nb_white - i)
            for node in cgraph.graph.nodes():
                self.assertEqual(cgraph.colours[node], cgraph.history[len(cgraph.history) - 1][node])

    def testColorGraphRand(self):
        """ We check if two neighbors don't have the same color for the rand algorithm
        """
        n = 16
        for i in range(n):
            cgraph = ColorGraph()
            cgraph.build_rand_graph(nb_nodes=n)
            cgraph.color_graph_rand_iter(it=10, save=False)
            is_correct = True
            for edge in cgraph.graph.edges():
                if cgraph.colours[edge[0]] == cgraph.colours[edge[1]]:
                    is_correct = False
            self.assertTrue(is_correct)

    def testSortedNodeHistory(self):
        """ We check if the returned list has all the nodes only one time
        """
        pass

if __name__ == "__main__":
    unittest.main()
