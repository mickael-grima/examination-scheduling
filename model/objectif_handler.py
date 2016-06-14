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
    h, conflicts = data.get('h', []), data.get('conflicts', {})
    H = [sum(h[l] * y[i, l] for l in range(p)) for i in range(n)]
    m = filter(bool, [[abs(H[i] - H[j]) for j in range(i + 1, n) if j in conflicts[i]] for i in range(n - 1)])
    return sum([min(mm) for mm in m])


def main_obj(x, y, data, gamma=1.0):
    return room_obj(x) - gamma * time_obj(y, data)
