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

from ColorGraph import ColorGraph
from model.groups_repartition_problem import GroupsRepartitionProblem
import sys


def build_groups_data(groups, data):
    """ build data updated to GroupsRepartitionProblem
    """
    groups_data = {'c': len(groups), 'p': data['p']}
    groups_data['h'] = data['h']  # Starting time of each time slot
    groups_data['v'] = {}  # value corresponding at the number of student for each group
    groups_data['conflicts'] = {}  # sum of the conflicts between two groups for each couple of groups
    for index, group in groups.iteritems():
        groups_data['v'].setdefault(index, {})
        groups_data['v'][index] = sum(data['s'][i] for i in group)
        for ind, gr in groups.iteritems():
            groups_data['conflicts'][index, ind] = sum(data['Q'][i][j] for i in group for j in gr)
    return groups_data


def attribute_time_and_room(groups_exams, data):
    # Data and variables
    n, r, p = data.get('n', 0), data.get('r', 0), data.get('p', 0)
    T, s, c = data['T'], data['s'], data['c']
    x = {(i, k, l): 0.0 for i in range(n) for k in range(r) for l in range(p)}
    y = {(i, l): 0.0 for i in range(n) for l in range(p)}

    # we attribuate the rooms to the groups function of the time slots we found
    for ind, dct in groups_exams.iteritems():
        rooms_ind = filter(lambda x: T[x][dct['times'][0]] > 0, range(r))
        rooms = sorted([(kk, c[kk]) for kk in rooms_ind], key=lambda x: x[1], reverse=True)
        i, k, seats = 0, 0, [seat for seat in s]
        while i < len(dct['exams']) and k < len(rooms):
            # sort roomsand exams, get times
            exams, times = sorted(dct['exams'], key=lambda ex: s[ex], reverse=True), dct['times']

            # We attribuate the rooms to the exams
            seats[exams[i]] = max(seats[exams[i]] - rooms[k][1], 0)
            x[exams[i], rooms[k][0], times[0]] = 1.0
            y[exams[i], times[0]] = 1.0
            if seats[exams[i]] <= rooms[k][1]:
                i += 1
            k += 1
    return x, y


def optimize(data, gamma=1.0):
    """ Generate first groups of exams that can be scheduled in parallel, and then fill
        the rooms in order that a minimal among of place is not used for each time slot
    """
    n = data.get('n', 0)

    # We first solve the coloring problem
    # TODO: try to randomize, maybe ILP
    prob = ColorGraph()
    prob.build_graph(n, data['conflicts'])
    prob.color_graph()
    groups, index, i = {}, {}, 0  # group of parallel exams
    for exam, colour in prob.colours.iteritems():
        if colour not in index:
            index.setdefault(colour, i)
            i += 1
        groups.setdefault(index[colour], [])
        groups[index[colour]].append(exam)

    # optimize the repartition of groups over the time slots
    groups_data = build_groups_data(groups, data)
    prob = GroupsRepartitionProblem(gamma=gamma)
    prob.build_problem(groups_data)
    prob.optimize()
    G = {key: var.X for key, var in prob.vars['x'].iteritems()}

    # attribute rooms and time slots
    groups_exams = {}
    for key, value in G.iteritems():
        groups_exams.setdefault(key[0], {'exams': groups[key[0]], 'times': []})
        if value > 0:
            groups_exams[key[0]]['times'].append(key[1])
    x, y = attribute_time_and_room(groups_exams, data)

    return x, y
