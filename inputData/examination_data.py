#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(PROJECT_PATH)

from collections import defaultdict
import re
import numpy as np
import pickle

from model.data_format import force_data_format

def read_columns(datname, key, cols, sep=","):
    '''
    Read csv file and extract data with column names in cols. Takes first value found!
    '''
    
    columns = defaultdict(dict)
    colnames = []
            
    with open("%sinputData/%s"%(PROJECT_PATH, datname)) as csvfile:
        for line in csvfile:
            line = re.sub('\"', '', line)
            line = re.sub('\n', '', line)
            line = re.split(sep, line)
            
            assert len(line) > len(cols)
            
            if len(colnames) == 0:
                colnames = line
            else:
                ident = line[colnames.index(key)]
                for i in range(0, len(colnames)):
                    name = colnames[i]
                    if name in cols and ident not in columns[name]:
                        columns[name][ident] = line[i]
                    
    return columns



def read_result_times(semester):
    # read times from result file
    
    # "","PRFG.NUMMER","startHours","endHours","startDate","endDate"
    prfg = read_columns("%s/prfg_times.csv" %semester, "PRFG.NUMMER", ["startHours", "endHours", "startDate", "endDate"], sep=",")

    startHours = prfg["startHours"]
    
    exam_times = dict()
    for exam in startHours:
        exam_times[exam] = float(startHours[exam])
    
    return exam_times


def read_result_rooms(semester):
    # read rooms from result file
    
    # "","PRFG.NUMMER","startHours","endHours","startDate","endDate"
    
    cols = []
    for i in range(1, 10):
        cols.append("ORT_CODE_0%d" %i)
    for i in range(10, 31):
        cols.append("ORT_CODE_%d" %i)
        
    prfg = read_columns("%s/Ergebnis_%s.csv" %(semester, semester), "PRFG-NUMMER", cols, sep=";")
    
    exam_rooms = defaultdict(set)
    for col in prfg:
        for exam in prfg[col]:
            exam_rooms[exam].add(prfg[col][exam])
    
    for exam in exam_rooms:
        exam_rooms[exam] = list(exam_rooms[exam])
        if '' in exam_rooms[exam]:
            exam_rooms[exam].remove('')
    return exam_rooms


def read_rooms():
    
    # Name;Name_lang;Sitzplaetze;Klausurplaetze_eng;ID_Raum;ID_Gebaeude;Gebaeude;ID_Raumgruppe;ID_Campus;Campus
    room_overview = read_columns("Data/Raumuebersicht.csv", "ID_Raum", ["Klausurplaetze_eng", "ID_Campus"], sep=";")
        
    return room_overview["Klausurplaetze_eng"], room_overview["ID_Campus"]
    
    
    
#def read_locked_rooms():
    ## "","ID_RAUM","startTime","endTime","startDate","endDate"
    #rooms = read_columns("raum_sperren.csv", "ID_RAUM", ["startTime", "endTime", "startDate","endDate"], sep=",")

    #start_hours = rooms["startTime"]
    #end_hours = rooms["endTime"]
    
    ## save locking times in dictionary
    #locking_times_unordered = defaultdict(list)
    
    ## find time indices for which rooms are locked
    #for room in start_hours:
        #for i in range(len(h)-1):
            ## determine position of locking start
            #if start_hours[room] >= h[i] and start_hours[room] <= h[i+1]:
                ##print "found a locked room!"
                #j = i
                ## search for position of locking end
                #while( j < len(h) - 1 ):
                    #if end_hours[room] < h[j]:
                        #break;
                    ## on the way insert locking times to dict
                    #locking_times_unordered[room].append(j)
                    #j += 1
    
    
    #locking_times = defaultdict(list)
    #capacity = defaultdict(int)
    #campus_id = defaultdict(str)
    #room_name = defaultdict(str)
    
    #for k, room in enumerate(room_overview["Klausurplaetze_eng"]):
        #locking_times[k] = locking_times_unordered[room]
        #capacity[k] = room_overview["Klausurplaetze_eng"][room]
        #campus_id[k] = room_overview["ID_Campus"]
        #room_name[k] = room
        
    #return capacity, locking_times, room_name, campus_id

def read_students(filename):
    #MODUL;T_NR;DATUM_T1;ANZ_STUD_MOD1;STUDIS_PRUEF1_GES;STUDIS_PRUEF1_ABGEMELDET;STUD_NICHT_ERSCHIENEN_PRUEF1;MODUL2;T_NR2;DATUM_T2;SEMESTER;ANZ_STUD_MOD2;STUDIS_PRUEF2_GES;STUDIS_PRUEF2_ABGEMELDET;STUD_NICHT_ERSCHIENEN_PRUEF2
    
    # Name;Name_lang;Sitzplaetze;Klausurplaetze_eng;ID_Raum;ID_Gebaeude;Gebaeude;ID_Raumgruppe;ID_Campus;Campus
    students_abs = read_columns(filename, "MODUL", ["STUDIS_PRUEF1_GES", "STUDIS_PRUEF1_ABGEMELDET", "STUD_NICHT_ERSCHIENEN_PRUEF1"], sep=";")
    
    exam_students = dict()
    for exam in students_abs["STUDIS_PRUEF1_GES"]:
        exam_students[exam] = int(students_abs["STUDIS_PRUEF1_GES"][exam]) - int(students_abs["STUDIS_PRUEF1_ABGEMELDET"][exam])
    
    return exam_students
    
    

def read_conflicts(filename, exams = None, threshold = 0):
    #MODUL;T_NR;DATUM_T1;ANZ_STUD_MOD1;STUDIS_PRUEF1_GES;STUDIS_PRUEF1_ABGEMELDET;STUD_NICHT_ERSCHIENEN_PRUEF1;MODUL2;T_NR2;DATUM_T2;SEMESTER;ANZ_STUD_MOD2;STUDIS_PRUEF2_GES;STUDIS_PRUEF2_ABGEMELDET;STUD_NICHT_ERSCHIENEN_PRUEF2
    
    Q_abs = defaultdict(int)
    colnames = []
    
    with open("%sinputData/%s"%(PROJECT_PATH, filename)) as csvfile:
        for line in csvfile:
            line = re.sub('\"', '', line)
            line = re.sub('\n', '', line)
            line = re.split(';', line)
            
            if len(colnames) == 0:
                colnames = line
            else:
                ident1 = line[colnames.index("MODUL")]
                ident2 = line[colnames.index("MODUL2")]
                
                # make sure the exam is used for our solution
                if exams is not None and ident1 not in exams:
                    continue
                if exams is not None and ident2 not in exams:
                    continue
                
                assert line[colnames.index("ANZ_STUD_MOD1")] == line[colnames.index("ANZ_STUD_MOD2")]
                
                # get conflicts
                n_conflicts = int(line[colnames.index("ANZ_STUD_MOD1")])
                
                # build Q matrix
                if n_conflicts > threshold:
                    Q_abs[ident1, ident2] = n_conflicts
                
    print "read"
    n = len(exams)
    Q = [[0 for i in range(n)] for i in range(n)]
    K = defaultdict(int)
    conflicts = defaultdict(list)
    
    for i, e1 in enumerate(exams):
        for j, e2 in enumerate(exams):
            if Q_abs[e1, e2] > 0:
                Q[i][j] = 1
                if j not in conflicts[i]:
                    conflicts[i].append(j)
                if i not in conflicts[j]:
                    conflicts[j].append(i)
                K[i,j] = Q_abs[e1, e2]
            
    return Q, conflicts, K
    
    
@force_data_format
def read_data(semester = "15W", threshold = 0, make_intersection=True, verbose=False, max_periods=None):
    '''
        @ Param make_intersection: Use exams which are in tumonline AND in szenarioergebnis
    '''
    assert semester in ["15W", "16S"], "Wir haben nur Ergebnisse für Winder 15 und Sommer 16!"
    
    anmelde_data = semester
    if semester == "16S":
        anmelde_data = "15S"
    
    #print "Loading data: Data needs verification!"
    if max_periods is not None:
        print "WARNING: max_periods is not implemented any more!"
    
    # load times from szenarioergebnis
    exam_times = read_result_times(semester)
    
    # load room results from szenarioergebnis
    exam_rooms = read_result_rooms(semester)
    
    # load room capacities
    room_capacity, room_campus_id = read_rooms()
    
    # load number of students registered for each exam
    exam_students = read_students("Conflicts/%s.csv" %anmelde_data)
        
    # differences in data size
    if verbose: print len( [exam for exam in exam_times if exam not in exam_students])
    if verbose: print len( [exam for exam in exam_students if exam not in exam_times])
    
    # filter all exams for which we have student data
    exams = [exam for exam in exam_times if exam in exam_students]
    
    if verbose: print "Number of exams", len(exams)
    
    # filter all exams for which we have room data
    exams = [exam for exam in exams if all(room in room_capacity for room in exam_rooms[exam])]
    
    if verbose: print "Number of exams", len(exams)
    if verbose: print "Number of timeslots", len(sorted(set(exam_times.values())))
    
    # build exam data structures
    times = [exam_times[exam] for exam in exams]
    h = sorted(set(times))
    s = [exam_students[exam] for exam in exams]
    
    if verbose: print "Number of timeslots", len(h)
    
    # construct room data
    rooms = sorted(set([ room for exam in exams for room in exam_rooms[exam]]))
    c = [int(room_capacity[room]) for room in rooms]
    
    if verbose: print "Number of rooms", len(rooms)    
    
    ## TODO: load locking rooms
    #c, locking_times, room_names, campus_ids = read_rooms(h)
    
    # construct time data -> 1 if room and time is planned by moses
    locking_times = defaultdict(list)
    for k, room in enumerate(rooms):
        for exam in exams:
            if room in exam_rooms[exam]:
                l = h.index(exam_times[exam])
                if l not in locking_times[k]:
                    locking_times[k].append(l)
                    
    if verbose: print "Locking times", sum( len(locking_times[k]) for k in range(len(rooms)) )
    
    Q, conflicts, K = read_conflicts(filename = "Conflicts/%s.csv" %anmelde_data, exams = exams, threshold = threshold)
    
    if verbose: print "Mean number of conflicts", np.mean([ len(conflicts[i]) for i, e in enumerate(exams)])
    if verbose: print "Percentage of conflicts", 100.*len(K)/(len(exams)**2)
    
    data = {}
    
    data['n'] = len(s)
    data['r'] = len(c)
    data['p'] = len(h)
    
    data['h'] = h
    data['s'] = s
    data['c'] = c
    data['Q'] = Q
    
    data['conflicts'] = conflicts
    data['locking_times'] = locking_times
    
    data['exam_names'] = exams
    data['exam_times'] = exam_times
    data['exam_rooms'] = exam_rooms
    data['room_names'] = rooms
    #data['campus_ids'] = campus_ids
    
    return data

if __name__ == "__main__":
    
    
    data = read_data(semester = "16S", threshold = 0, make_intersection=True, verbose=True, max_periods = 10)
    
    print data['n'], data['r'], data['p']
    print "KEYS:", [key for key in data]
    
    n = data['n']
    Q = data['Q']
    
    counter = 0
    conflicts = 0
    
    for i in range(n):
        for j in range(n):
            counter += 1
            if Q[i][j] == 1:
                conflicts += 1
    print "Conflict ratio:", conflicts * 1. / counter
    