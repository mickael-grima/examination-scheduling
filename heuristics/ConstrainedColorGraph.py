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
from heuristics.schedule_rooms import schedule_rooms_in_period


class ConstrainedColorGraph(ColorGraph):
    def __init__(self):
        super(ConstrainedColorGraph, self).__init__()

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
        nodes = [node for node, col in self.colours.iteritems() if col == color] + [node]

        # schedule rooms
        # TODO: Give start solution ?!?
        return schedule_rooms_in_period(nodes, period, data) is not None

    def check_rooms_constraint(self, node, color, data):
        """
            Check if rooms capacities constraint is fullfilled for the nodes that already have color as color
            @param node: node to color
            @param color: color for coloring node
            @param capacities: rooms capacities
        """
        # get all nodes with that color
        nodes = [nod for nod, col in self.colours.iteritems() if col != color] + [node]

        c, s, r = data.get('c', []), data.get('s', []), data.get('r', 0)

        # sort students and capacities
        # TODO: Why? Please explain this!!
        students = sorted([(i, s[i]) for i in nodes], key=lambda x: x[1], reverse=True) if s else []
        capacities = sorted([c[k] for k in range(r)], reverse=True)

        i, k = 0, 0
        while i < len(nodes) and k < r:
            if students[i][1] <= capacities[k]:
                i += 1
            k += 1

        # TODO: Why does i < len(nodes) tell us that the room constrint is fulfilled? Please explain!!
        return i < len(nodes)

    def color_node(self, node, data={}, check_constraints=True, periods=None):
        """
            Check the colors of the neighbors, and color the node with a different color.
            If capacities is not empty, we color the node respecting the capacities room constraint
        """
        for col in self.ALL_COLOURS:
            # we check if every other neighbors don't have col as color
            if self.check_neighbours(node, col):
                # We check if the room constraint is fullfilled
                if not check_constraints:
                    self.colours[node] = col
                    break
                elif periods is not None and self.check_room_constraints_ILP(node, col, data, periods=periods):
                    self.colours[node] = col
                    break
                elif self.check_rooms_constraint(node, col, data):
                    self.colours[node] = col
                    break
