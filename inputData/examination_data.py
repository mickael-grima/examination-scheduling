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
    Read csv file and extract column names in cols.
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
                    if name in cols:
                        columns[name][ident] = line[i]
                    
    return columns


def read_times(semester):
    # "","PRFG.NUMMER","startHours","endHours","startDate","endDate"
    prfg = read_columns("%s/prfg_times.csv" %semester, "PRFG.NUMMER", ["startHours", "endHours", "startDate", "endDate"], sep=",")

    startHours = prfg["startHours"]
    
    h = sorted(set(map(float, startHours.values())))

    exam_names = [e for e in startHours]
    exam_times = {}
    for exam in startHours:
        exam_times[exam] = float(startHours[exam])
    
    return h, exam_names, exam_times


def read_result_rooms(filename):
    # "","PRFG.NUMMER","startHours","endHours","startDate","endDate"
    
    cols = []
    for i in range(1, 10):
        cols.append("ORT_CODE_0%d" %i)
    for i in range(10, 31):
        cols.append("ORT_CODE_%d" %i)
        
    prfg = read_columns(filename, "PRFG-NUMMER", cols, sep=";")
    
    exam_rooms = defaultdict(set)
    for col in prfg:
        for exam in prfg[col]:
            exam_rooms[exam].add(prfg[col][exam])
    
    for exam in exam_rooms:
        exam_rooms[exam] = list(exam_rooms[exam])
        if '' in exam_rooms[exam]:
            exam_rooms[exam].remove('')
    return exam_rooms



def read_rooms(h):
    
    # Name;Name_lang;Sitzplaetze;Klausurplaetze_eng;ID_Raum;ID_Gebaeude;Gebaeude;ID_Raumgruppe;ID_Campus;Campus
    room_overview = read_columns("Raumuebersicht.csv", "ID_Raum", ["Klausurplaetze_eng", "ID_Campus"], sep=";")

    # "","ID_RAUM","startTime","endTime","startDate","endDate"
    rooms = read_columns("raum_sperren.csv", "ID_RAUM", ["startTime", "endTime", "startDate","endDate"], sep=",")

    start_hours = rooms["startTime"]
    end_hours = rooms["endTime"]
    
    # save locking times in dictionary
    locking_times_unordered = defaultdict(list)
    
    # find time indices for which rooms are locked
    for room in start_hours:
        for i in range(len(h)-1):
            # determine position of locking start
            if start_hours[room] >= h[i] and start_hours[room] <= h[i+1]:
                #print "found a locked room!"
                j = i
                # search for position of locking end
                while( j < len(h) - 1 ):
                    if end_hours[room] < h[j]:
                        break;
                    # on the way insert locking times to dict
                    locking_times_unordered[room].append(j)
                    j += 1
    
    
    locking_times = defaultdict(list)
    capacity = defaultdict(int)
    campus_id = defaultdict(str)
    room_name = defaultdict(str)
    
    for k, room in enumerate(room_overview["Klausurplaetze_eng"]):
        locking_times[k] = locking_times_unordered[room]
        capacity[k] = room_overview["Klausurplaetze_eng"][room]
        campus_id[k] = room_overview["ID_Campus"]
        room_name[k] = room
        
    return capacity, locking_times, room_name, campus_id
    

def read_conflicts(filename = "exam_conflicts_15S.csv", exam_names = None, threshold = 0):
    #MODUL;T_NR;DATUM_T1;ANZ_STUD_MOD1;STUDIS_PRUEF1_GES;STUDIS_PRUEF1_ABGEMELDET;STUD_NICHT_ERSCHIENEN_PRUEF1;MODUL2;T_NR2;DATUM_T2;SEMESTER;ANZ_STUD_MOD2;STUDIS_PRUEF2_GES;STUDIS_PRUEF2_ABGEMELDET;STUD_NICHT_ERSCHIENEN_PRUEF2
    students = defaultdict(int)
    Q_abs = defaultdict(int)
    colnames = []
    
    with open("%sinputData/Data/%s"%(PROJECT_PATH, filename)) as csvfile:
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
                if exam_names is not None and ident1 not in exam_names:
                    continue
                if exam_names is not None and ident2 not in exam_names:
                    continue
                
                assert line[colnames.index("ANZ_STUD_MOD1")] == line[colnames.index("ANZ_STUD_MOD2")]
                
                # save student numbers
                if ident1 not in students:
                    students[ident1] = int(line[colnames.index("STUDIS_PRUEF1_GES")]) - int(line[colnames.index("STUDIS_PRUEF1_ABGEMELDET")])
                if ident2 not in students:
                    students[ident2] = int(line[colnames.index("STUDIS_PRUEF2_GES")]) - int(line[colnames.index("STUDIS_PRUEF2_ABGEMELDET")])
                    
                #calculate conflicts
                n_conflicts = int(line[colnames.index("ANZ_STUD_MOD1")])
                
                # build Q matrix
                if n_conflicts > threshold:
                    Q_abs[ident1, ident2] = n_conflicts
                
                
    # only use exams for which we have data!
    s = []
    names = []
    
    # make sure only names with information are used
    for i, name in enumerate(students):
        s.append(students[name])
        names.append(name)
        
    #print [n for n in exam_names if n in names]
    
    n = len(s)
    Q = [[0 for i in range(n)] for i in range(n)]
    conflicts = defaultdict(list)
    
    # build std conflicts matrix
    for ident1, ident2 in Q_abs:
        if ident1 in students and ident2 in students:
            i = names.index(ident1)
            j = names.index(ident2)
            Q[i][j] = 1 * (Q_abs > 0)
            Q[j][i] = 1 * (Q_abs > 0)
            
    return s, Q, names
    
@force_data_format
def read_data(semester = "W15", threshold = 0, make_intersection=True, verbose=False, max_periods=None):
    '''
        @ Param make_intersection: Use exams which are in tumonline AND in szenarioergebnis
    '''
    #print "Loading data: Data needs verification!"
    
    
    # load times from szenarioergebnis
    h, exam_names, exam_times = read_times(semester)
    
    if max_periods is not None:
        h = h[0:max_periods]
        # TODO: WARNING: exam times not valuable any more
    
    # load room results from szenarioergebnis
    exam_rooms = read_result_rooms("%s/Ergebnis_%s.csv" %(semester, semester))
    
    if verbose: print "Moses exams:", len(exam_names)
    
    
    
    # load locking rooms
    c, locking_times, room_names, campus_ids = read_rooms(h)
    
    # consider all exams in tumOnline
    if not make_intersection:
        exam_names = None
        
    s, Q, exam_names = read_conflicts(exam_names = exam_names, threshold = threshold)
    
    if verbose: print "Exams used:", len(exam_names)
    
    assert len(c) == len(room_names)
    assert len(exam_names) == len(s)
   
    data = {}
    
    data['n'] = len(s)
    data['r'] = len(c)
    data['p'] = len(h)
    
    data['h'] = h
    data['c'] = c
    data['s'] = s
    data['Q'] = Q
    
    data['locking_times'] = locking_times
    
    data['exam_names'] = exam_names
    data['exam_times'] = exam_times
    data['exam_rooms'] = exam_rooms
    data['room_names'] = room_names
    data['campus_ids'] = campus_ids
    
    return data

if __name__ == "__main__":
    
    
    data = read_data(threshold = 0, make_intersection=True, verbose=True, max_periods = 10)
    
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
    