#!/usr/bin/env python
# -*- coding: utf-8 -*-


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


def get_dimensions_from(variables):
    """ @param variables: variable from gurobi
        return the maximal number or each rank in the tuple key
    """
    maxs = {}
    for key, _ in variables.iteritems():
        for i in range(len(key)):
            maxs.setdefault(i, key[i])
            maxs[i] = max(key[i], maxs[i])
    return [value for _, value in maxs.iteritems()]
