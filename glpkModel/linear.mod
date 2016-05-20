param n, integer, >= 1;
param r, integer, >= 1;
param p, integer, >= 1;
    
set N, default {1..n};
set R, default {1..r};
set P, default {1..p};

set NxRxP, within N cross R cross P
set NxP, within N cross P;
set NxN, within N cross N;
    
var x{(i,k,l) in NxRxP}, >= 0, <= 1;
var y{(i,l) in NxP}, >= 0, <= 1;

param s{i in N}, > 0; // number of students
param c{i in R}, > 0; // room capacities

s.t. connection_1{
s.t. node{i in NxP}:
    sum([ x[i, k, l] for k in range(r) if T[k][l] == 1 ]) <= r * y[i, l], "c1a")
            model.st( sum([ x[i, k, l] for k in range(r) if T[k][l] == 1 ]) >= y[i, l], "c1b")            
    
    
/* node[i] is conservation constraint for node i */

   sum{(j,i) in E} x[j,i] + (if i = s then flow)
   /* summary flow into node i through all ingoing arcs */

   = /* must be equal to */

   sum{(i,j) in E} x[i,j] + (if i = t then flow);
   /* summary flow from node i through all outgoing arcs */

maximize obj: flow;
/* objective is to maximize the total flow through the network */

solve;

printf{1..56} "="; printf "\n";
printf "Maximum flow from node %s to node %s is %g\n\n", s, t, flow;
printf "Starting node   Ending node   Arc capacity   Flow in arc\n";
printf "-------------   -----------   ------------   -----------\n";
printf{(i,j) in E: x[i,j] != 0}: "%13s   %11s   %12g   %11g\n", i, j,
   a[i,j], x[i,j];
printf{1..56} "="; printf "\n";

data;

/* These data correspond to an example from [Christofides]. */

/* Optimal solution is 29 */

param n := 9;

end;



# Create variables
def build_model(data, n_cliques = 20):
    
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
    
    x = model.var(NxRxP, 'x', bool) 

    # y[i,l] = 1 if exam i is at time l
    y = model.var(NxP, 'y', bool) 
    
    # help variable z[i,j] and delta[i,j] for exam i and exam j
    # we are only interested in those exams i and j which have a conflict!
    z = model.var(NxN, 'z', bool) 
    delta = model.var(NxN, 'delta', bool) 
    
    
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
    
    print("c6: any multi room exam takes place at one moment in time")
    for i in range(n):
        for l in range(p):
            model.st(sum([ x[i, k, m] for k in range(r) for m in range(p) if m != l and T[k][m] == 1 ]) <= (1 - y[i, l]) * r, "c6")
    
    print("c7: resolving the absolute value")
    for i in range(n):
        for j in conflicts[i]:
            model.st( z[i, j] <= sum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) + delta[i,j] * (2*h[len(h)-1]), "c7a")
            model.st( z[i, j] <= -sum([ h[l]*(y[i,l]-y[j,l]) for l in range(p) ]) + (1-delta[i,j]) * (2*h[len(h)-1]), "c7b")
            model.st( z[i, j] >= sum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) , "c7c")
            model.st( z[i, j] >= -sum([ h[l]*(y[i,l] - y[j,l]) for l in range(p) ]) , "c7d")
            
    
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
            model.st( sum([ y[i, l] for i in clique ]) <= 1, "c_lique")
        
    print("OK")

    # objective: minimize number of used rooms and maximize the distance of exams
    print("Building Objective...")
    gamma = 1
    obj1 = sum([ x[i,k,l] * s[i] for i,k,l in itertools.product(range(n), range(r), range(p)) if T[k][l] == 1 ]) 
    obj2 = -sum([ z[i,j] for i in range(n) for j in conflicts[i] ])
    #print(x)
    #obj1 = sum(x.values()) 
    #obj2 = -sum(z.values())
    
    model.min(obj1 + gamma * obj2, 'ExaminationScheduling')
    
    print("Setting Parameters...")
    print("None")
    
    return(glpkWrapper(model),y)

    

if __name__ == "__main__":
    
    n = 6
    r = 6
    p = 6

    # generate data
    random.seed(42)
    data = build_random_data(n=n, r=r, p=p, prob_conflicts=0.9)
    exams = [ 'Ana%s' % (i+1) for i in range(n) ]
    rooms = ['MI%s' % (k+1) for k in range(r)]
    
    # Create and solve model
    model,x = build_model(data, n_cliques = 0)   
    print("Optimizing...")
    model.optimize()
    print x
    print('Obj: %g' % model.objVal)
