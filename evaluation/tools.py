
from time import time
import datetime
import random 
from collections import defaultdict
import pickle

from evaluation.objectives import *

def write_result(x_ikl, y_il, data, filename = None, prob_name = None):
    
    if prob_name is None:
        prob_name = "unspecified"
    if filename is None:
        today = datetime.datetime.today()
        filename = "%sresults/Result_%s_%s_%s_%s_%s_%s.txt" % (PROJECT_PATH, today.year, today.month, today.day, today.hour, today.minute, prob_name )
        
    file = open(filename, 'a+')

    file.write("Number of exams: %s" % data['n'])
    file.write('\n')
    file.write("Number of rooms: %s" % data['r'])
    file.write('\n')
    file.write("Number of periods: %s" % data['p'])
    file.write('\n')
    file.write("Students per Exam: %s" % data['s'])
    file.write('\n')
    file.write("capacity per Room: %s" % data['c'])
    file.write('\n')
    #if data['Q'] is not None:
        #file.write("Conflicts: %s" % data['Q'])
    #else:
    file.write("Conflicts: %s" %data['conflicts'])
    file.write('\n')
    file.write("locking times: %s" % data['T'])
    file.write('\n')
    file.write("faculty weeks: %s" % data['faculty_weeks'])
    file.write('\n')
    
    print "DATA: X"
    for i in range(data['n']):
        file.write('%d' %i)  
        for l in range(data['p']):
            file.write('%d' %l)  
            for k in range(data['r']):
                if x_ikl[i,k,l] == 1:
                    file.write('%d' %k)    
            file.write('\n')            
    
    print "DATA: Y"
    for i in range(data['n']):
        file.write('%d' %i)  
        for l in range(data['p']):
            if y_il[i,l] == 1:
                file.write('%d' %l)    
        file.write('\n')            
                    
    file.write("Room Objective: %f" %obj_room(x_ikl))
    file.write('\n')
    
    file.write("Time Objective: %f" %obj_time_y(y_il, data))
    file.write('\n')
    
    file.write("Full Objective: %f" %obj(x_ikl, y_il, data))
    file.write('\n')
 
