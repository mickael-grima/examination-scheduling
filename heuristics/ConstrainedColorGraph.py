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
        
        period = -1
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
    '''
        The EqualizedColorGraph combines the ideas of the EqualizedColorGraph 
        with the intruduction of time feasibility of exams and examination periods.
        A node is only colored, if there remains some time for the exams of the color.
        
        Differences to color_node of ConstrainedColorGraph
        - checks for max. number of available periods directly
        - checks for max. number of available rooms directly
        - tries to fill colors evenly with exams 
    '''
    def __init__(self, n_colours=2000):
        super(EqualizedColorGraph, self).__init__(n_colours=n_colours)
        
        self.color_slots = dict()
        
        self.color_count = defaultdict(int)
        self.min_colors = deepcopy(self.ALL_COLOURS)
        
        
    def check_neighbours(self, node, colour, data):
        """ @param node: node to consider
            @param colour: colour to check
            We check for every neighbor of node if it has colour as colour
            If not we return true, else we return false.
            If exam slots are provided we only use colors which guarantee feasibility.
        """
        neighbor_colors = [self.colours[x[1]] for x in self.graph.edges(node)]
        
        if colour in neighbor_colors:
            return(False)
        
        if 'exam_slots' in data and len(data['exam_slots']) > 0:
            exam_slots = data['exam_slots']
            if colour not in self.color_slots:
                return(True)
            #print len([slot for slot in exam_slots[node] if slot in self.color_slots[colour]])
            if len([slot for slot in exam_slots[node] if slot in self.color_slots[colour]]) <= 1:
                return(False)
        return(True)


    def reset_colours(self):
        """
            Reset all the colours to white and reset the color_count
        """
        for col in self.colours:
            self.colours[col] = self.WHITE
        
        self.color_slots = dict()
        
        self.color_count = dict()
        self.min_colors = deepcopy(self.ALL_COLOURS)
        
        

    def color_node(self, node, data={}, mode=0, periods=None):
        """
            Check the colors of the neighbors, and color the node with a different color.
            If capacities is not empty, we color the node respecting the capacities room constraint
        """
        
        ordered_colors = sorted( self.color_count, key=lambda x: self.color_count[x] )
        ordered_colors = self.min_colors + ordered_colors
        
        if len(set(ordered_colors)) != len(ordered_colors):
            print "Warning: Duplicate colors in color_node", len(ordered_colors), len(set(ordered_colors))            
        if len(ordered_colors) > data['p']:
            print "Warning: Error constructing ordered colors in color_node!", len(ordered_colors), data['p']
            
        
        #allowed_colors = [color for color in ordered_colors if not (color in self.color_count and self.color_count[color] >= data['r']) and self.check_neighbours(node, color, data)]
        #allowed_colors = [color for color in allowed_colors if mode == 0 or self.check_room_constraints(node, color, data, mode = mode, periods = periods)]
        # TODO: Choose color such that it maximizes statespace (long lists of color_slots!!!)
        
        for color in ordered_colors:
            #print color
            
            if color in self.color_count and self.color_count[color] >= data['r']:
                continue
                
            # we check whether any other neighbor has color
            if self.check_neighbours(node, color, data):
                if mode == 0 or self.check_room_constraints(node, color, data, mode = mode, periods = periods):
                    self.colours[node] = color
                    
                    if color not in self.color_count: self.color_count[color] = 0
                    self.color_count[color] += 1
                    
                    if color in self.min_colors:
                        self.min_colors.remove(color)
                    if 'exam_slots' in data and len(data['exam_slots']) > 0:
                        if color not in self.color_slots:
                            self.color_slots[color] = data['exam_slots'][node]
                        else:
                            self.color_slots[color] = [slot for slot in self.color_slots[color] if slot in data['exam_slots'][node]]
                            # break if feasibility vanished in the above line of code
                            if len(self.color_slots[color]) == 0:
                                return False
                    
                    #break afer node was chosen
                    break
        
        if self.colours[node] == self.WHITE:
            return False
        else:
            return True