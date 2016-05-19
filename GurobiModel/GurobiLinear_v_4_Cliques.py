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
    
from gurobipy import Model, quicksum, GRB, GurobiError
from model.instance import build_random_data

'''

	-Model GurobiLinear_v_3 has fewer variables since it doesnt create x_(i,k,l) if room k is closed in period l
	-Model GurobiLinear_v_4_Cliques adds Clique constraints for conflicts only one exam in a clique conflict can take place at a time

'''

'''
	***************  POSSIBLE IMPROVEMENTS    ***************
	
	-Add an option that such that courses in Garching are only schedule in rooms in Garchin and vice versa -> Removes lots of variables
	-Change objective function:
		-our current objective funcion fails for cliques (all exams have conflicts) for example 
			*exam1 on day 1
			*exam2 on day 5
			*exam3 on day 10
			*Our current objective function |5-1|+|10-5|+|10-1| = 18
			*exam1 on day 1
			*exam2 on day 1
			*exam3 on day 10
			*Has exactly the same objective function of 18 but clearly the first schedule is by far better
	-Change in "c6: any multi room exam takes place at one moment in time" the r in big M-Method from r to min{10, ceil(si/75)} or similiar [to discuss]
'''

# Create variables
def build_model(data, n_cliques = 2):
    
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
    
    model = Model("ExaminationScheduling")
    
    
    print("Building variables...")
    
    # x[i,k,l] = 1 if exam i is at time l in room k
    x = {}
    for i in range(n):
        for k in range(r):
            for l in range(p):
                if T[k][l] == 1:
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
        for j in conflicts[i]:
            z[i, j] = model.addVar(vtype=GRB.INTEGER, name="z_%s_%s" % (i,j))
            delta[i, j] = model.addVar(vtype=GRB.BINARY, name="delta_%s_%s" % (i,j))
    
    # integrate new variables
    model.update() 

    # adding variables as found in MidTerm.pdf
    print("Building constraints...")    
    
    print("c1: connecting variables x and y")
    for i in range(n):
        for l in range(p):
            model.addConstr( quicksum([ x[i, k, l] for k in range(r) if T[k][l] == 1 ]) <= r * y[i, l], "c1a")
            model.addConstr( quicksum([ x[i, k, l] for k in range(r) if T[k][l] == 1 ]) >= y[i, l], "c1b")
            
    print("c2: each exam at exactly one time")
    for i in range(n):
        model.addConstr( quicksum([ y[i, l] for l in range(p) ]) == 1 , "c2")

    """
    Idea:   -instead of saving a conflict Matrix, save Cliques of exams that cannot be written at the same time
            -then instead of saying of one exam is written in a given period all conflicts cannot be written in the same period we could say
            -for all exams in a given clique only one can be written
    """
    
    print("c3: avoid conflicts")
    for i in range(n):
        for l in range(p):
            # careful!! Big M changed!
            model.addConstr(quicksum([ y[j,l] for j in conflicts[i] ]) <= (1 - y[i, l]) * sum(conflicts[i]), "c3")
    
    print("c4: seats for all students")
    for i in range(n):
        model.addConstr( quicksum([ x[i, k, l] * c[k] for k in range(r) for l in range(p) if T[k][l] == 1 ]) >= s[i], "c4")
    
    print("c5: only one exam per room per period")
    for k in range(r):
        for l in range(p):
            if T[k][l] == 1:
                model.addConstr( quicksum([ x[i, k, l] for i in range(n)  ]) <= 1, "c5")
    
    print("c6: any multi room exam takes place at one moment in time")
    for i in range(n):
        for l in range(p):
            Mr = 10 if 10 < s[i]/75 else s[i]/75
            model.addConstr(quicksum([ x[i, k, m] for k in range(r) for m in range(p) if m != l and T[k][m] == 1 ]) <= (1 - y[i, l]) * r, "c6")
    
    print("c7: resolving the absolute value")
    for i in range(n):
        for j in conflicts[i]:
            model.addConstr( z[i, j] <= quicksum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) + delta[i,j] * (2*h[len(h)-1]), "c7a")
            model.addConstr( z[i, j] <= -quicksum([ h[l]*(y[i,l]-y[j,l]) for l in range(p) ]) + (1-delta[i,j]) * (2*h[len(h)-1]), "c7b")
            model.addConstr( z[i, j] >= quicksum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) , "c7c")
            model.addConstr( z[i, j] >= -quicksum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) , "c7d")
            
    
    print("c8: Building clique constraints")
    G = nx.Graph()
    for i in range(n):
        G.add_node(i)
        
    for i in range(n):
        for j in conflicts[i]:
            G.add_edge(i,j)
            
    cliques = nx.find_cliques(G) # generator
    
    for counter, clique in itertools.izip(range(n_cliques), cliques):
        for l in range(l):
            model.addConstr( quicksum([ y[i, l] for i in clique ]) <= 1, "c_lique_%s_%s_%s" % (counter,clique,l))

    print("All constrained built - OK")

    # objective: minimize number of used rooms and maximize the distance of exams
    print("Building Objective...")
    gamma = 1
    obj1 = quicksum([ x[i,k,l] * s[i] for i,k,l in itertools.product(range(n), range(r), range(p)) if T[k][l] == 1 ]) 
    obj2 = -quicksum([ z[i,j] for i in range(n) for j in conflicts[i] ])

    model.setObjective( obj1 + gamma * obj2, GRB.MINIMIZE)
    # Set Parameters
    print("Setting Parameters...")
    # max presolve agressivity
    #model.params.presolve = 2
    # Choosing root method 3= concurrent = run barrier and dual simplex in parallel
    #model.params.method = 1

    # return
    return(model)


if __name__ == "__main__":
    
    # n = 50
    # r = 20
    # p = 20  

    # # generate data
    # random.seed(42)
    # data = build_random_data(n=n, r=r, p=p, prob_conflicts=0.05)
    # exams = [ 'Ana%s' % (i+1) for i in range(n) ]
    # rooms = ['MI%s' % (k+1) for k in range(r)]
    
    # Create and solve model
    try:        
        model = build_model(data, n_cliques = 0)        
        
        model.optimize()
        
        for v in model.getVars():
            if v.x == 1 and ("x" in v.varName or "y" in v.varName): 
                print('%s %g' % (v.varName, v.x))

        print('Obj: %g' % model.objVal)

    except GurobiError:
        print('Error reported')