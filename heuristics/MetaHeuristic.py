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
from collections import defaultdict

from ConstrainedColorGraph import ConstrainedColorGraph, EqualizedColorGraph

from heuristics.schedule_times import schedule_times
from heuristics.tools import to_binary

import numpy as np

#from sklearn.ensemble import RandomForestRegressor

class MetaHeuristic:

    def __init__(self, data, n_colorings=50):
        self.data = data
        self.n_colorings = n_colorings
        
    def generate_colorings(self):
        raise NotImplementedError()
    
    def update(self, values, best_index = None, time_slots = None):
        raise NotImplementedError()
    
    
class RandomHeuristic(MetaHeuristic):
    
    def __init__(self, data, n_colorings=50):
        MetaHeuristic.__init__(self, data, n_colorings = n_colorings)
        self.graph = ConstrainedColorGraph()
        self.graph.build_graph(self.data['n'], self.data['conflicts'])   
        self.periods = [None] * self.n_colorings
        self.mode = 0
        
    
    def generate_colorings(self):
        '''
            Generate colorings in purely random fashion. Does not check room constraints
        '''
        colorings = []
        nodes = self.graph.nodes()
        
        for i in range(self.n_colorings):
            self.graph.reset_colours()
            
            rd.shuffle(nodes)
            for node in nodes:
                self.graph.color_node(node, data=self.data, mode = self.mode, periods = self.periods[i])
            
            colorings.append({n: c for n, c in self.graph.colours.iteritems()})      
        
        return colorings
    
    
    def update(self, values, best_index = None, time_slots = None):
        '''
            Pure chance -> Nothing to be intelligent about here ;)
        ''' 
        pass

    
    
class RandomHeuristicAdvanced(RandomHeuristic):
    '''
        A variant of the random heuristic, which uses color equalization and constraint checking
    '''
    def __init__(self, data, n_colorings=50):
        RandomHeuristic.__init__(self, data, n_colorings = n_colorings)
        self.graph = EqualizedColorGraph()
        self.graph.build_graph(self.data['n'], self.data['conflicts'])   
        self.periods = { i: None for i in range(n_colorings) }
        self.mode = 1
        
    def update(self, values, best_index = None, time_slots = None):
        '''
            We use periods when checking constraints. Get them from time_solots color dict.
        '''
        if self.periods is None:
            self.periods = defaultdict(list)
        
        for i in range(len(values)):
            if time_slots[i] is not None:
                self.periods[i] = [self.data['h'].index(color) for color in time_slots[i]]
            
    
    
    
'''
class ForestHeuristic:
        Use Random Forest Regression in coloring step.
    def __init__(self, data, n_colorings=50):
        MetaHeuristic.__init__(self, data, n_colorings = n_colorings)
        self.graph = ConstrainedColorGraph()
        self.graph.build_graph(self.data['n'], self.data['conflicts'])
        self.next_X = []
        self.X = []
        self.Y = []
        self.regressor = RandomForestRegressor(n_estimators=150, min_samples_split=1)
        self.best_val = sys.maxint
        
    def generate_colorings(self):
        colorings = []
        nodes = self.graph.nodes()
        self.next_X = []
        for i in range(self.n_colorings):
            rd.shuffle(nodes)
            if len(self.Y) > 100:
                while self.regressor.predict( np.asarray( nodes ) ) > 1.5*self.best_val:
                    rd.shuffle(nodes)
                    print nodes
            
            self.graph.reset_colours()
            for node in nodes:
                self.graph.color_node(node, data=self.data, check_constraints = False)
            colorings.append({n: c for n, c in self.graph.colours.iteritems()})
            self.next_X.append( np.asarray( nodes ) )
                
        return colorings
    
    
    def update(self, values, best_index = None, time_slots = None):
        
        for i, value in enumerate(values):
            if value < sys.maxint:
                self.Y.append(value)
                self.X.append(self.next_X[i])
            if value < self.best_val:
                self.best_val = value
                
        print len(self.X), len(self.Y)
        self.regressor.fit( np.asarray(self.X), np.asarray(self.Y) )
        
        for i, value in enumerate(values):
            if value < sys.maxint:
                print "prediction", self.regressor.predict( self.next_X[i] ) 
                print "value", value
        
        #print "Do nothing. Value is", values[best_index]
        pass
    '''
    
'''
class SAHeuristic(MetaHeuristic):
 #   ''
   #     Use simulated annealing for optimizing the coloring step.
  #  ''
    def __init__(self, data, n_colorings=50):
        MetaHeuristic.__init__(self, data, n_colorings = n_colorings)
        self.graph = ConstrainedColorGraph()
        self.graph.build_graph(self.data['n'], self.data['conflicts'])
        self.visiting = []
        self.visiting_old = []
        self.old_values = []
        self.beta_0 = 20
        self.beta = self.beta_0
        self.schedule = lambda t: self.beta_0 * np.log(1+np.log(1+t))
    
        self.iteration = 1
        
    def generate_colorings(self):
        colorings = []
        nodes = self.graph.nodes()
        if len(self.visiting) == 0:
            self.visiting = [ rd.sample(nodes, len(nodes)) ] * self.n_colorings
        self.visiting_old = self.visiting
        
        for i in range(self.n_colorings):
            
            # 1. choose random color and eligible time slot
            color1 = rd.sample(nodes, int(0.1*len(nodes)))
            color2 = rd.sample(nodes, int(0.1*len(nodes)))
            while color2 == color1:
                color2 = rd.sample(nodes, int(0.1*len(nodes)))
            for c1, c2 in zip(color1, color2):
                tmp = self.visiting[i][c1]
                self.visiting[i][c1] = self.visiting[i][c2]
                self.visiting[i][c2] = tmp
            
            self.graph.reset_colours()
            for node in nodes:
                self.graph.color_node(node, data=self.data, check_constraints = False)
            colorings.append({n: c for n, c in self.graph.colours.iteritems()})
        
        self.iteration += 1
        return colorings
    
    def update(self, values, best_index = None, time_slots = None):
        if len(self.old_values) == 0:
            self.old_values = values
            pass
        
        self.beta = self.schedule(self.iteration)
        
        # acceptance steps
        for i, value in enumerate(values):   
            if value == sys.maxint:
                self.visiting[i] = self.visiting_old[i]
                continue
            if self.old_values[i] == sys.maxint:
                self.old_values[i] = value
                continue
            
            if rd.uniform(0,1) <= np.exp( -self.beta * (value - self.old_values[i]) ):
                self.old_values[i] = value
            else: # reject -> roll back
                self.visiting[i] = self.visiting_old[i]
    
'''