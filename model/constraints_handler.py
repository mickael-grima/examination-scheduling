#!/usr/bin/env python
# -*- coding: utf-8 -*-

# We write functions concerning the constraints

from utils import tools
import itertools


def test_one_exam_per_period(prob, **indices):
    """ Test here the constraint: one exam per period
    """
    prob.optimize()
    x, y = tools.update_variable(prob)
    n, _, p = tools.get_dimensions_from(x, y)
    res = True
    if indices.get('i') is not None:
        i = indices.get('i')
        res = sum([y[i, l] for l in range(p)]) == 1
    else:
        for i in range(n):
            res = res and (sum([y[i, l] for l in range(p)]) == 1)
    return res


def test_enough_seat(prob, **indices):
    """ Test here the constraint: enough seats for each exam
    """
    prob.optimize()
    x, y = tools.update_variable(prob)
    n, r, _ = tools.get_dimensions_from(x, y)
    c, s, _, _, _ = tools.get_constants_from(prob)
    res = True
    if indices.get('i') is not None:
        i = indices.get('i')
        res = sum([x[i, k] * c[k] for k in range(r)]) >= s[i]
    else:
        for i in range(n):
            res = res and sum([x[i, k] * c[k] for k in range(r)]) >= s[i]
    return res


def test_one_exam_period_room(prob, **indices):
    """ Test here the constraint: For each room and period we have only one exam
    """
    prob.optimize()
    x, y = tools.update_variable(prob)
    n, r, p = tools.get_dimensions_from(x, y)
    _, _, _, T, _ = prob.get_constants()
    res = True
    if indices.get('k') is not None:
        k = indices.get('k')
        if indices.get('l') is not None:
            l = indices.get('l')
            res = sum([x[i, k] * y[i, l] for i in range(n)]) <= T[k][l]
        else:
            for l in range(p):
                res = res and sum([x[i, k] * y[i, l] for i in range(n)]) <= T[k][l]
    else:
        for k in range(r):
            if indices.get('l') is not None:
                l = indices.get('l')
                res = res and sum([x[i, k] * y[i, l] for i in range(n)]) <= T[k][l]
            else:
                for l in range(p):
                    res = res and sum([x[i, k] * y[i, l] for i in range(n)]) <= T[k][l]
    return res


def test_conflicts(prob, **indices):
    """ Test here the constraint: no student has to write two exams or more at the same time
    """
    prob.optimize()
    x, y = tools.update_variable(prob)
    n, r, p = tools.get_dimensions_from(x, y)
    _, _, Q, _, _ = tools.get_constants_from(prob)
    res = True
    if indices.get('l') is not None:
        l = indices.get('l')
        res = sum([y[i, l] * y[j, l] * Q[i][j] for i, j in itertools.combinations(range(n), 2) if Q[i][j] == 1]) == 0
    else:
        for l in range(p):
            res = res and sum([y[i, l] * y[j, l] * Q[i][j] for i, j in itertools.combinations(range(n), 2) if Q[i][j] == 1]) == 0
    return res
