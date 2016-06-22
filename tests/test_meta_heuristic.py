#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
paths = os.getcwd().split('/')
path = ''
for p in paths:
    path += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(path)

import unittest

import random as rd
from heuristics.generate_starting_solution import generate_starting_solution_by_maximal_time_slot_filling
from heuristics.AC import AC
import heuristics.examination_scheduler as scheduler
from heuristics import tools
from model.instance import build_smart_random, build_small_input, build_random_data
import heuristics.schedule_times as schedule_times
from heuristics.ColorGraph import ColorGraph

from heuristics.examination_scheduler import *
from heuristics.MetaHeuristic import *


from utils.tools import transform_variables
from model.constraints_handler import (
    test_conflicts,
    test_enough_seat,
    test_one_exam_per_period,
    test_one_exam_period_room
)


if __name__ == '__main__':
    
    n = 15
    r = 5 
    p = 15
    prob = 0.6
    seed = 42
    
    rd.seed(seed)
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=prob, build_Q = False)
    
    for H, name in zip([RandomHeuristic, RandomHeuristicAdvanced, AC], ["Random", "RandomAdvanced", "AC"]):
        T = H(data, 400)
        colorings = T.generate_colorings()
        for color in colorings:
            values = color.values()
            m = max(values)
            assert all( [t >= 0 for t in values] ), "Error: Some nodes are left white!!! Nodes need all be colored!!"
            assert all( [t <= m for t in values] ), "Error: Color values need to be in range"
        print "OK:", name
        
        