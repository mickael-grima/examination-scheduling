#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging


def convert_to_table(variables, *dim):
    """ @param variables: dictionnary of variables
        @param dim: dimension of variables
        convert it to a string that represent a tabel
    """
    res = '     |  %s\n' % '  |  '.join([str(i) for i in range(dim[0])])
    res += '%s\n' % '|'.join(['-----' for i in range(dim[0] + 1)])
    if len(dim) > 1:
        for j in range(dim[1]):
            res += '  %s  |  %s\n' % (j, '  |  '.join([str(int(variables[i, j].X)) for i in range(dim[0])]))
            res += '%s\n' % '|'.join(['-----' for i in range(dim[0] + 1)])
    else:
        res += '  1  |  %s\n' % '  |  '.join([str(int(variables[i].X)) for i in range(dim[0])])
        res += '%s\n' % '|'.join(['-----' for i in range(dim[0] + 1)])
    return res


def get_dimensions_from(x, y):
    """ @param variables: variable from gurobi
        return the maximal number or each rank in the tuple key
    """
    n, r, p = set(), set(), set()
    for key, _ in x.iteritems():
        n.add(key[0])
        r.add(key[1])
    for key, _ in y.iteritems():
        n.add(key[0])
        p.add(key[1])
    return len(n), len(r), len(p)


def get_value(var):
        """ Return the value of var if possible, else 0
        """
        try:
            return var.X
        except Exception as e:
            logging.warning(str(e))
            return 0.0


def update_variable(problem):
    """ @param problem: either a problem inheriting from BaseProblem class or a guroby problem
        Transform the variable of the given problem to the two following variables:
                    x[i, k]: 1 if exam i is taking place in room k
                    y[i, l]: 1 if exam i happens during period l
        @returns: x, y
    """
    # problem from Base_problem class
    try:
        return problem.update_variable()
    except:
        logging.exception("update_variable: the given problem doesn't have a function update_prob")
    return ({}, {})


def get_constants_from(problem):
    """ @param problem: either a problem inheriting from BaseProblem class or a guroby problem
        Find the constants of the problem
        @returns: c, s, Q, T, h
    """
    try:
        return problem.constants['c'], problem.constants['s'], problem.constants['Q'], problem.constants['T'], problem.constants['h']
    except:
        logging.warning('get_constants_from: problem has no argument constants')
        return ({} for i in range(5))
