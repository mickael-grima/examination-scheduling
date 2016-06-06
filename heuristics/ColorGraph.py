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
import glob
from time import time, strftime
import pickle as pk
from argparse import ArgumentParser
from copy import deepcopy
import gtk

from collections import defaultdict

import matplotlib
matplotlib.use('Agg')  # for not popping up windows
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec



plt.axis('off')


def get_screen_size():
    """ return a tuple with the width and the length of the screen siye in inches
    """
    screen = gtk.Window().get_screen()
    resolution = screen.get_resolution()
    size = (screen.get_width(), screen.get_height())
    return size[0] / resolution, size[1] / resolution


class ColorGraph(object):
    
    
    def __init__(self, n_colors = 20):
        self.DIRECTORY = "%sheuristics/plots/" % PROJECT_PATH
        self.plotname = "graphcoloring"
        
        self.colors = defaultdict(int)
        self.DEFAULT_COLOR = 0 # needs to be 0!!! (by defaultdict default)
        self.ALL_COLORS = range(n_colors)
        
        self.graph = nx.Graph()
        self.revert = True
        self.history = {}

        if not os.path.exists(self.DIRECTORY):
            os.makedirs(self.DIRECTORY)

    def add_node(self, node):
        """ @param node: node
        Add node to self.graph
        """
        self.graph.add_node(node)
        self.colors.setdefault(node, self.DEFAULT_COLOR)

    def add_edge(self, node1, node2):
        self.graph.add_edge(node1, node2)
        self.colors.setdefault(node1, self.DEFAULT_COLOR)
        self.colors.setdefault(node2, self.DEFAULT_COLOR)

    def reset_history(self):
        """ reinitialized self.history to an empty dictionnary
        """
        self.history = {}

    def reset_colors(self):
        """ Reset all the colors to white
        """
        for col in self.colors:
            self.colors[col] = self.DEFAULT_COLOR

    def reset(self):
        """ do both reset_colors and reset_history
        """
        self.reset_colors()
        self.reset_history()

    def reinitialize(self):
        """ reinitialize everything
        """
        self.reset()
        self.graph = nx.Graph()

    def update_color(self, node, color):
        """ @param node: node to consider in self.graph
            @param color: color to set to this node
            Set color to node in self.colors
        """
        self.colors[node] = color

        
    def plot_history(self, save=True):
        for step in self.history:
            self.colors = self.history[step]
            self.draw(save=save, ind=step)


    def get_degree(self):
        """ return a dictionnary {node: degree}
        """
        degree = {node: len(self.graph.neighbors(node)) for node in self.graph.nodes()}
        return degree


    def get_chromatic_number(self):
        """ return the number of colors used
        """
        return len(set([self.colors[x] for x in self.colors]))


    def get_max_ind_set(self):
        """ for the given coloring give the maximum independant set size
        """
        cols = {color: len([node for node in self.graph.nodes() if self.colors[node] == color])
                for color in set([col for _, col in self.colors.iteritems()])}
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


    def check_neighbours(self, node, color):
        """ @param node: node to consider
            @param color: color to check
            We check for every neighbor of node if it has color as color
            If so we return true, else we return false
        """
        return color in [self.colors[x[1]] for x in self.graph.edges(node)] 
        

    def get_history_node_ordered(self):
        """ Give the list of node sorted such that first node was colored first, ans so on
        """
        res = []
        for step, history in self.history.iteritems():
            for node, color in history.iteritems():
                if color != self.DEFAULT_COLOR and node not in res:
                    res.append(node)
        return res


    def color_node(self, node):
        """ Check the colors of the neighbors, and color the node with a different color
        """
        for col in self.ALL_COLORS:
            if not self.check_neighbours(node, col):
                self.colors[node] = col
                break

    
    def color_graph_in_order(self, visiting_scheme):
        ''' 
        Color the graph following a given visiting scheme
        '''
        
        # Save the state
        self.history[0] = deepcopy(self.colors)

        counter = 1
        for node in visiting_scheme:

            # respect initial condition
            if self.colors[node] != self.DEFAULT_COLOR:
                continue
            
            # color node
            self.color_node(node)

            # Save the state
            self.history[counter] = deepcopy(self.colors)
            counter += 1
        
        return self.colors

    
    def color_graph(self):
        """ 
            @param save: do we save the sequence?
            We solve the coloring graph problem with a greedy algorithm
            We take the node from the biggest degree to the lowest and we color them to have no conflict
            We try to have as little colors as possible
        """
        degree = self.get_degree()

        # sort by degree
        sl = sorted([(dg, node) for node, dg in degree.iteritems()])
        lookup_order = [x[1] for x in sl]
        if self.revert:
            lookup_order = reversed(lookup_order)
        
        # color graph following visiting scheme
        color_graph_in_order(lookup_order)
        
        return self.colors


    def build_variable(self):
        """ we build the binary variable y = {(i, l): value} from the coloring solution we found
        """
        y = {}
        for i in range(len(self.graph.nodes())):
            for l in range(self.get_chromatic_number()):
                y[i, l] = 1.0 if self.colors[self.graph.nodes()[i]] == self.ALL_COLORS[l] else 0.0
        return y
        

    def draw(self, save=False, with_labels=False, ind=0, ax=None, clf=False, colors={}, pos={}):
        
        """ 
            Draw the graph with the self.colors and save it if save==true
            @param save: do we save the picture
            @param with_labels: do we write the labels of the nodes on the picture
            @param ind: index of the picture
            @param ax: if we have an ax we draw on it
            @param clf: after saving we clean the figure if clf==True
        """
        
        
        all_colors = ["#00B1EB", "#E51C39", "#FCEA10", "green", "red", "yellow", "cyan", "orange", "blue", "grey", "purple", "pink", "black"] + ['i' for i in range(1000)]
        m = len(all_colors)
        
        if not pos:
            pos = nx.spring_layout(self.graph)
        cols = [all_colors[color] for _, color in colors.iteritems()] or [all_colors[color] for _, color in self.colors.iteritems()]
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


def build_rand_graph(nb_nodes=16, probability=0.5):
    """ 
        We build a graph with exactly nb_nodes and approximately #possible_edges*probability
        @param nb_nodes: number of nodes of the constructed graph
        @param probability: the ratio of edge we want in expectation
    """
    # construct random node-node-incidence matrix
    rands = [rd.random() < probability for i in range(int(1 + 0.5 * nb_nodes * (nb_nodes - 1)))]

    G = ColorGraph()
    g = nx.Graph()
    # make edges
    counter = 0
    for i in range(nb_nodes):
        g.add_node(i)
        for j in range(i + 1, nb_nodes):
            if(rands[counter]):
                g.add_edge(i, j)
            counter += 1
    G.graph = g
    return G

if __name__ == '__main__':
    print "ok"
    #G = build_rand_graph(nb_nodes=4)
    #G.draw(save=True)
    G = ColorGraph()
    G.draw(save=True)