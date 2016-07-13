import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)

import itertools
import random
import networkx as nx
import math 
from time import time
import timeit
    
from gurobipy import Model, quicksum, GRB, GurobiError
from model.instance import build_random_data
      
    
def build_model(data, n_cliques = 0, verbose = True):
    
    # Load Data Format
    n = data['n']
    r = data['r']
    p = data['p']
    s = data['s']
    c = data['c']
    h = data['h']
    w = data['w']
    location = data['location']
    conflicts = data['conflicts']
    locking_times = data['locking_times']
    T = data['T']
    
    model = Model("ExaminationScheduling")
    
    
    if verbose:
        print("Building variables...")
    
    # x[i,k,l] = 1 if exam i is at time l in room k
    x = {}
    for k in range(r):
        for l in range(p):
            if T[k][l] == 1:
                for i in range(n):
                    if location[k] in w[i]:
                        x[i,k,l] = model.addVar(vtype=GRB.BINARY, name="x_%s_%s_%s" % (i,k,l))
    
    # y[i,l] = 1 if exam i is at time l
    y = {}
    for i in range(n):
        for l in range(p):
            y[i, l] = model.addVar(vtype=GRB.BINARY, name="y_%s_%s" % (i,l))
    

    # integrate new variables
    model.update() 

    start = timeit.default_timer()
    # adding constraints as found in MidTerm.pdf
    if verbose:
        print("Building constraints...")    
    
    if verbose:
        print("c1: connecting variables x and y")
    for i in range(n):
        for l in range(p):
            model.addConstr( quicksum([ x[i, k, l] for k in range(r) if T[k][l] == 1 and location[k] in w[i] ]) <= 12 * y[i, l], "c1a")
            model.addConstr( quicksum([ x[i, k, l] for k in range(r) if T[k][l] == 1 and location[k] in w[i] ]) >= y[i, l], "c1b")
            
    if verbose:
        print("c2: each exam at exactly one time")
    for i in range(n):
        model.addConstr( quicksum([ y[i, l] for l in range(p) ]) == 1 , "c2")

    """
    Idea:   -instead of saving a conflict Matrix, save Cliques of exams that cannot be written at the same time
            -then instead of saying of one exam is written in a given period all conflicts cannot be written in the same period we could say
            -for all exams in a given clique only one can be written
    """
    
    if verbose:
        print("c3: avoid conflicts")
    for i in range(n):
        for l in range(p):
            # careful!! Big M changed!
            model.addConstr(quicksum([ y[j,l] for j in conflicts[i] ]) <= (1 - y[i, l]) * sum(conflicts[i]), "c3")
    
    if verbose:
        print("c4: seats for all students")
    for i in range(n):
        model.addConstr( quicksum([ x[i, k, l] * c[k] for k in range(r) for l in range(p) if T[k][l] == 1 and location[k] in w[i] ]) >= s[i], "c4")
    
    if verbose:
        print("c5: only one exam per room per period")
    for k in range(r):
        for l in range(p):
            if T[k][l] == 1:
                model.addConstr( quicksum([ x[i, k, l] for i in range(n) if location[k] in w[i] ]) <= 1, "c5")    
    

    if verbose:
        print("All constrained built - OK")

    

    # objective: minimize number of used rooms
    if verbose:
        print("Building Objective...")
    obj1 = quicksum([ x[i,k,l] for i,k,l in itertools.product(range(n), range(r), range(p)) if T[k][l] == 1 and location[k] in w[i]]) 

    model.setObjective( obj1, GRB.MINIMIZE)

    print timeit.default_timer()-start

    if not verbose:
        model.params.OutputFlag = 0
    
    # Set Parameters
    #print("Setting Parameters...")
 
    # max presolve agressivity
    #model.params.presolve = 2
    # Choosing root method 3= concurrent = run barrier and dual simplex in parallel
    #model.params.method = 1
    #model.params.MIPFocus = 1
    #model.params.cuts = 0
    model.params.OutputFlag = 1


    # # Tune the model
    # model.tune()

    # if model.tuneResultCount > 0:

    #     # Load the best tuned parameters into the model
    #     model.getTuneResult(0)

    #     # Write tuned parameters to a file
    #     model.write('tune1.prm')

    # return
    return(model)



if __name__ == "__main__":
    
    n = 150
    r = 20
    p = 20  

    # generate data
    random.seed(42)
    data = build_random_data(n=n, r=r, p=p, prob_conflicts=0.75)
    exams = [ 'Ana%s' % (i+1) for i in range(n) ]
    rooms = ['MI%s' % (k+1) for k in range(r)]
    
    # Create and solve model
    t = time()
    try:        
        model = build_model(data, n_cliques = 30)        
        
        model.optimize()
        
        for v in model.getVars():
            if v.x == 1 and ("x" in v.varName or "y" in v.varName): 
                print('%s %g' % (v.varName, v.x))

        print('Obj: %g' % model.objVal)
    except GurobiError:
        print('Error reported')
    t = time() - t
    print('Runtime: %0.2f s' % t)
    