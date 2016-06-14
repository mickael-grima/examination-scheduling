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
import random as rd
import networkx as nx
import math 
from time import time
    
from gurobipy import Model, quicksum, GRB, GurobiError
from model.instance import build_random_data

from heuristics.simulated_annealing import swap_color_dictionary

def exact_time_schedule(data, exam_colors, n_cliques = 0):
    
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
    
    w = {}
    for i in range(n):
        w[i] = model.addVar(vtype=GRB.INTEGER, name="w_%s" % (i))
        
    # integrate new variables
    model.update() 

    # adding constraints as found in MidTerm.pdf
    print("Building constraints...")    
            
    print("c1: each exam at exactly one time")
    for i in range(n):
        model.addConstr( quicksum([ y[i, l] for l in range(p) ]) == 1 , "c2")

    print("c2: avoid conflicts")
    for i in range(n):
        for l in range(p):
            # careful!! Big M changed!
            model.addConstr(quicksum([ y[j,l] for j in conflicts[i] ]) <= (1 - y[i, l]) * sum(conflicts[i]), "c3")
    
    print("c3: Building %d clique constraints" %n_cliques)
    if n_cliques > 0:
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
                #print "c_lique_%s_%s_%s" % (counter,clique,l)
    
    print("c4: resolving the absolute value")
    for i in range(n):
        for j in conflicts[i]:
            model.addConstr( z[i, j] <= quicksum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) + delta[i,j] * (2*h[len(h)-1]), "c7a")
            model.addConstr( z[i, j] <= -quicksum([ h[l]*(y[i,l]-y[j,l]) for l in range(p) ]) + (1-delta[i,j]) * (2*h[len(h)-1]), "c7b")
            model.addConstr( z[i, j] >= quicksum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) , "c7c")
            model.addConstr( z[i, j] >= -quicksum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) , "c7d")
            model.addConstr( w[i] <= z[i,j], "c7e")            
    
    print("c5: coloring")
    color_exams = swap_color_dictionary(exam_colors)
    for color in color_exams:
        for l in range(p):
            for i in color_exams[color]:
                for j in range(n):
                    if i == j:
                        continue
                    if j in color_exams[color]:
                        model.addConstr( y[i,l] == y[j,l], "c5a")            
                    else:
                        model.addConstr( y[i,l] != y[j,l], "c5b")            
            
    print("All constrained built - OK")

    # objective: minimize number of used rooms
    print("Building Objective...")
    obj1 = quicksum([ w[i] for i in range(n)]) 

    model.setObjective( obj1, GRB.MAXIMIZE)

    # Set Parameters
    #print("Setting Parameters...")
    model.setParam(GRB.Param.Threads, 1)
    # max presolve agressivity
    #model.params.presolve = 2
    # Choosing root method 3= concurrent = run barrier and dual simplex in parallel
    #model.params.method = 1

    # return
    return(model)



if __name__ == "__main__":
    
    rd.seed(42)
    n = 1500
    r = 60
    p = 60
    n_colors = 50
    
    data = build_random_data( n=n, r=r, p=p, prob_conflicts=0.75 )
    exams = [ 'Ana%s' % (i+1) for i in range(n) ]
    rooms = ['MI%s' % (k+1) for k in range(r)]
    
    # random coloring
    exam_colors = { i: rd.randint(0,n_colors-1) for i in range(n) }
    
    # Create and solve model
    t = time()
    try:        
        model = exact_time_schedule(data, exam_colors, n_cliques = 30)        
        
        model.optimize()
        
        for v in model.getVars():
            if v.x == 1 and "y" in v.varName: 
                print('%s %g' % (v.varName, v.x))

        print('Obj: %g' % model.objVal)
    except GurobiError:
        print('Error reported')
    t = time() - t
    print('Runtime: %0.2f s' % t)
    