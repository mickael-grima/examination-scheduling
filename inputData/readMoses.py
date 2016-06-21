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


def read_columns(datname, key, cols, sep=","):
    '''
    Read csv file and extract column names in cols.
    '''
    
    columns = defaultdict(dict)
    colnames = []
            
    with open("%sinputData/Data/%s"%(PROJECT_PATH, datname)) as csvfile:
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


def read_times():
    # "","PRFG.NUMMER","startHours","endHours","startDate","endDate"
    prfg = read_columns("prfg_times.csv", "PRFG.NUMMER", ["startHours", "endHours", "startDate", "endDate"], sep=",")

    startHours = prfg["startHours"]
    
    h = sorted(set(map(float, startHours.values())))

    exam_names = [e for e in startHours]
    exam_times = map(float, startHours.values())
    
    return h, exam_names, exam_times


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
    
    
    
    room_capacities = room_overview["Klausurplaetze_eng"]
    
    locking_times = defaultdict(list)
    capacity = defaultdict(int)
    campus_id = defaultdict(str)
    room_name = defaultdict(str)
    
    for k, room in enumerate(room_capacities):
        locking_times[k] = locking_times_unordered[room]
        capacity[k] = room_capacities[room]
        campus_id[k] = room_overview["ID_Campus"]
        room_name[k] = room
        
    print "Loading times and rooms: Correctness was not tested, but seems to work!"
    return capacity, locking_times, room_name, campus_id
    

def read_conflicts(exam_names, threshold = 0):
    #MODUL;T_NR;DATUM_T1;ANZ_STUD_MOD1;STUDIS_PRUEF1_GES;STUDIS_PRUEF1_ABGEMELDET;STUD_NICHT_ERSCHIENEN_PRUEF1;MODUL2;T_NR2;DATUM_T2;SEMESTER;ANZ_STUD_MOD2;STUDIS_PRUEF2_GES;STUDIS_PRUEF2_ABGEMELDET;STUD_NICHT_ERSCHIENEN_PRUEF2
    datname = "exam_conflicts.csv"
    Q = defaultdict(int)
    conflicts = defaultdict(list)
    students = defaultdict(int)
    colnames = []
    
    with open("%sinputData/Data/%s"%(PROJECT_PATH, datname)) as csvfile:
        for line in csvfile:
            line = re.sub('\"', '', line)
            line = re.sub('\n', '', line)
            line = re.split(';', line)
            
            if len(colnames) == 0:
                colnames = line
            else:
                ident1 = line[colnames.index("MODUL")]
                ident2 = line[colnames.index("MODUL2")]
                
                # convert idents to indices
                if ident1 in exam_names:
                    ident1 = exam_names.index(ident1)
                else:
                    continue
                if ident2 in exam_names:
                    ident2 = exam_names.index(ident2)
                else:
                    continue
                
                assert line[colnames.index("ANZ_STUD_MOD1")] == line[colnames.index("ANZ_STUD_MOD2")]
                
                n_conflicts = int(line[colnames.index("ANZ_STUD_MOD1")])
                
                if n_conflicts <= threshold:
                    continue
                
                # build Q matrix
                Q[ident1, ident2] = n_conflicts
                
                # add to conflicts
                conflicts[ident1].append(ident2)
                conflicts[ident2].append(ident1)
                
                if ident1 not in students:
                    students[ident1] = int(line[colnames.index("STUDIS_PRUEF1_GES")]) - int(line[colnames.index("STUDIS_PRUEF1_ABGEMELDET")])
                    
    for i in conflicts:
        conflicts[i] = sorted(set(conflicts[i]))
        
    return students.values(), conflicts, Q
    
    
def read_real_data(conflict_threshold = 0):

    h, exam_names, exam_times = read_times()
    c, locking_times, room_names, campus_ids = read_rooms(h)
    s, conflicts, Q = read_conflicts(exam_names, threshold = conflict_threshold)
    
    data = {}
    
    data['h'] = h
    data['c'] = c
    data['s'] = s
    data['Q'] = Q
    data['conflicts'] = conflicts
    data['locking_times'] = locking_times
    data['exam_names'] = exam_names
    data['exam_times'] = exam_times
    data['room_names'] = room_names
    data['campus_ids'] = campus_ids
    
    return data

if __name__ == "__main__":
    data = read_real_data()
    
    print "KEYS:", [key for key in data]
    