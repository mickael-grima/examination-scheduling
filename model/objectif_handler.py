#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Some functions to compute the objective with variables as input


def room_obj(x):
    ''' Room objective
    '''
    return sum(x.itervalues())


def time_obj(y, data):
    """ We return the objectif value concerning the time
    """
    n, p = data.get('n', 0), data.get('p', 0)
    h = data.get('h', [])
    d = {(i, j): sum(h[l] / 2 * abs(y.get((i, l), 0.0) - y.get((j, l), 0.0)) ** 2 for l in range(p))
         for i in range(n) for j in range(i + 1, n)}
    print y, d
    return sum(min(d[i, j] for j in range(i + 1, n)) for i in range(n))


def main_obj(x, y, data, gamma=1.0):
    return room_obj(x) - gamma * time_obj(y, data)
