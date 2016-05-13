
import itertools

from gurobipy import *

try:

    #Create constants
    exams, examstudents = multidict({'Ana1': 100, 'Ana2': 79, 'Ana3': 14, 'Ana4': 34, 'Ana5': 300   })
    rooms, roomcapacity = multidict({'MI1': 100, 'MI2': 103,'MI3': 400})
    hours = [0,2,4]
    numberofperiods = len(hours)

    t = {}
    k = {}
    for room in rooms:
    	for l in range(numberofperiods):
    		t[("%s" % (room) ,"%s" % (l)) ] = 1

    for examA in exams:
    	for examB in exams:
    		k[("%s" % (examA),"%s" % (examB))] = 0


    for examA, examB in itertools.combinations(exams,2):
    	print examA, "+", examB

    # Create a new model
    m = Model("ExaminationScheduling")

    # Create variables
    x = {}
    y = {}
    for exam in exams:
        for room in rooms:
            x[exam,room] = m.addVar(vtype=GRB.BINARY, name="x_%s_%s" % (exam,room))
        for l in range(numberofperiods):
            y[exam, l] = m.addVar(vtype=GRB.BINARY, name="y_%s_%s" % (exam,l))



    # Integrate new variables
    m.update()

    # Add constraints
    for exam in exams:
    	# Add constraint: Each exam is planned in exactly one period
    	m.addConstr( quicksum( y[exam,l] for l in range(numberofperiods) ) == 1, "c0")

    	# Add constraint: Each exam has enough seats
    	m.addConstr( quicksum(x[exam,room]*roomcapacity[room] for room in rooms) >= examstudents[exam], "c1")

    # Add constraint: Each room has at most one exam per period
    for room in rooms:
    	for l in range(numberofperiods):
    		m.addQConstr( quicksum(x[exam,room]*y[exam,l] for exam in exams) <= t[("%s"  % (room),"%s" % (l))], "c2")

    # Add constraint: There are no conflicts
    for l in range(numberofperiods):
    	m.addQConstr( quicksum(y[examA,l]*y[examB,l]*k[("%s" % (examA),"%s" % (examB))] for examA, examB in itertools.combinations(exams,2) if examA != examB ) == 0,  "c3")



    # Set objective
    m.setObjective(quicksum(x[exam,room]*examstudents[exam] for exam,room in itertools.product(exams,rooms) )  , GRB.MINIMIZE)

    m.optimize()

    for v in m.getVars():
    	if v.x == 1:
        	print('%s %g' % (v.varName, v.x))

    print('Obj: %g' % m.objVal)

except GurobiError:
    print('Error reported')