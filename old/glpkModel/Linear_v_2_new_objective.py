
# wrapper class
class glpkWrapper(object):
    ''' 
    A simple wrapper for the PyMathProg glpk class 
    This should have as little functionality as possible!
    '''
    
    def __init__(self, model=None):
        self.model = model
        self.objVal = 0
        
    def optimize(self):
        
        #result = self.model.solve()
        self.model.solvopt(msg_lev = 3, mir_cuts=False, gmi_cuts=True, presolve=True, #pp_tech=2,
                           tm_lim=6000)
        result = self.model.solve()
        self.objVal = self.model.vobj()
        return result

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
from time import time

import pymprog
from model.instance import build_random_data

'''

Model GurobiLinearAdvanced has fewer variables since it doesnt create x_(i,k,l) if room k is closed in period l

'''

# Create variables
def build_model(data, n_cliques = 0, spread_time=False):
    
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
    
    model = pymprog.model("ExaminationScheduling")    
    print("Building variables...")
    
    # x[i,k,l] = 1 if exam i is at time l in room k
    
    NxRxP = [ (i,k,l) for i in range(n) for k in range(r) for l in range(p) if T[k][l] == 1 ]
    x = model.var(NxRxP, 'x', kind=bool) 

    # y[i,l] = 1 if exam i is at time l
    NxP = itertools.product(range(n), range(p))
    y = model.var(NxP, 'y', kind=bool) 
    y[1,1] = 1
    if spread_time:
        # help variable z[i,j] and delta[i,j] for exam i and exam j
        # we are only interested in those exams i and j which have a conflict!
        NxN = [ (i,j) for i in range(n) for j in conflicts[i] ]
        z = model.var(NxN, 'z') 
        delta = model.var(NxN, 'delta', kind=bool) 
    
        # min abs replacement variable
        w = model.var() 
    
    # adding variables as found in MidTerm.pdf
    print("Building constraints...")    
    
    print("c1: connecting variables x and y")
    for i in range(n):
        for l in range(p):
            model.st( sum([ x[i, k, l] for k in range(r) if T[k][l] == 1 ]) <= r * y[i, l], "c1a")
            model.st( sum([ x[i, k, l] for k in range(r) if T[k][l] == 1 ]) >= y[i, l], "c1b")            
            
    print("c2: each exam at exactly one time")
    for i in range(n):
        model.st( sum([ y[i, l] for l in range(p) ]) == 1 , "c2")
    
    print("c3: avoid conflicts")
    for i in range(n):
        for l in range(p):
            # careful!! Big M changed!
            model.st(sum([ y[j,l] for j in conflicts[i] ]) <= (1 - y[i, l]) * sum(conflicts[i]), "c3")
    
    print("c4: seats for all students")
    for i in range(n):
        model.st( sum([ x[i, k, l] * c[k] for k in range(r) for l in range(p) if T[k][l] == 1 ]) >= s[i], "c4")
    
    print("c5: only one exam per room per period")
    for k in range(r):
        for l in range(p):
            if T[k][l] == 1:
                model.st( sum([ x[i, k, l] for i in range(n)  ]) <= 1, "c5")
    
    print("c7: resolving the absolute value")
    if spread_time:
        for i in range(n):
            for j in conflicts[i]:
                model.st( z[i, j] <= sum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) + delta[i,j] * (2*h[len(h)-1]), "c7a")
                model.st( z[i, j] <= -sum([ h[l]*(y[i,l]-y[j,l]) for l in range(p) ]) + (1-delta[i,j]) * (2*h[len(h)-1]), "c7b")
                model.st( z[i, j] >= sum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) , "c7c")
                model.st( z[i, j] >= -sum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) , "c7d")
                model.st( w <= z[i, j] , "c7e")
            
    
    print("c8: Building clique constraints")
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
                model.st( sum([ y[i, l] for i in clique ]) <= 1, "c_lique")
            
    print("OK")

    # objective: minimize number of used rooms and maximize the distance of exams
    print("Building Objective...")
    gamma = 1
    
    obj1 = sum([ 1.0 * x[i,k,l]  for i,k,l in itertools.product(range(n), range(r), range(p)) if T[k][l] == 1 ]) 
    obj2 = 0
    if spread_time:
        obj2 = -w
    
    model.min(obj1 + gamma * obj2, 'ExaminationScheduling')
    
    return(model,y)

    
if __name__ == "__main__":
    
    n = 12
    r = 8
    p = 8

    # generate data
    random.seed(42)
    data = build_random_data(n=n, r=r, p=p, prob_conflicts=0.9)
    exams = [ 'Ana%s' % (i+1) for i in range(n) ]
    rooms = ['MI%s' % (k+1) for k in range(r)]
    
    # Create and solve model
    model, x = build_model(data, n_cliques = 0)   
    model.solvopt(msg_lev = 3, mir_cuts=False, gmi_cuts=True, presolve=True, #pp_tech=2,
                           tm_lim=6000)
    result = model.solve()
    objVal = model.vobj()
        
    
    #model.optimize()
    t = time() - t
    print x
    print('Obj: %g' % objVal)
    print('Runtime: %0.2f s' % t)
    