#!/usr/bin/env python
# -*- coding: utf-8 -*-

# We generate here a feasible solution for our problem. This solution just has to build feasible solutions
# x and y, here is no about how good the solution is

from model.constraints_handler import test_conflicts, test_enough_seat
from booth.colouring import ColorGraph
from random import randint
import sys


def get_random_exam(seats, black_list=[]):
    """ take a exam randomly in seats but not in black_list
        @return: index in seats
    """
    ind = randint(0, sum([seats[i][1] for i in range(len(seats)) if i not in black_list]))
    n = 0
    for i in range(len(seats)):
        exam, seat = seats[i]
        if i not in black_list:
            n += seat
            if ind <= n:
                return i


def permut_exam(seats):
    """ @param seats: list of tuple (exam, number of seat required for exam)
        permut randomly two exams. The most places has an exam, biger is the chance two permut it
    """
    ind1 = get_random_exam(seats)
    ind2 = get_random_exam(seats, black_list=[ind1])
    tpl = (seats[ind1][0], seats[ind1][1])
    seats[ind1] = seats[ind2]
    seats[ind2] = tpl
    return seats


def generate_starting_solution_from_given_order(x, y, ordered_exams, data):
    """ Generate a solution for a given order of indices
    """
    n, r, p = data.get('n', 0), data.get('r', 0), data.get('p', 0)
    Q, T, c, s = data.get('Q', []), data.get('T', []), data.get('c', []), data.get('s', [])
    C = {(k, l): c[k] for k in range(r) for l in range(p)}
    for i in ordered_exams:
        l = 0
        y[i, l] = 1.0
        # First find a time where the exam could be schedule
        xx = {(i, k): sum([x[i, k, l] for l in range(p)]) for i in range(n) for k in range(r)}
        while l < p and (not test_enough_seat(xx, y, c=c, s=s) or not test_conflicts(x, y, Q=Q)):
            l += 1
            y[i, l] = 0.0
        if l >= p:
            # logging.warning('No feasible solutions found by generate_starting_solution')
            return {}, {}
        rooms = sorted([(k, C[k, l]) for k in range(r)], key=lambda z: z[1], reverse=True)
        ind, current_ca = 0, 0
        while ind < r and current_ca < s[i]:
            k, capacity = rooms[ind]
            if T[k][l] == 1:
                x[i, k, l] = 1.0
                C[k, l] = 0
                current_ca += C[k, l]
            ind += 1

    return x, y


def generate_starting_solution(data, Niter=10):
    """ @param data: data concerning the problem
    """
    # First solve the colouring problem to solve the conflicts
    n, r, p = data.get('n', 0), data.get('r', 0), data.get('p', 0)
    s = data.get('s', [])
    x = {(i, k, l): 0.0 for i in range(n) for k in range(r) for l in range(p)}
    y = {(i, l): 0.0 for i in range(n) for l in range(p)}

    seats = sorted([(i, s[i]) for i in range(n)], key=lambda z: z[1], reverse=True)

    N = 0
    while Niter < 0 or N < Niter:
        x_, y_ = generate_starting_solution_from_given_order(x, y, [ind for ind, _ in seats], data)
        if not x_ or not y_:
            seats = permut_exam(seats)
            N += 1
        else:
            break

    return x_, y_


# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------
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
            v += max(rooms[k] - s[exs[i]], 0)
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
        exams = sorted(exams, key=lambda ex: s[ex], reverse=True)
        rooms_ind = filter(lambda x: T[x][time] > 0, range(r))
        rooms = sorted([(k, c[k]) for k in rooms_ind], key=lambda x: x[1], reverse=True)
        i, k, seats = 0, 0, [seat for seat in s]
        while i < len(exams) and k < len(rooms):
            seats[exams[i]] = max(seats[exams[i]] - rooms[k][1], 0)
            x[exams[i], rooms[k][0], time] = 1.0
            y[exams[i], time] = 1.0
            if seats[exams[i]] <= rooms[k][1]:
                i += 1
            k += 1
    return x, y


def generate_starting_solution_by_maximal_time_slot_filling(data):
    """ Generate first groups of exams that can be scheduled in parallel, and then fill
        the rooms in order that a minimal among of place is not used for each time slot
    """
    n = data.get('n', 0)
    Q = data['Q']

    # We first solve the coloring problem
    prob = ColorGraph()
    prob.build_graph(n, Q)
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
