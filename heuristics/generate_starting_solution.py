#!/usr/bin/env python
# -*- coding: utf-8 -*-

# We generate here a feasible solution for our problem. This solution just has to build feasible solutions
# x and y, here is no about how good the solution is

import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)

from ColorGraph import ColorGraph
from model.objectif_handler import time_obj
import sys


def find_best_time_slots(exs, data, black_times=[]):
    """ @param exs: list of exams
        find the time slots that are the most adapted to the exams
        a time slot is adapted to a group if the number of free seats is minimized
        We try first to use only one time slot. If it is not possible we try two and so on
    """
    T, c, s, p, r = data['T'], data['c'], data['s'], data['p'], data['r']
    value, time = sys.maxint, -1
    exs = sorted(exs, key=lambda ex: s[ex], reverse=True)
    for l in [ll for ll in range(p) if ll not in black_times]:
        rooms_ind = filter(lambda x: T[x][l] > 0, range(r))
        rooms = sorted([c[k] for k in rooms_ind], reverse=True)
        i, k, v = 0, 0, 0
        seats = [seat for seat in s]
        while i < len(exs) and k < len(rooms):
            v = max(rooms[k] - seats[exs[i]], 0)
            seats[exs[i]] = max(seats[exs[i]] - rooms[k], 0)
            if seats[exs[i]] <= rooms[k]:
                i += 1
            k += 1
        if i == len(exs) and v < value:
            value = v
            time = l
    return time, value


def sort_and_split(groups, data):
    """ @param groups: dictinnary of colour, exams. exams have no conflict each other
        for each group of parallel exams, we try to find the most adapted time slot for scheduling
        if several time slots are needed, we split the group into several groups, one for each time slot
        a time slot is adapted to a group if the number of free seats is minimized
    """
    groups_exams = []
    while groups:
        time_slots, value, colour = None, sys.maxint, None
        for col, exs in groups.iteritems():
            t, v = find_best_time_slots(exs, data, black_times=[time for time, _ in groups_exams])
            if v <= value:
                value, time_slots, colour = v, (t, exs), col
        groups_exams.append(time_slots)
        del groups[colour]
    return groups_exams


def attribute_time_and_room(groups_exams, data):
    n, r, p = data.get('n', 0), data.get('r', 0), data.get('p', 0)
    T, s, c = data['T'], data['s'], data['c']
    x = {(i, k, l): 0.0 for i in range(n) for k in range(r) for l in range(p)}
    y = {(i, l): 0.0 for i in range(n) for l in range(p)}
    for time, exams in groups_exams:
        rooms_ind = filter(lambda x: T[x][time] > 0, range(r))
        i, k, seats = 0, 0, [seat for seat in s]
        while i < len(exams) and k < len(rooms_ind):
            exams = sorted(exams, key=lambda ex: seats[ex], reverse=True)
            rooms = sorted([(kk, c[kk]) for kk in rooms_ind], key=lambda x: x[1], reverse=True)
            exam = exams[i]
            seats[exam] = max(seats[exam] - rooms[k][1], 0)
            x[exam, rooms[k][0], time], y[exam, time] = 1.0, 1.0
            if seats[exam] <= rooms[k][1]:
                i += 1
            k += 1
    return x, y


def generate_starting_solution_by_maximal_time_slot_filling(data):
    """ Generate first groups of exams that can be scheduled in parallel, and then fill
        the rooms in order that a minimal among of place is not used for each time slot
    """
    n = data.get('n', 0)

    # We first solve the coloring problem
    prob = ColorGraph()
    prob.build_graph(n, data['conflicts'])
    prob.color_graph()
    groups = {}  # group of parallel exams
    for exam, colour in prob.colours.iteritems():
        groups.setdefault(colour, [])
        groups[colour].append(exam)

    # give an order to the groups
    groups_exams = sort_and_split(groups, data)

    # attribute rooms and time slots
    x, y = attribute_time_and_room(groups_exams, data)

    return x, y
