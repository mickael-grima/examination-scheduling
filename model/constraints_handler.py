#!/usr/bin/env python
# -*- coding: utf-8 -*-

# We write functions concerning the constraints

from utils import tools


def test_one_exam_per_period(x, y, **indices):
    """ Test here the constraint: one exam per period
    """
    n, _, p = tools.get_dimensions_from(x, y)
    res = True
    if indices.get('i') is not None:
        i = indices.get('i')
        res = sum([y[i, l] for l in range(p)]) == 1
    else:
        for i in range(n):
            res = res and (sum([y[i, l] for l in range(p)]) == 1)
    return res


def test_enough_seat(x, y, c=[], s=[], **indices):
    """ Test here the constraint: enough seats for each exam
    """
    n, r, _ = tools.get_dimensions_from(x, y)
    res = True
    if indices.get('i') is not None:
        i = indices.get('i')
        res = sum([x[i, k] * c[k] for k in range(r)]) >= s[i]
    else:
        for i in range(n):
            res = res and sum([x[i, k] * c[k] for k in range(r)]) >= s[i]
    return res


def test_one_exam_period_room(x, y, T=[], **indices):
    """ Test here the constraint: For each room and period we have only one exam
    """
    n, r, p = tools.get_dimensions_from(x, y)
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


def test_conflicts(x, y, Q=[], **indices):
    """ Test here the constraint: no student has to write two exams or more at the same time
    """
    n, r, p = tools.get_dimensions_from(x, y)
    res = True
    if indices.get('l') is not None:
        l = indices.get('l')
        if indices.get('i') is not None:
            i = indices.get('i')
            res = sum([y[i, l] * y[j, l] * Q[i][j] for j in range(n) if Q[i][j] == 1 and i != j]) == 0
        else:
            for i in range(n):
                res = res and sum([y[i, l] * y[j, l] * Q[i][j]for j in range(n) if Q[i][j] == 1 and i != j]) == 0
    else:
        for l in range(p):
            if indices.get('i') is not None:
                i = indices.get('i')
                res = res and sum([y[i, l] * y[j, l] * Q[i][j] for j in range(n) if Q[i][j] == 1 and i != j]) == 0
            else:
                for i in range(n):
                    res = res and sum([y[i, l] * y[j, l] for j in range(n) if Q[i][j] == 1 and i != j]) == 0
    return res
