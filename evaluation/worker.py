#!/usr/bin/env python
# -*- coding: utf-8 -*-



from __future__ import division

import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)

from time import time
import datetime
import random 
from collections import defaultdict
import pickle

from GurobiModel.GurobiLinear_v_1 import build_model as build_linear_model_1
from GurobiModel.GurobiLinear_v_2_Q import build_model as build_linear_model_2
from GurobiModel.GurobiLinear_v_3 import build_model as build_linear_model_3
from GurobiModel.GurobiLinear_v_4_Cliques import build_model as build_linear_model_4
from GurobiModel.GurobiLinear_v_5_changed_obj import build_model as build_linear_model_5
from GurobiModel.GurobiLinear_v_6_removed_c6 import build_model as build_linear_model_6
from GurobiModel.GurobiLinear_v_8_removed_obj import build_model as build_linear_model_8
from GurobiModel.GurobiLinear_v_10_location import build_model as build_linear_model_10
from GurobiModel.GurobiLinear_v_11_model_speed import build_model as build_linear_model_11
from GurobiModel.GurobiLinear_v_12_smaller_M import build_model as build_linear_model_12
from GurobiModel.GurobiLinear_v_13_cover_inequalities import build_model as build_linear_model_13

from GurobiModel.GurobiLinear_v_14_cuts1 import build_model as build_linear_model_14c1
from GurobiModel.GurobiLinear_v_14_cuts2 import build_model as build_linear_model_14c2
from GurobiModel.GurobiLinear_v_14_cuts3 import build_model as build_linear_model_14c3
from GurobiModel.GurobiLinear_v_14_cuts4 import build_model as build_linear_model_14c4
from GurobiModel.GurobiLinear_v_14_cuts5 import build_model as build_linear_model_14c5
from GurobiModel.GurobiLinear_v_14_cuts6 import build_model as build_linear_model_14c6
from GurobiModel.GurobiLinear_v_14_cuts7 import build_model as build_linear_model_14c7
from GurobiModel.GurobiLinear_v_14_cuts8 import build_model as build_linear_model_14c8
from GurobiModel.GurobiLinear_v_14_cuts9 import build_model as build_linear_model_14c9
from GurobiModel.GurobiLinear_v_14_cuts10 import build_model as build_linear_model_14c10
from GurobiModel.GurobiLinear_v_14_cuts11 import build_model as build_linear_model_14c11
from GurobiModel.GurobiLinear_v_14_cuts12 import build_model as build_linear_model_14c12

from GurobiModel.GurobiLinear_v_15_more_covers import build_model as build_linear_model_15
from GurobiModel.GurobiLinear_v_16_symmetry import build_model as build_linear_model_16
from GurobiModel.GurobiLinear_v_17_pertubate import build_model as build_linear_model_17
from GurobiModel.GurobiLinear_v_18_lexicographic import build_model as build_linear_model_18
from GurobiModel.GurobiLinear_v_19_Branch_Priority import build_model as build_linear_model_19
from GurobiModel.GurobiLinear_v_20_orbital import build_model as build_linear_model_20
from GurobiModel.GurobiLinear_v_21_l2 import build_model as build_linear_model_21
from GurobiModel.GurobiLinear_v_22_l3 import build_model as build_linear_model_22


from GurobiModel.GurobiLinear_v_23_data import build_model as build_linear_model_23




from evaluation.objectives import *

from model.instance import build_smart_random
from model.instance import build_real_data
from model.instance import build_real_data_sample
from model.instance import detect_similarities

from inputData.examination_data import read_data




from time import time
import datetime
import random 
from collections import defaultdict
import pickle

from evaluation.objectives import *
from evaluation import tools as eval_tools

def compare(data, timeL=0):
    """ we compare for some problems how many time we need to solve each problem
    """
    # Select models to compare
    problems = {
    #    'Data Evaluate' : build_linear_model_23,
         'Data L3' : build_linear_model_22,
         'Data L2' : build_linear_model_21,
    #    'Linear orbital': build_linear_model_20,
    #    'Linear Lexicographic': build_linear_model_18,
    #    'Linear Pertubate': build_linear_model_17,
    #    'Linear symmetrie': build_linear_model_16,
         'Linear more covers': build_linear_model_15,
    #    'Linear Cover inequalities': build_linear_model_13,
    #    'Linear smaller M': build_linear_model_12,
    #    'Linear model speed': build_linear_model_11,
    #    'Linear Location': build_linear_model_10,
    #   'Linear Advanced removed obj': build_linear_model_8,
    #   'Linear Advanced removed c6': build_linear_model_6,
    #   'Linear Advanced changed obj': build_linear_model_5,
    #   'Linear Advanced': build_linear_model_3,
    #   'Linear Advanced Cliques': build_linear_model_4,    
    #   'GurobiQ_neu': build_nonlinear_model
    }

    times = dict()

    objectives = dict()

    nodeCount = dict()

    for prob_name in problems:
        print(prob_name)
        # Build selected model
        random.seed(42)

        problem = problems[prob_name](data)
        #problem.params.OutputFlag = 0
        #problem.params.cuts = 0
        problem.params.heuristics = 0
        # Optimize selected model
        t = time()
        #problem.params.cuts = 0
        if timeL != 0:
            problem.params.TimeLimit = timeL
        problem.optimize()
        # try:
        #     problem.computeIIS()
        # except:
        #     pass
        # problem.write("model.lp")
        times[prob_name] = time() - t

        count_rooms = 0


        today = datetime.datetime.today()
        filename = "%sresults\Result_%s_%s_%s_%s_%s_%s.txt" % (PROJECT_PATH, today.year, today.month, today.day, today.hour, today.minute, prob_name )

        try:
            x_ikl = defaultdict(int)
            y_il = defaultdict(int)
            
            for i in range(data['n']):
                for l in range(data['p']):
                    v = problem.getVarByName('y_%s_%s' % (i,l))
                    if not v is None and v.x == 1:
                        y_il[i,l] = 1
                        
                    for k in range(data['r']):
                        v = problem.getVarByName('x_%s_%s_%s' % (i,k,l))
                        if not v is None and v.x == 1:
                            x_ikl[i,k,l] = 1
                            count_rooms += 1
            
            eval_tools.write_result(x_ikl, y_il, data)
        except:
            print "Couldnt write data"

        # Save objective value
        try:
            objectives[prob_name] = problem.objVal
        except:

            objectives[prob_name] = 0

        nodeCount[prob_name] = problem.NodeCount

    return times, objectives, nodeCount


from inputData import examination_data


def test_compare(n,r,p,tseed,timeL):


    #data = build_smart_random(n=n,r=r,p=p,tseed=tseed)
    #data = build_real_data(tseed=tseed)
    data = detect_similarities(build_real_data_sample(n=n,r=r,p=p,tseed=tseed))
    #data = examination_data.read_data(semester = "15W", threshold = 0)
    #data['similar_periods'] = tools.get_similar_periods(data)
    #data = examination_data.load_data(dataset = "3", threshold = 0, verbose = True)
    
    time, objectives, nodeCount = compare(data,timeL)

    print("")
    print("n: %s" % (data['n']))
    print("r: %s" % (r))
    print("p: %s" % (p))
    print("seed: %s" % (tseed))
    print("Percentage conflicts: %s" % (sum( len(data['conflicts'][i]) for i in range(n)) /(2*n*(n-1))))
    print("")
    for key in time:
        print key
        print("time:")
        print(time[key])
        print("value:")
        print(objectives[key])
        print("nodeCount:")
        print(nodeCount[key])
        print("")


if __name__ == '__main__':
    n = 400
    r = 60
    p = 40
    tseed = 83
    timeL = [8000]
    for t in timeL:
        print t
        test_compare(n,r,p,tseed,t)
