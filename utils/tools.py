#!/usr/bin/env python
# -*- coding: utf-8 -*-


def convert_to_table(var, *dim):
    """ @param var: dictionnary of variables
        @param dim: dimension of var
        convert it to a string that represent a tabel
    """
    res = '     |  %s\n' % '  |  '.join([str(i) for i in range(dim[0])])
    res += '%s\n' % '|'.join(['-----' for i in range(dim[0] + 1)])
    if len(dim) > 1:
        for j in range(dim[1]):
            res += '  %s  | %s\n' % (j, ' | '.join([str(var[i, j].Obj) for i in range(dim[0])]))
            res += '%s\n' % '|'.join(['-----' for i in range(dim[0] + 1)])
    else:
        res += '  1  | %s\n' % ' | '.join([str(var[i].Obj) for i in range(dim[0])])
        res += '%s\n' % '|'.join(['-----' for i in range(dim[0] + 1)])
    return res
