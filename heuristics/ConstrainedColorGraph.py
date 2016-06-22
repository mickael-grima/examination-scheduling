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

from heuristics.ColorGraph import ColorGraph
from heuristics.schedule_rooms import schedule_rooms_in_period, schedule_greedy
from collections import defaultdict
from operator import itemgetter
from copy import deepcopy
import random as rd
        


def check_rooms_constraint(nodes, data):
    """
        Check if rooms capacities constraint is fullfilled for the nodes that already have color as color
        @param nodes: nodes with that to color
    """
    
    c, s, r = data.get('c', []), data.get('s', []), data.get('r', 0)

    # sort students and capacities
    students = sorted([(i, s[i]) for i in nodes], key=lambda x: x[1], reverse=True) if s else []
    capacities = sorted([c[k] for k in range(r)], reverse=True)

    #WARNING: ERROR!
    i, k = 0, 0
    while i < len(nodes) and k < r:
        if students[i][1] <= capacities[k]:
            i += 1
        k += 1
    #WARNING: ERROR!

    # Do we have exams without rooms
    return i < len(nodes)


class ConstrainedColorGraph(ColorGraph):
    def __init__(self, n_colours=2000):
        super(ConstrainedColorGraph, self).__init__(n_colours = n_colours)
        
    def check_room_constraints(self, node, color, data, mode = 1, periods = None):
        """
            Check if rooms capacities constraint is fullfilled for the nodes that already have color as color
            Use ILP in order to get this feasibility
            @param node: node to color
            @param color: color for coloring node
            @param periods: period for given color
        """
        assert mode > 0 and mode < 3, mode
        
        period = 0
        if periods is not None and color < len(periods):
            period = periods[color]
        
        # get all nodes with that color
        nodes = [nod for nod, col in self.colours.iteritems() if col == color] + [node]
        if mode == 1: # greedy scheduling heuristic
            return schedule_greedy(nodes, period, data) is not None
        elif mode == 2: # ILP
            return schedule_rooms_in_period(nodes, period, data) is not None
        elif mode == 3:
            return check_rooms_constraint(nodes, data)


    def color_node(self, node, data={}, mode=0, periods=None):
        """
            Check the colors of the neighbors, and color the node with a different color.
            If capacities is not empty, we color the node respecting the capacities room constraint
            @ Param mode:
                0 - Don't check constraints
                1 - Use greedy scheduling for checking constraints
                2 - Use ILP feasibility
                3 - Use hand picked heuristic
        """
        #rd.shuffle(self.ALL_COLOURS)
        for color in self.ALL_COLOURS:
            # we check if every other neighbors don't have col as color
            if self.check_neighbours(node, color):
                if mode == 0 or self.check_room_constraints(node, color, data, mode = mode, periods = periods):
                    self.colours[node] = color
                    break



class EqualizedColorGraph(ConstrainedColorGraph):
    def __init__(self, n_colours=2000):
        super(EqualizedColorGraph, self).__init__(n_colours=n_colours)
        self.color_exams = defaultdict(list)
        self.color_count = [0]*self.n_colours
        
        self.color_count_new = defaultdict(int)
        self.min_colors = deepcopy(self.ALL_COLOURS)
        
    '''
        differences to color_node of ConstrainedColorGraph
        - checks for max. number of available periods directly
        - checks for max. number of available rooms directly
        - tries to fill colors evenly with exams 
    ''' 

    def reset_colours(self):
        """
            Reset all the colours to white and reset the color_count
        """
        for col in self.colours:
            self.colours[col] = self.WHITE
        
        self.color_count_new = defaultdict(int)
        self.min_colors = deepcopy(self.ALL_COLOURS)
        self.color_count = [0 for c in self.color_count]


    def color_node(self, node, data={}, mode=0, periods=None):
        """
            Check the colors of the neighbors, and color the node with a different color.
            If capacities is not empty, we color the node respecting the capacities room constraint
        """
        
        ordered_colors = sorted( self.color_count_new, key=lambda x: self.color_count_new[x] )
        ordered_colors = self.min_colors + ordered_colors
        
        #ordered_colors = [elmts[0] for elmts in sorted(zip(self.ALL_COLOURS, self.color_count), key=itemgetter(1))]
        #ordered_colors = [col for col in ordered_colors if self.color_count[col] > 0]
        #print ordered_colors
        assert len(ordered_colors) <= data['p']
        
        #if len(ordered_colors) < data['p']:
            #for col in self.ALL_COLOURS:
                #if self.color_count[col] > 0:
                    #continue
                #self.colours[node] = col
                #self.color_count[col] += 1
                #return

        for col in ordered_colors:

            # continue if the current color already has too many exams
            if self.color_count[col] >= data['r']:
                continue

            # we check whether any other neighbor has col as color
            if self.check_neighbours(node, col):
                if mode == 0 or self.check_room_constraints(node, col, data, mode = mode, periods = periods):
                    self.colours[node] = col
                    self.color_count[col] += 1
                    self.color_count_new[col] += 1
                    if col in self.min_colors:
                        self.min_colors.remove(col)
                    break