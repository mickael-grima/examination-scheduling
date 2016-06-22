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


import numpy as np
import random as rd
import collections
from time import time
import timeit

from model.instance import force_data_format, build_random_data
import GurobiModel.GurobiLinear_v_8_removed_obj as gurobi
from gurobipy import Model, quicksum, GRB, GurobiError, LinExpr

from heuristics.AC import AC
from heuristics.schedule_times import schedule_times
from heuristics.schedule_rooms import schedule_rooms
from heuristics.tools import to_binary, get_coloring, swap_color_dictionary
from heuristics.schedule_rooms import schedule_rooms_in_period, schedule_greedy


# We write functions concerning the constraints

from utils import tools

# time constraints

def test_one_exam_per_period(y, n = None, p = None, **indices):
    """ 
        Test here the constraint: one exam per period
    """
    if y is None: return False
    
    if n is None or p is None:
        n, p = tools.get_dimensions_from_y(y)
        
    res = True
    if indices.get('i') is not None:
        i = indices.get('i')
        res = sum([y[i, l] for l in range(p)]) == 1
    else:
        for i in range(n):
            res = res and (sum([y[i, l] for l in range(p)]) == 1)
    return res


def test_conflicts(y, n = None, p = None, conflicts={}, **indices):
    """ 
        Test here the constraint: no student has to write two exams or more at the same time
    """
    
    if y is None: return False
    
    if n is None or p is None:
        n, p = tools.get_dimensions_from_y(y)
    
    res = True
    if indices.get('l') is not None:
        l = indices.get('l')
        if indices.get('i') is not None:
            i = indices.get('i')
            res = sum([y[i, l] * y[j, l] for j in conflicts[i]]) == 0
        else:
            for i in range(n):
                res = res and sum([y[i, l] * y[j, l] for j in conflicts[i]]) == 0
    else:
        if indices.get('i') is not None:
            i = indices.get('i')
            for l in range(p):
                res = res and sum([y[i, l] * y[j, l] for j in conflicts[i]]) == 0
        else:
            for i in range(n):
                for l in range(p):
                    res = res and sum([y[i, l] * y[j, l] for j in conflicts[i]]) == 0
    return res


# room constraints

def test_enough_seat(x, n = None, r = None, c=[], s=[], **indices):
    """         
        Test here the constraint: enough seats for each exam
    """
    
    if x is None: return False
    
    if n is None or r is None:
        n, r = tools.get_dimensions_from_x(x)
        
    res = True
    if indices.get('i') is not None:
        i = indices.get('i')
        res = sum([x[i, k] * c[k] for k in range(r)]) >= s[i]
    else:
        for i in range(n):
            res = res and sum([x[i, k] * c[k] for k in range(r)]) >= s[i]
    return res

#combined constraints

def test_one_exam_period_room(x, y, T=[], n = None, r = None, p = None, **indices):
    """ 
        Test here the constraint: For each room and period we have only one exam
    """
    
    if x is None or y is None: return False
    
    if n is None or r is None or p is None:
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



def time_feasible(y, data):
    """ 
        For each time constraint return if it is feasible or not
    """
    return {
        'one exam per period': test_one_exam_per_period(y, n = data['n'], p = data['p']),
        'conflicts': test_conflicts(y, conflicts=data['conflicts'], n = data['n'], p = data['p']),
    }

def room_feasible(x, data):
    """ 
        For each room constraint return if it is feasible or not
    """
    return {
        'enough seat': test_enough_seat(x, c=data['c'], s=data['s'], n = data['n'], r = data['r'])
    }


def is_feasible(x, y, data):
    """ 
        For each type of constraint return if it is feasible or not
    """
    feasibility = time_feasible(y, data)
    feasibility.update(room_feasible(x, data))
    feasibility['one exam per period per room'] = test_one_exam_period_room(x, y, T=data['T'], n = data['n'], r = data['r'], p = data['p'])
    return feasibility





def check_feasability_ILP(exams_to_schedule, period, data, verbose = False):
    
    #More precise but by far to slow compared to heuristic
    r = data['r']
    c = data['c']
    T = data['T']
    s = data['s']
    z = {}


    model = Model("RoomFeasability")

    # z[i,k] = if exam i is written in room k
    for k in range(r):
        #print k, period
        if T[k][period] == 1:
            for i in exams_to_schedule:
                z[i,k] = model.addVar(vtype=GRB.BINARY, name="z_%s_%s" % (i,k))

    model.update()

    # Building constraints...    


    # c1: seats for all students   
    for i in exams_to_schedule:
        expr = LinExpr()
        for k in range(r):
            if T[k][period] == 1:
                expr.addTerms(1, z[i,k])
        model.addConstr( expr >= s[i], "c1")


    # c2: only one exam per room   
    for k in range(r):
        if T[k][period] == 1:
            expr = LinExpr()
            for i in exams_to_schedule:
                expr.addTerms(1 , z[i,k])
            model.addConstr( expr <= 1, "c2")    

    model.setObjective(0, GRB.MINIMIZE)
    
    if not verbose:
        model.params.OutputFlag = 0

    model.params.heuristics = 0
    model.params.PrePasses = 1


    model.optimize()

    # return best room schedule
    try:         
        return model.objval
    except GurobiError:
        return None

