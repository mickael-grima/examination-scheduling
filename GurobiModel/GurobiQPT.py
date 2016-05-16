
import itertools
import random

from gurobipy import *

try:

    #Create constants

    random.seed(597)

    exams = []
    examstudents = {}
    for i in range(50):
    	exams.extend(['Ana%s' % (i+1) ])
    	examstudents.update({'Ana%s' % (i+1) : random.randint(20, 500)})
    print examstudents

    rooms = []
    roomcapacity = {}
    for i in range(15):
    	rooms.extend(['MI%s' % (i+1) ])
    	roomcapacity.update({'MI%s' % (i+1) : random.randint(20, 350)})

    hours = []
    for i in range(10):
    	hours.extend([i*2])


    #exams, examstudents = multidict({'Ana1': 100, 'Ana2': 79, 'Ana3': 14, 'Ana4': 34, 'Ana5': 300 ,'Ana6': 100, 'Ana7': 79, 'Ana8': 1004, 'Ana9': 304, 'Ana10': 300, 'Ana11': 100, 'Ana12': 79, 'Ana13': 14, 'Ana14': 30, 'Ana15': 300})
    #rooms, roomcapacity = multidict({'MI1': 100, 'MI2': 103,'MI3': 100, 'MI4': 100, 'MI5': 103,'MI6': 34, 'MI7': 100, 'MI8': 103,'MI9': 23, 'MI10': 100, 'MI11': 103,'MI12': 150})
    #hours = [0,2,4]
    numberofperiods = len(hours)

    t = {}
    k = {}
    for room in rooms:
    	for l in range(numberofperiods):
    		t[room,l] = 1

    for examA in exams:
    	for examB in exams:
    		k[examA,examB] = 0

    print "Konstanten generiert"

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

    print "Variablen generiert"



    # Integrate new variables
    m.update()

    # Add constraints
    for exam in exams:
    	# Add constraint: Each exam is planned in exactly one period
    	m.addConstr( quicksum([y[exam,l] for l in range(numberofperiods)]) == 1, "c0")

    	# Add constraint: Each exam has enough seats
    	m.addConstr( quicksum([x[exam,room]*roomcapacity[room] for room in rooms]) >= examstudents[exam], "c1")


    print "Bedingungen 1 generiert"

    # Add constraint: Each room has at most one exam per period
    for room in rooms:
    	for l in range(numberofperiods):
    		m.addQConstr( quicksum([x[exam,room]*y[exam,l] for exam in exams]) <= t[room,l], "c2")
    	print "Bedingungen 2 - %s generiert" % (room)

    # # Add constraint: There are no conflicts - linear - takes to long to add
    # for l in range(numberofperiods):
    # 	for room in rooms:
    # 		for examA,examB in itertools.combinations(exams,2):
    # 			m.addConstr( x[examA,room] + x[examB,room] + y[examA,l] + y[examB,l] <= 3,  "c2a")
    # 			print "Bedingungen 2a - %s - %s generiert" % (l,room)
    # 		for exam in exams:
    # 			if t[room,l] == 0:
    # 				m.addConstr( x[exam,room] + y[exam,l] <= 1 , "c2b")
    # 				"Bedingungen 2b generiert"


    

    # Add constraint: There are no conflicts quadratic
    for l in range(numberofperiods):
    	m.addQConstr( quicksum([y[examA,l]*y[examB,l]*k[examA,examB] for examA, examB in itertools.combinations(exams,2) if k[examA,examB] == 1 ]) == 0,  "c3")
    	print "Bedingungen 3 %s generiert" % (l)




    ###### Improve speed by generating combinations of examA and examb outside of loop
    


    # Set objective
    m.setObjective(-1*quicksum([k[examA,examB]*(quicksum([y[examA,l]*hours[l] - y[examB,l]*hours[l] for l in range(numberofperiods)]))*(quicksum([y[examA,l]*hours[l] - y[examB,l]*hours[l] for l in range(numberofperiods)])) for examA, examB in itertools.combinations(exams,2) if k[examA,examB] == 1])  +  quicksum([x[exam,room]*examstudents[exam] for exam,room in itertools.product(exams,rooms)])  , GRB.MINIMIZE)
 
    print "Zielfunktion gesetzt"



    m.tune()

    m.params.TuneTimeLimit = 50

    model.tune()
    for i in range(model.tuneResultCount):
    	model.getTuneResult(i)
    	model.write('tune'+str(i)+'.prm')


    for v in m.getVars():
    	if v.x == 1:
        	print('%s %g' % (v.varName, v.x))

    print('Obj: %g' % m.objVal)

except GurobiError:
    print('Error reported')