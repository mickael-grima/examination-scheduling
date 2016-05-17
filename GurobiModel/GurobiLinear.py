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

from gurobipy import Model, quicksum, GRB, GurobiError
from model.instance import build_random_data

# Create variables
def build_model(data):
    
    # Load Data Format
    n = data['n']
    r = data['r']
    p = data['p']
    s = data['s']
    c = data['c']
    h = data['h']
    Q = data['Q']
    T = data['T']
    model = Model("ExaminationScheduling")
    
    # Build variables
    print("Building variables...")
    
    # x[i,k,l] = 1 if exam i is at time l in room k
    x = {}
    for i in range(n):
        for k in range(r):
            for l in range(p):
                x[i,k,l] = model.addVar(vtype=GRB.BINARY, name="x_%s_%s_%s" % (i,k,l))
    
    # y[i,l] = 1 if exam i is at time l
    y = {}
    for i in range(n):
        for l in range(p):
            y[i, l] = model.addVar(vtype=GRB.BINARY, name="y_%s_%s" % (i,l))
    
    # help variable z[i,j] and delta[i,j] for exam i and exam j
    # we are only interested in those exams i and j which have a conflict!
    z = {}
    delta = {}
    for i in range(n):
        for j in range(i+1,n):
            if Q[i][j] == 0:
                continue
            z[i, j] = model.addVar(vtype=GRB.INTEGER, name="z_%s_%s" % (i,j))
            delta[i, j] = model.addVar(vtype=GRB.BINARY, name="delta_%s_%s" % (i,j))
    
    # integrate new variables
    model.update() 

    # adding variables as found in MidTerm.pdf
    print("Building constraints...")    
    print("c1: connecting variables x and y")
    for i in range(n):
        for l in range(p):
            model.addConstr( quicksum([ x[i, k, l] for k in range(r) ]) <= r * y[i, l], "c1a")
            model.addConstr( quicksum([ x[i, k, l] for k in range(r) ]) >= y[i, l], "c1b")
            
    print("c2: each exam at exactly one time")
    for i in range(n):
        model.addConstr( quicksum([ y[i, l] for l in range(p) ]) == 1 , "c2")
    
    print("c3: avoid conflicts")
    for i in range(n):
        for l in range(p):
            model.addConstr(quicksum([ Q[i][j] * y[j,l] for j in range(i+1,n) if Q[i][j] == 1 ]) <= (1 - y[i, l]) * sum(Q[i]), "c3")
    
    print("c4: seats for all students")
    for i in range(n):
        model.addConstr( quicksum([ x[i, k, l] * c[k] for k in range(r) for l in range(p)]) >= s[i], "c4")
    
    print("c5: only one exam per room per period")
    for k in range(r):
        for l in range(p):
            model.addConstr( quicksum([ x[i, k, l] for i in range(n) ]) <= T[k][l], "c5")
    
    print("c6: any multi room exam takes place at one moment in time")
    for i in range(n):
        for l in range(p):
            model.addConstr(quicksum([ x[i, k, m] for k in range(r) for m in range(p) if m != l ]) <= (1 - y[i, l])*r, "c6")
    
    print("c7: resolving the absolute value")
    for i in range(n):
        for j in range(i+1,n):
            if Q[i][j] == 0:
                continue
            model.addConstr( z[i, j] <= quicksum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) + delta[i,j] * (2*h[len(h)-1]), "c7a")
            model.addConstr( z[i, j] <= -quicksum([ h[l]*(y[i,l]-y[j,l]) for l in range(p) ]) + (1-delta[i,j]) * (2*h[len(h)-1]), "c7b")
            model.addConstr( z[i, j] >= quicksum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) , "c7c")
            model.addConstr( z[i, j] >= -quicksum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) , "c7d")
            
    print("OK")

    # objective: minimize number of used rooms and maximize the distance of exams
    print("Building Objective...")
    gamma = 1
    obj1 = quicksum([ x[i,k,l] * s[i] for i,k,l in itertools.product(range(n), range(r), range(p)) ]) 
    obj2 = -quicksum([ Q[i][j] * z[i,j] for i in range(n) for j in range(i+1,n) if Q[i][j] == 1])

    model.setObjective( obj1 + gamma * obj2, GRB.MINIMIZE)
    # Set Parameters
    print("Setting Parameters...")
    # max presolve agressivity
    model.params.presolve = 2
    # Choosing root method 3= concurrent = run barrier and dual simplex in parallel
    #model.params.method = 1

    # return
    return(model)


if __name__ == "__main__":
    
    n = 10
    r = 5
    p = 10   

    # generate data
    random.seed(42)
    data = build_random_data(n=n, r=r, p=p, conflicts=0.75)
    print(data['h'])
    print(data['c'])
    print(data['s'])
    exams = [ 'Ana%s' % (i+1) for i in range(n) ]
    rooms = ['MI%s' % (k+1) for k in range(r)]
    
    # Create and solve model
    try:        
        model = build_model(data)        
        
        model.optimize()

        
        for v in model.getVars():
            if v.x == 1 and ("x" in v.varName or "y" in v.varName): 
                print('%s %g' % (v.varName, v.x))

        print('Obj: %g' % model.objVal)

    except GurobiError:
        print('Error reported')