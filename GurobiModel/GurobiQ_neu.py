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
from instance import build_random_data

# Create variables
def build_model(data):
    
    n = data['n']
    r = data['r']
    p = data['p']
    s = data['s']
    c = data['c']
    h = data['h']
    Q = data['Q']
    T = data['T']
    
    model = Model("ExaminationScheduling")
    
    print("Building variables...")
    x = {}
    y = {}
    for i in range(n):
        for k in range(r):
            x[i,k] = model.addVar(vtype=GRB.BINARY, name="x_%s_%s" % (i,k))
        for l in range(p):
            y[i, l] = model.addVar(vtype=GRB.BINARY, name="y_%s_%s" % (i,l))

    model.update() # integrate new variables
    
    print("Building constraints...")    

    # Add constraints
    for i in range(n):

        # Add constraint: Each i is planned in exactly one period
        model.addConstr( quicksum([y[i,l] for l in range(p)]) == 1, "c0")

        # Add constraint: Each i has enough seats
        model.addConstr( quicksum([x[i,k] * c[k] for k in range(r)]) >= s[i], "c1")

    print "Bedingungen 1 generiert"

    # Add constraint: Each k has at most one i per period
    for k in range(r):
        for l in range(p):
            model.addQConstr( quicksum([x[i,k] * y[i,l] for i in range(n)]) <= T[k][l], "c2")

    # Add constraint: There are no conflicts quadratic
    for l in range(p):
        model.addQConstr( quicksum([ y[i,l] * y[j,l] * Q[i][j] for i, j in itertools.combinations(range(n),2) if Q[i][j] == 1]) == 0,  "c3")


    ###### Improve speed by generating combinations of i and j outside of loop

    # Set objective
    #model.setObjective( quicksum([ x[i,k] * s[i] for i,k in itertools.product(range(n), range(r)) ]), GRB.MINIMIZE)
    model.setObjective( -1*quicksum([Q[i][j]*(quicksum([y[i,l]*h[l] - y[j,l]*h[l] for l in range(p)]))*(quicksum([y[i,l]*h[l] - y[j,l]*h[l] for l in range(p)])) for i, j in itertools.combinations(range(n),2) if Q[i][j] == 1])  +  quicksum(x[i,k] * s[i] for i,k in itertools.product(range(n),range(r)) )  , GRB.MINIMIZE)
 
    print "Zielfunktion gesetzt"

    # Set Parameter
    #model.params.mipfocus = 3
    #maximum level of linearization
    model.params.preqlinearize = 1
    #max presolve agressivity
    model.params.presolve = 2
    #Choosing root method 3= concurrent = run barrier and dual simplex in parallel
    model.params.method = 1

    return(model)


if __name__ == "__main__":
    
    n = 20
    r = 10
    p = 5

    # generate data
    random.seed(42)
    data = build_random_data(n=n, r=r, p=p)
    
    exams = [ 'Ana%s' % (i+1) for i in range(n) ]
    rooms = ['MI%s' % (k+1) for k in range(r)]
    
    # Create and solve model
    try:        
        model = build_model(data)
        
        model.optimize()

        for v in model.getVars():
            if v.x == 1: 
                print('%s %g' % (v.varName, v.x))

        print('Obj: %g' % model.objVal)

    except GurobiError:
        print('Error reported')

