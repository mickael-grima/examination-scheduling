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


class ConstrainedColorGraph(ColorGraph):
    def __init__(self, n_colours=2000):
        super(ConstrainedColorGraph, self).__init__(n_colours = n_colours)
        self.color_exams = defaultdict(list)

    def check_room_constraints_ILP(self, node, color, data, periods=None):
        """
            Check if rooms capacities constraint is fullfilled for the nodes that already have color as color
            Use ILP in order to get this feasibility
            @param node: node to color
            @param color: color for coloring node
            @param capacities: rooms capacities
        """
        period = 0
        if periods is not None and color < len(periods):
            period = periods[color]

        # get all nodes with that color, and solve ILP
        nodes = [nod for nod, col in self.colours.iteritems() if col == color] + [node]

        # schedule rooms
        # TODO: Give start solution ?!?
        return schedule_rooms_in_period(nodes, period, data) is not None

    def check_room_constraints_greedy(self, node, color, data, periods=None):
        """
            Check if rooms capacities constraint is fullfilled for the nodes that already have color as color
            Use ILP in order to get this feasibility
            @param node: node to color
            @param color: color for coloring node
            @param capacities: rooms capacities
        """
        if periods is not None and color < len(periods):
            period = periods[color]
        else:
            period = 0

        # get all nodes with that color, and solve ILP
        nodes = [nod for nod, col in self.colours.iteritems() if col == color] + [node]

        # schedule rooms
        # TODO: Give start solution ?!?
        return schedule_greedy(nodes, period, data) is not None

    def check_rooms_constraint(self, node, color, data):
        """
            Check if rooms capacities constraint is fullfilled for the nodes that already have color as color
            @param node: node to color
            @param color: color for coloring node
            @param capacities: rooms capacities
        """
        # get all nodes with that color
        #nodes = self.color_exams[color] + [node]
        nodes = [node for node, col in self.colours.iteritems() if col == color] + [node]
        
        c, s, r = data.get('c', []), data.get('s', []), data.get('r', 0)

        # sort students and capacities
        # TODO: Why? Please explain this!!
        students = sorted([(i, s[i]) for i in nodes], key=lambda x: x[1], reverse=True) if s else []
        capacities = sorted([c[k] for k in range(r)], reverse=True)

        #TODO: talk about whether this does what we want it to do
        i, k = 0, 0
        while i < len(nodes) and k < r:
            if students[i][1] <= capacities[k]:
                i += 1
            k += 1

        # Do we have exams without rooms
        return i < len(nodes)

    def color_node(self, node, data={}, check_constraints=True, periods=None, check_max_rooms_and_slots=False):
        """
            Check the colors of the neighbors, and color the node with a different color.
            If capacities is not empty, we color the node respecting the capacities room constraint
        """
        for col in self.ALL_COLOURS:
            # we check if every other neighbors don't have col as color
            if self.check_neighbours(node, col):

                # We check if the room constraint is fullfilled
                color_this_node = False
                if not check_constraints:
                    #print "dont check constraints"
                    color_this_node = True
                elif periods is not None and self.check_room_constraints_greedy(node, col, data, periods = periods):
                    color_this_node = True
                elif self.check_rooms_constraint(node, col, data):
                    color_this_node = True
                #elif check_constraints:
                    ## dont know why it works, but it works ^^°
                    #color_this_node = True
                    
                # if the node can be colored, do so and add it to color exams list
                if color_this_node:
                    self.colours[node] = col
                    self.color_exams[col].append(node)
                    break



class EqualizedColorGraph(ConstrainedColorGraph):
    def __init__(self, n_colours=2000):
        super(EqualizedColorGraph, self).__init__(n_colours=n_colours)
        self.color_exams = defaultdict(list)



    def color_node(self, node, data={}, check_constraints=True, periods=None, check_max_rooms_and_slots=False):
        """
            Check the colors of the neighbors, and color the node with a different color.
            If capacities is not empty, we color the node respecting the capacities room constraint
        """
        for col in self.ALL_COLOURS:
            # we check if every other neighbors don't have col as color
            if self.check_neighbours(node, col):
                self.colours[node] = col
                break
