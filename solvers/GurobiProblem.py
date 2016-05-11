

from gurobipy import *

try:

    #Create constants
    n = 10;
    r = 10;
    p = 10;

    # Create a new model
    m = Model("ExaminationScheduling")

    # Create variables
    x = {}
    y = {}
    for j in range(n):
        for k in range(r):
            x[i,k] = m.addVar(vtype=GRB.BINARY, name="x")
        for l in range(p):
            y[i,l] = m.addVar(vtype=GRB.BINARY, name="y")


    # Integrate new variables
    m.update()

    # Set objective
    m.setObjective(x + y + 2 * z, GRB.MAXIMIZE)

    # Add constraint: x + 2 y + 3 z <= 4
    m.addConstr(x + 2 * y + 3 * z <= 4, "c0")

    # Add constraint: x + y >= 1
    m.addConstr(x + y >= 1, "c1")

    m.optimize()

    for v in m.getVars():
        print('%s %g' % (v.varName, v.x))

    print('Obj: %g' % m.objVal)

except GurobiError:
    print('Error reported')