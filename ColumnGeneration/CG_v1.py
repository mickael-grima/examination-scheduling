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
    
from gurobipy import Model, quicksum, GRB, GurobiError


             
    
def build_model(data, n_cliques = 0):
    
    # Load Data Format
    n = data['n']
    r = data['r']
    p = data['p']
    s = data['s']
    c = data['c']
    h = data['h']
    conflicts = data['conflicts']
    locking_times = data['locking_times']
    T = data['T']
    
    model = Model("ExaminationSchedulingCG")
    
    
    print("Building variables...")
    


    # x[p] = 1 if path p is active
    x = {}
    for k in range(r):
    	for p in path[k]:
    		x[p] = model.addVar(vtype=GRB.BINARY, name="x_%s" % (p))
    
    # y[i,l] = 1 if exam i is at time l
    y = {}
    for i in range(n):
        for l in range(p):
            y[i, l] = model.addVar(vtype=GRB.BINARY, name="y_%s_%s" % (i,l))
    
    
    w = model.addVar(vtype=GRB.INTEGER, name="w")
    
    # integrate new variables
    model.update() 

    # adding constraints as found in MidTerm.pdf
    print("Building constraints...")    


    print("c0: connecting variables x and y")
    for i in range(n):
        for l in range(p):
            model.addConstr( quicksum( quicksum(x[p] for p in path[k,i,l])  for k in range(r) ) <= 12 * y[i, l], "c0a")
            model.addConstr( quicksum( quicksum(x[p] for p in path[k,i,l])  for k in range(r) ) >= y[i, l], "c0b")
    
    print("c1: For each room there is exactly one path")
    for k in range(r):
    	model.addConstr(quicksum(x[p] fpr p in path[k]) == 1, "c1" )
            
    print("c2: Enough seating capacity")
    for i in range(n):
        model.addConstr( quicksum( quicksum(x[p]*c[k] for p in path[k] if i in p) for k in range(r)  ) >= s[i] , "c2")
    
    print("c3: Each exam needs to take place in exactly one period")
    for i in range(n):
        model.addConstr( quicksum(y[i,l] for l in range(p)) == 1, "c3")

    print("c4: No conflicts")
    for i in range(n):
    	for l in range(p):
        	model.addConstr( quicksum( y[j,l] if j in conflicts[i]  ) <= (1-y[i,l])*sum(conflicts[i]), "c3")
    
    

    print("All constrained built - OK")

    # objective: minimize number of used rooms
    print("Building Objective...")
    obj1 = quicksum([ x[i,k,l] * s[i] for i,k,l in itertools.product(range(n), range(r), range(p)) if T[k][l] == 1 ]) 

    model.setObjective( obj1, GRB.MINIMIZE)

    # Set Parameters
    print("Setting Parameters...")


    # return
    return(model)


if __name__ == "__main__":
    
    n = 50
    r = 20
    p = 20  

    # generate data
    random.seed(42)
    data = build_random_data(n=n, r=r, p=p, prob_conflicts=0.05)
    exams = [ 'Ana%s' % (i+1) for i in range(n) ]
    rooms = ['MI%s' % (k+1) for k in range(r)]
    
    # Create and solve model
    try:        
        model = build_model(data, n_cliques = 30)        
        
        t = time()
        model.optimize()
        t = time() - t
        
        for v in model.getVars():
            if v.x == 1 and ("x" in v.varName or "y" in v.varName): 
                print('%s %g' % (v.varName, v.x))

        print('Obj: %g' % model.objVal)
        print('Runtime: %0.2f s' % t)
    except GurobiError:
        print('Error reported')