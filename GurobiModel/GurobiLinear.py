
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
    for i in range(n):
        for k in range(r):
            for l in range(p):
                x[i,k,l] = model.addVar(vtype=GRB.BINARY, name="x_%s_%s_%s" % (i,k,l))
    y = {}
    for i in range(n):
        for l in range(p):
            y[i, l] = model.addVar(vtype=GRB.BINARY, name="y_%s_%s" % (i,l))
    
    z = {}
    delta = {}
    for i in range(n):
        for j in range(n):
            z[i, j] = model.addVar(vtype=GRB.BINARY, name="z_%s_%s" % (i,j))
            delta[i, j] = model.addVar(vtype=GRB.BINARY, name="delta_%s_%s" % (i,j))
    
    model.update() # integrate new variables

    print("Building constraints...")    
    print("c1: connecting variables")
    for i in range(n):
        for l in range(p):
            model.addConstr( quicksum([ x[i, k, l] for k in range(r) ]) <= r * y[i, l], "c1a")
            model.addConstr( quicksum([ x[i, k, l] for k in range(r) ]) >= y[i, l], "c1b")
            
            
    print("c2: each exam exactly at one time")
    for i in range(n):
        model.addConstr( quicksum([ y[i, l] for l in range(p) ]) == 1 , "c2")
    
    
    print("c3: no conflicts")
    for i in range(n):
        for l in range(p):
            model.addConstr(quicksum([ Q[i][j] * y[j,l] for j in range(i+1,n) ]) <= (1 - y[i, l]) * sum(Q[i]), "c3")
    
    
    print("c4: enough seats for all students")
    for i in range(n):
        model.addConstr( quicksum([ x[i, k, l] * c[k] for k in range(r) for l in range(p)]) >= s[i], "c4")
    
    
    print("c5: maximal one exam per room per period")
    for k in range(r):
        for l in range(p):
            model.addConstr( quicksum([ x[i, k, l] for i in range(n) ]) <= T[k][l], "c5")
    
    
    print("c6: a multi room exam takes place at one moment in time")
    for i in range(n):
        for l in range(p):
            model.addConstr(quicksum([ x[i, k, m] for k in range(r) for m in range(p) if m != l ]) <= (1 - y[i, l])*r, "c6")
    
    print("c7: resolving the absolute value")
    for i in range(n):
        for j in range(n):
            model.addConstr( z[i, j] <= quicksum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) + delta[i,j] * (h[len(h)-1] - h[0]), "c7a")
            model.addConstr( z[i, j] <= -quicksum([ h[l]*(y[i,l]-y[j,l]) for l in range(p) ]) + (1-delta[i,j]) * (h[len(h)-1]-h[0]), "c7b")
            model.addConstr( z[i, j] <= quicksum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) , "c7c")
            model.addConstr( -z[i, j] <= quicksum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) , "c7d")
            
    print("OK")

    print("Building Objective...")
    gamma = 0.4
    model.setObjective( quicksum([ x[i,k,l] * s[i] for i,k,l in itertools.product(range(n), range(r), range(p)) ]) 
                        - gamma * quicksum([ Q[i][j] * z[i,j] for j in range(i+1,n) for i in range(n) ]) , GRB.MINIMIZE)
    print("Setting Params...")

    # Set Parameter
    #model.params.mipfocus = 3
    #maximum level of linearization
    #model.params.preqlinearize = 1
    #max presolve agressivity
    #model.params.presolve = 2
    #Choosing root method 3= concurrent = run barrier and dual simplex in parallel
    #model.params.method = 1

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