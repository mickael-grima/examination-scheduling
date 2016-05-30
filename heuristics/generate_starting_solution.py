#!/usr/bin/env python
# -*- coding: utf-8 -*-

# We generate here a feasible solution for our problem. This solution just has to build feasible solutions
# x and y, here is no about how good the solution is

import logging
from copy import deepcopy


def generate_starting_solution(data):
    """ @param data: data concerning the problem
    """
    # First solve the colouring problem to solve the conflicts
    n = data.get('n', 0)
    r = data.get('r', 0)
    p = data.get('p', 0)
    Q = data.get('Q', [])
    T = data.get('T', [])
    s = data.get('s', [])
    c = deepcopy(data.get('c', []))
    x = {(i, k, l): 0.0 for i in range(n) for k in range(r) for l in range(p)}
    y = {(i, l): 0.0 for i in range(n) for l in range(p)}

    seats = sorted([(i, s[i]) for i in range(n)], key=lambda z: z[1], reverse=True)
    capacity_constr = lambda seat, l: seat <= sum([T[k][l] for k in range(r)])
    conflict_constr = lambda i, l: sum([y[i, l] * y[j, l] * Q[i][j] for j in range(i)]) == 0

    for i, seat in seats:
        l = 0
        while l < p and not capacity_constr(seat, l) and not conflict_constr(i, l):
            l += 1
        if l >= p:
            logging.warning('No feasible solutions found by generate_starting_solution')
            return {}, {}
        y[i, l] = 1.0
        rooms = sorted([(k, c[k]) for k in range(r)], key=lambda z: z[1], reverse=True)
        ind, current_ca = 0, 0
        while ind < r and current_ca < seat:
            k, capacity = rooms[ind]
            if T[k][l] == 1:
                x[i, k, l] = 1.0
                c[k] = max(c[k] - seat, 0)
                current_ca += c[k]
            ind += 1

    return x, y
