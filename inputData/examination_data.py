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
import random as rd

from inputData import tools as datatools
from model.data_format import force_data_format
import heuristics.tools as htools

def split_key(exam):
    ''' 
        Split the combined key into module and datum!
    '''
    match = re.search("\d{1,2}.\d{1,2}.\d{4}", exam)
    
    if match is None:
        return None, None
    
    datum = match.group()
    modul = re.sub("\s*%s" %datum, "", exam)
    
    if len(re.split("\/", datum)) != 3:
        return None, None
        
    return modul, datum


def keys_are_equal(exam1, exam2):
    '''
        Compare two keys for equality.
        If exams are close by less than 10 days, they are considered as equal.
    '''
    modul2, datum2 = split_key(exam2)
    if modul2 is None: return False
    
    dat2 = map(int, re.split("\/", datum2))
    
    return keys_are_equal_fast(exam1, modul2, dat2[0], dat2[1])
    

def keys_are_equal_fast(exam1, modul2, month2, day2):
    '''
        Compare two keys for equality. Use info of known key
        If exams are close by less than 10 days, they are considered as equal.
    '''
    modul1, datum1 = split_key(exam1)
    if modul1 is None: return False
    
    if modul1 != modul2: return False

    dat1 = map(int, re.split("\/", datum1))
    
    # If exams are close by less than 10 days, consider as equal
    if abs(dat1[0] - month2) <= 1 and abs(dat1[1] - day2) <= 30:
        return True
    else:
        return False


def read_columns(datname, key, cols, sep=","):
    '''
    Read csv file and extract data with column names in cols. Takes first value found!
    '''
    return datatools.read_csv("%sinputData/%s"%(PROJECT_PATH, datname), key, cols, sep=sep)


def read_result_times(semester):
    # read times from result file
    
    if semester == "15W":
        key = ["PRFG.NUMMER", "TERMIN"]
    else:
        key = "PRFG.NUMMER"
    # "","PRFG.NUMMER","startHours","endHours","startDate","endDate"
    prfg = read_columns("%s/prfg_times.csv" %semester, key, ["startHours", "endHours", "startDate", "endDate"], sep=",")

    startHours = prfg["startHours"]
    startDate = prfg["startDate"]
    
    exam_times = dict()
    for exam in startHours:
        exam_times[exam] = float(startHours[exam])
    
    return exam_times, startDate


def read_result_rooms(semester):
    # read rooms from result file
    
    # "","PRFG.NUMMER","startHours","endHours","startDate","endDate"
    
    cols = []
    for i in range(1, 10):
        cols.append("ORT_CODE_0%d" %i)
    for i in range(10, 31):
        cols.append("ORT_CODE_%d" %i)
        
    if semester == "15W":
        key = ["PRFG-NUMMER", "TERMIN"]
    else:
        key = "PRFG-NUMMER"
        
    prfg = read_columns("%s/Ergebnis_%s.csv" %(semester, semester), key, cols, sep=";")
    
    exam_rooms = defaultdict(set)
    for col in prfg:
        for exam in prfg[col]:
            exam_rooms[exam].add(prfg[col][exam])
    
    for exam in exam_rooms:
        exam_rooms[exam] = list(exam_rooms[exam])
        if '' in exam_rooms[exam]:
            exam_rooms[exam].remove('')
    
    exam_rooms = { exam: exam_rooms[exam] for exam in exam_rooms if len(exam_rooms[exam]) > 0 }
    
    return exam_rooms


def read_rooms():
    
    # Name;Name_lang;Sitzplaetze;Klausurplaetze_eng;ID_Raum;ID_Gebaeude;Gebaeude;ID_Raumgruppe;ID_Campus;Campus
    room_overview = read_columns("Data/Raumuebersicht.csv", "ID_Raum", ["Klausurplaetze_eng", "ID_Campus"], sep=";")
        
    return room_overview["Klausurplaetze_eng"], room_overview["ID_Campus"]
    
def read_rooms_zusatz():
    
    # Name;Name_lang;Sitzplaetze;Klausurplaetze_eng;ID_Raum;ID_Gebaeude;Gebaeude;ID_Raumgruppe;ID_Campus;Campus
    room_overview = read_columns("Data/Raumuebersicht_Zusatz.csv", "ID_Raum", ["Klausurplaetze_eng", "ID_Campus"], sep=";")
    
    return room_overview["Klausurplaetze_eng"], room_overview["ID_Campus"]
    
    
    
def read_locked_rooms(semester, rooms, h):
    
    # "","ID_RAUM","startTime","endTime","startDate","endDate"
    if semester == "15W":
        key = "RAUM_CODE"
        full_key = ["RAUM_CODE", "startDate", "endDate"]
    else:
        key = "ID_RAUM"
        full_key = "ID_RAUM"
    
    room_data = read_columns("%s/raum_sperren.csv" %semester, full_key, [key, "startTime", "endTime", "startDate","endDate"], sep=",")
    
    room_ids = room_data[key]
    start_hours = room_data["startTime"]
    end_hours = room_data["endTime"]
    
    # save locking times in dictionary
    room_locking_times = defaultdict(list)
    
    # find time indices for which rooms are locked
    for key in start_hours:
        room = room_ids[key]
        if room not in rooms:
        #    print "ROOM NOT USED!"
            continue
        else:
            k = rooms.index(room)
        for i in range(len(h)-1):
            # determine position of locking start
            if float(start_hours[key]) > h[i] and float(start_hours[key]) <= h[i+1]:
                j = i+1
                
                # search for position of locking end
                while( j < len(h) ):
                    
                    if float(end_hours[key]) < h[j]:
                        break;
                    # on the way insert locking times to dict
                    if j not in room_locking_times[k]:
                        room_locking_times[k].append(j)
                    j += 1
    return room_locking_times


def read_teilnehmer(semester):
    #LV_NUMMER;LV_TITEL;LV_SEMESTER;DATUM;ANZ_TEILNEHMER
    
    filename = "Teilnehmer/Teilnehmer_15.csv"
    
    if semester == "15W":
        key = ["LV_NUMMER", "DATUM"]
    else:
        key = "LV_NUMMER"
        
    students = read_columns(filename, key, ["LV_SEMESTER", "ANZ_TEILNEHMER"], sep=";")
    
    
    exam_students = dict()
    for exam in students["ANZ_TEILNEHMER"]:
        
        if students["LV_SEMESTER"][exam] != semester:
            continue

        # IN0039;Praktikum: Game Engine Design;15S;24/07/2015;195
        # split key, we need to rearrange date
        modul, datum = split_key(exam)
        
        if modul is None:
            #print "ERROR!", exam
            continue
        
        datum = re.split("\/", datum)
        datum = "%d/%d/%s" %(int(datum[1]), int(datum[0]), datum[2])
        
        key = "%s %s" %(modul, datum)
        
        if key not in exam_students:
            exam_students[key] = int(students["ANZ_TEILNEHMER"][exam])
        else:
            exam_students[key] += int(students["ANZ_TEILNEHMER"][exam])
            
    return exam_students
    
    
def read_students(semester):
    #MODUL;T_NR;DATUM_T1;ANZ_STUD_MOD1;STUDIS_PRUEF1_GES;STUDIS_PRUEF1_ABGEMELDET;STUD_NICHT_ERSCHIENEN_PRUEF1;MODUL2;T_NR2;DATUM_T2;SEMESTER;ANZ_STUD_MOD2;STUDIS_PRUEF2_GES;STUDIS_PRUEF2_ABGEMELDET;STUD_NICHT_ERSCHIENEN_PRUEF2
    
    # Name;Name_lang;Sitzplaetze;Klausurplaetze_eng;ID_Raum;ID_Gebaeude;Gebaeude;ID_Raumgruppe;ID_Campus;Campus
    
    anmelde_data = semester
    if semester == "16S":
        anmelde_data = "15S"
    
    filename = "Conflicts/%s.csv" %anmelde_data
    
    if semester == "15W":
        key1 = ["MODUL", "DATUM_T1"]
        key2 = ["MODUL2", "DATUM_T2"]
    else:
        key1 = "MODUL"
        key2 = "MODUL2"
        
    students_abs_1 = read_columns(filename, key1, ["STUDIS_PRUEF1_GES", "STUDIS_PRUEF1_ABGEMELDET", "STUD_NICHT_ERSCHIENEN_PRUEF1"], sep=";")
    
    students_abs_2 = read_columns(filename, key2, ["STUDIS_PRUEF2_GES", "STUDIS_PRUEF2_ABGEMELDET", "STUD_NICHT_ERSCHIENEN_PRUEF2"], sep=";")
    
    exam_students = dict()
    for exam in students_abs_1["STUDIS_PRUEF1_GES"]:
        exam_students[exam] = int(students_abs_1["STUDIS_PRUEF1_GES"][exam])# - int(students_abs_1["STUDIS_PRUEF1_ABGEMELDET"][exam])
        if exam_students[exam] < 0:
            exam_students[exam] = int(students_abs_2["STUDIS_PRUEF2_GES"][exam])
        
    
    for exam in students_abs_2["STUDIS_PRUEF2_GES"]:
        exam_students[exam] = int(students_abs_2["STUDIS_PRUEF2_GES"][exam])# - int(students_abs_2["STUDIS_PRUEF2_ABGEMELDET"][exam])
        if exam_students[exam] < 0:
            exam_students[exam] = int(students_abs_2["STUDIS_PRUEF2_GES"][exam])
            
    return exam_students
    
   

def search_for_key_in_exams(key, exams):
    '''
        Get the key in list. If it is there, take it, otherwise compare the keys!
    '''
    if key in exams:
        return key
    
    modul, datum = split_key(key)
    if modul is None: return None
    dat = map(int, re.split("\/", datum))
    
    for exam in exams:
        if modul not in exam:
            continue
        if keys_are_equal_fast(exam, modul, dat[0], dat[1]):
            return exam
    return None


def match_keys(exam_students, result_times):
    '''
        Some exams in MOSES are moved by hand again. Those are usually quite close to the planned one.
        Using this method, we can find student numbers for those exams!
    '''
    for exam in result_times:
        key = search_for_key_in_exams(exam, exam_students)
        if key is None:
            continue
        exam_students[exam] = exam_students[key]
    return exam_students


def read_conflicts(semester, exams = None, threshold = 0):
    #MODUL;T_NR;DATUM_T1;ANZ_STUD_MOD1;STUDIS_PRUEF1_GES;STUDIS_PRUEF1_ABGEMELDET;STUD_NICHT_ERSCHIENEN_PRUEF1;MODUL2;T_NR2;DATUM_T2;SEMESTER;ANZ_STUD_MOD2;STUDIS_PRUEF2_GES;STUDIS_PRUEF2_ABGEMELDET;STUD_NICHT_ERSCHIENEN_PRUEF2
    
    anmelde_data = semester
    if semester == "16S":
        anmelde_data = "15S"
    filename = "Conflicts/%s.csv" %anmelde_data
    
    Q_abs = defaultdict(int)
    colnames = []
    unresolved_idents = []
    ident_matches = dict()
    
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
                if semester == "15W":
                    ident1 = ident1 + " " + line[colnames.index("DATUM_T1")]
                    ident2 = ident2 + " " + line[colnames.index("DATUM_T2")]
                    
                assert line[colnames.index("ANZ_STUD_MOD1")] == line[colnames.index("ANZ_STUD_MOD2")]
                
                # get conflicts
                n_conflicts = int(line[colnames.index("ANZ_STUD_MOD1")])
                
                if n_conflicts <= threshold:
                    continue
                
                # make sure the exam is used for our solution
                if exams is not None and ident1 not in exams:
                    
                    if ident1 not in ident_matches:
                        match1 = search_for_key_in_exams(ident1, exams)
                        if match1 is None:
                            continue
                        ident_matches[ident1] = match1
                    
                    ident1 = ident_matches[ident1]
                    
                # make sure the exam is used for our solution
                if exams is not None and ident2 not in exams:
                    
                    if ident2 not in ident_matches:
                        match2 = search_for_key_in_exams(ident2, exams)
                        if match2 is None:
                            continue
                        ident_matches[ident2] = match2
                    
                    ident2 = ident_matches[ident2]
                    
                # build Q matrix
                Q_abs[ident1, ident2] = n_conflicts
                    
    n = len(exams)
    Q = [[0 for i in range(n)] for i in range(n)]
    K = defaultdict(int)
    conflicts = defaultdict(list)
    
    for i, e1 in enumerate(exams):
        for j, e2 in enumerate(exams):
            if Q_abs[e1, e2] > 0:
                Q[i][j] = 1
                Q[j][i] = 1
                if j not in conflicts[i]:
                    conflicts[i].append(j)
                if i not in conflicts[j]:
                    conflicts[j].append(i)
                
                K[i,j] = Q_abs[e1, e2]
                if (e2, e1) in Q_abs:
                    K[i,j] = max(K[i,j], Q_abs[e2, e1])
                K[j,i] = K[i,j]
              
    return Q, conflicts, K
    
    
def get_duplicate_exams(exams, exam_rooms, exam_times):
    
    '''
        Some exams are in the same room in the same time slot. This happens because we define the slots differently.
        The method returns those exams which are to be dropped!
    '''
    
    duplicates = defaultdict(set)
    for exam in exams:
        for exam2 in exams:
            if exam2 in duplicates[exam] or exam in duplicates[exam2]:
                continue
            if exam_times[exam] == exam_times[exam2]:
                if any( room in exam_rooms[exam2] for room in exam_rooms[exam] ):
                    #print exam, exam2, exam_rooms[exam], exam_rooms[exam2]
                    duplicates[exam].add(exam2)
    
    # throw out those duplicate exams with the least number of rooms
    drop_exams = set()
    for exam in duplicates:
        dupl = sorted(duplicates[exam])
        if len(dupl) > 1:
            n_rooms = [ len(exam_rooms[exam2]) for exam2 in dupl ]
            max_rooms = n_rooms.index(max(n_rooms))
            for j in range(len(n_rooms)):
                if j != max_rooms:
                    drop_exams.add(dupl[j])
    return drop_exams

    
def get_weeks(h):
    '''
        Returns an heuristic for when a week starts and when it ends.
        Data structure is a dictionary for week number and a list with [begin, end].
    '''
    
    distances = defaultdict(int)
    for i in range(1, len(h)):
        d = h[i] - h[i-1]
        distances[d] += 1
    #for w in distances:
        #print w, distances[w]
        
    D = [d for d in distances][2]
    
    counter = 0
    weeks = defaultdict(list)
    for i in range(1, len(h)):
        weeks[counter] += [h[i-1]]
        if h[i] - h[i-1] >= D:
            counter += 1
        
        # APPEND REST
        if i == len(h) - 1:
            weeks[counter] += [h[i]]
        
    return weeks


def get_faculty_weeks(exam_times, week_slots, verbose = False):
    '''
        For each faculty get lists of weeks where exams are held
    '''
    
    # get faculties
    exam_faculty = {exam: re.search("\D+\d", exam).group()[0:-1] for exam in exam_times }
    faculties = sorted(set(exam_faculty.values()))
    if verbose: print faculties
    
    
    ## old: do it for each slot
    #faculty_periods = defaultdict(list)
    #for exam in exams:
        #for faculty in faculties:
            #if re.match(faculty, exam) is not None:
                #faculty_periods[faculty].append(exam_times[exam])
                #break
    
    # get examination periods for each faculty in weeks:
    faculty_periods = defaultdict(list)
    for exam in exam_times:
        faculty = exam_faculty[exam]
        for week in week_slots:
            if week not in faculty_periods[faculty] and exam_times[exam] in week_slots[week]:
                faculty_periods[faculty].append(week)
                break
    
    return faculty_periods


def get_possible_exam_weeks(exam_times, verbose=False, relax_total = True, math_only = False):
    '''
        For each exam get the time slots which can be used to schedule this exam!
    '''
    
    # get time slots of weeks
    week_slots = get_weeks(sorted(set(exam_times.values())))
    #if verbose:
        #for w in week_slots:
            #print w, week_slots[w]
        
    # get examination periods for each faculty in weeks:
    faculty_weeks = get_faculty_weeks(exam_times, week_slots, verbose = verbose)
    #if verbose:
    #for f in faculty_weeks:
        #print f, sorted(faculty_weeks[f])

    faculty_weeks['ME'] = [3]
    faculty_weeks['CH'] = [0, 1, 2, 4, 6, 7, 8]
    faculty_weeks['MA'] = [0, 1, 2, 3, 4, 7, 8]
    faculty_weeks['ED'] = [0]
    faculty_weeks['SP'] = [0, 1, 3, 8]
    faculty_weeks['BV'] = [2, 3, 4]
    faculty_weeks['WI'] = [0, 1, 2, 4, 6]
    faculty_weeks['MW'] = [0, 1, 2, 3, 4, 6, 7, 8]
    faculty_weeks['BGU'] = [0, 1, 2, 3, 4, 5]
    faculty_weeks['IN'] = [0, 1, 2, 4, 7, 8]
    faculty_weeks['EI'] = [0, 1, 2, 3, 4, 7, 8]
    faculty_weeks['PH'] = [0, 1, 2, 3, 6, 7, 8]
    faculty_weeks['SG'] = [0, 1, 2, 8]
    faculty_weeks['WZ'] = [0, 1, 2, 3, 4, 6, 7, 8]

    faculty_weeks['ME'] = [0, 1, 2, 3, 4]
    faculty_weeks['CH'] = [0, 1, 2, 3, 4, 6, 7, 8]
    faculty_weeks['MA'] = [0, 1, 2, 3, 4, 6, 7, 8]
    faculty_weeks['ED'] = [0, 1, 2, 3, 4]
    faculty_weeks['SP'] = [0, 1, 3, 3, 4, 6, 7, 8]
    faculty_weeks['BV'] = [0, 1, 2, 3, 4]
    faculty_weeks['WI'] = [0, 1, 2, 3, 4, 6, 7, 8]
    faculty_weeks['MW'] = [0, 1, 2, 3, 4, 6, 7, 8]
    faculty_weeks['BGU'] = [0, 1, 2, 3, 4, 5]
    faculty_weeks['IN'] = [0, 1, 2, 3, 4, 6, 7, 8]
    faculty_weeks['EI'] = [0, 1, 2, 3, 4, 6, 7, 8]
    faculty_weeks['PH'] = [0, 1, 2, 3, 4, 6, 7, 8]
    faculty_weeks['SG'] = [0, 1, 2, 3, 4, 6, 7, 8]
    faculty_weeks['WZ'] = [0, 1, 2, 3, 4, 6, 7, 8]

    if relax_total:
        faculty_weeks['ME'] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        faculty_weeks['CH'] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        faculty_weeks['MA'] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        faculty_weeks['ED'] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        faculty_weeks['SP'] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        faculty_weeks['BV'] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        faculty_weeks['WI'] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        faculty_weeks['MW'] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        faculty_weeks['BGU'] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        faculty_weeks['IN'] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        faculty_weeks['EI'] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        faculty_weeks['PH'] = [0, 1, 2, 3, 4, 5, 6, 7, 8] 
        faculty_weeks['SG'] = [0, 1, 2, 3, 4, 5, 6, 7, 8] 
        faculty_weeks['WZ'] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    
    
    faculty_black_list = []#'ME', 'ED', 'SP', 'BV', 'SG']
    
    if math_only:
        faculty_weeks['MA'] = [0, 1, 2]
        faculty_black_list = [ faculty for faculty in faculty_weeks if faculty != "MA" ]
        
    
    for f in faculty_weeks:
        if f in faculty_black_list:
            continue
        print f, sorted(faculty_weeks[f])
    
    # get faculty of each exam
    exam_faculty = { exam: re.search("\D+\d", exam).group()[0:-1] for exam in exam_times }
    
    # extract the weeks of each exam
    debug_name = 'CH0127'
    debug_name = 'XYZNODEBUG'
    
    exam_weeks = defaultdict(list)
    for exam in exam_times:

        if debug_name in exam:
            print exam, exam_times[exam]
            
        faculty = exam_faculty[exam]

        # dont do exams in blacklist
        if faculty in faculty_black_list:
            continue
        
        # determine week of exam:
        w = 0
        while w < len(week_slots):
            if exam_times[exam] in week_slots[w]:
                break
            else: 
                w += 1
           
        # only consider exam which has right week (feasibility)
        if w in faculty_weeks[faculty]:
            exam_weeks[exam].append(w)
        else:
            continue
        
        if debug_name in exam:
            print exam, exam_weeks[exam]
            
        # for all connecting weeks to the left, add slots
        w2 = w-1
        while w2 >= 0:
            if w2 in faculty_weeks[faculty]:
                exam_weeks[exam].append(w2)
            else:
                break
            w2 -= 1
        
        if debug_name in exam:
            print exam, exam_weeks[exam]
        # for all connecting weeks to the right, add slots
        w3 = w+1
        while w3 <= len(week_slots):
            if w3 in faculty_weeks[faculty]:
                exam_weeks[exam].append(w3)
            else:
                break
            w3 += 1
        
        # sort list
        exam_weeks[exam] = sorted(exam_weeks[exam])
        
        if debug_name in exam:
            print exam, exam_weeks[exam]
            
    return exam_weeks, week_slots
    
def get_exam_slots(result_times, verbose=False, math_only=False,relax_total=True):
    '''
        Given the calendar weeks for each exam, give the corresponing slots.
        All exams with more or equal to week_threshold weeks are considered
    '''

    exam_weeks, week_slots = get_possible_exam_weeks(result_times, verbose=verbose, math_only = math_only,relax_total = relax_total)

    #for exam in exam_weeks:
        #exam_weeks[exam].append(max(exam_weeks[exam])+1)
    
    exam_slots = defaultdict(list)
    for exam in exam_weeks:
        
        slots = list()
        
        for week in exam_weeks[exam]:
            
            #if week in [8,9]:
                #continue
            
            slots += week_slots[week]
        slots = sorted(set(slots))
        
        if len(slots) >= 5:
            exam_slots[exam] = slots
            if result_times[exam] not in slots:
                print "BUG: Time not in slots!", result_times[exam]
                exam_slots[exam] = sorted(exam_slots[exam] + [result_times[exam]])
        #else:
            #print exam, len(exam_slots[exam])
    
    return exam_slots, exam_weeks
    
    
def get_exam_rooms(result_rooms, room_campus_id):
    '''
        For each exam get the rooms which are located at the campus the exam is to be held.
    '''
    all_rooms = set([room for exam in result_rooms for room in result_rooms[exam]])
            
    exam_rooms = defaultdict(list)
    for exam in result_rooms:
        camps = set([ room_campus_id[room] for room in result_rooms[exam] if room in room_campus_id ])
        for room in all_rooms:
            if room in room_campus_id and room_campus_id[room] in camps:
                exam_rooms[exam].append(room)
    
    return exam_rooms
    
    
@force_data_format
def read_data(semester = "16S", threshold = 0, pre_year_data = False, make_intersection=True, verbose=False, max_periods = None, max_exams = None, relax_total = True, math_only = False):
    '''
        @ Param make_intersection: Use exams which are in tumonline AND in szenarioergebnis
    '''
    
    #semester = "15W"
    assert semester in ["15W"], "Wir verwenden nur Ergebnisse für Winder 15!"
    assert max_periods is None, "WARNING: max_periods is not implemented any more!"
    assert not pre_year_data, "Pre year data is currently turned off!"
    
    print "Semester:", semester
    
    # load times from szenarioergebnis
    result_times, result_dates = read_result_times(semester)
    
    # load room results from szenarioergebnis
    result_rooms = read_result_rooms(semester)
    
    # load room capacities
    room_capacity, room_campus_id = read_rooms()
    
    # read zusatzinformation
    rc2, rci2 = read_rooms_zusatz()
    room_capacity.update(rc2)
    room_campus_id.update(rci2)
    
    # load number of students registered for each exam
    exam_students = read_teilnehmer(semester)
    
    # enrich student data by hand changed exams
    exam_students = match_keys(exam_students, result_times)
    
    if verbose: print "Exams which we cannot find data for:", len(sorted([exam for exam in result_times if exam not in exam_students]))
    
    # get exams in the MOSES result
    exams = [exam for exam in result_times]
    if verbose: print "Number of exams", len(exams)
    
    # get exams for which we have student data
    exams = [exam for exam in exams if exam in exam_students and exam_students[exam] > 0]
    if verbose: print "Number of exams", len(exams)
    
    # filter all exams for which we know the room
    exams = [exam for exam in exams if exam in result_rooms and len(result_rooms[exam]) > 0]
    if verbose: print "Number of exams", len(exams)
    
    # filter all exams for which we have room data
    exams = [exam for exam in exams if all(room in room_capacity for room in result_rooms[exam])]
    if verbose: print "Number of exams", len(exams)
    
    # detect duplicates, i.e. exams at the same time slot in the same room. Drop smaller ones
    drop_exams = get_duplicate_exams(exams, result_rooms, result_times)
    exams = [ exam for exam in exams if exam not in drop_exams ]
    if verbose: print "Drop duplicates", len(drop_exams)
    if verbose: print "Number of exams", len(exams)
    
    # For each exam get all rooms at the eligible campus
    exam_rooms = get_exam_rooms(result_rooms, room_campus_id)
    
    # for each exam determine the possible slots according to examination periods
    exam_slots, exam_weeks = get_exam_slots(result_times, relax_total = relax_total, math_only = math_only, verbose=verbose)
    
    # filter exams which are considered with examination period
    exams = sorted([ exam for exam in exams if exam in exam_slots ])
    
    # filter impossible exams (found by hand)
    impossibles = ['BV000001 2/26/2016', 'CH0115 2/17/2016', 'IN0015 2/13/2016', 'IN0019 2/11/2016', 'MA9301 2/24/2016', 'MA9302 2/18/2016', 'MA9305 3/1/2016', 'MA9711 2/8/2016', 'MW0084 3/8/2016', 'MW0104 3/22/2016', 'MW1108 3/1/2016', 'MW1911 2/23/2016', 'MW2021 3/11/2016', 'MW2023 2/25/2016', 'PH0001 4/7/2016', 'PH9009 2/15/2016', 'WI000021 2/15/2016', 'WI000027 2/22/2016', 'WI001056 2/12/2016', 'BV000013 3/4/2016', 'CH1102 2/18/2016', 'IN0015 4/5/2016', 'IN2062 2/8/2016', 'MA9409 4/4/2016', 'MA9413 2/23/2016', 'MW0102 3/11/2016', 'MW1919 3/2/2016', 'MW1937-1 3/3/2016', 'MW2015 2/23/2016', 'PH0003 2/18/2016', 'SG120020 2/13/2016', 'SG160013 2/12/2016', 'WI000178 2/19/2016', 'WI000219 2/9/2016', 'WI000820 2/10/2016', 'CH0128 4/1/2016', 'MA9201 2/19/2016', 'MA9202 4/5/2016', 'MA9511 3/8/2016', 'MW1586 3/21/2016', 'WI001059 2/18/2016', 'MA9202 2/9/2016', 'MA9517 3/9/2016', 'MW0612 3/29/2016', 'MW1921 2/18/2016', 'MW1939-1 3/8/2016', 'PH0001 2/11/2016', 'SG120022 2/17/2016', 'MA9411 2/18/2016', 'MW1980 2/9/2016', 'MW2129 2/29/2016', 'SG110200 2/26/2016', 'SG120024 2/19/2016', 'WI000275 2/22/2016', 'WI000728 2/11/2016', 'BGU55027 3/1/2016', 'EI0611 2/8/2016', 'EI1182 3/10/2016', 'IN0008 2/24/2016', 'IN0009 2/22/2016', 'MA9201 3/31/2016', 'MW1938-1 2/26/2016', 'PH9009 3/29/2016', 'WI000729 2/11/2016', 'IN0021 2/22/2016', 'MW1694 3/2/2016', 'SG110230 2/25/2016', 'BGU51017 2/29/2016']
    exams = [exam for exam in exams if exam not in impossibles]
    
    if verbose: print "Drop the impossible", len(impossibles)
    if verbose: print "Number of exams", len(exams)
    
    # make subproblem
    if type(max_exams) == int:
        rd.shuffle(exams)
        exams = sorted(exams[0:max_exams])
        
    exams = sorted(exams)
    
    # get names of all used rooms
    rooms = sorted(set([ room for exam in exams for room in exam_rooms[exam] ]))
    
    # get all usable slots
    h = sorted(set([ slot for exam in exams for slot in exam_slots[exam] ]))
    s = [exam_students[exam] for exam in exams]
    c = [int(room_capacity[room]) for room in rooms]
    
    if verbose: print "Number of exams", len(exams)
    if verbose: print "Number of rooms:", len(rooms)
    if verbose: print "Number of periods", len(h)
    
    #print "RELAXING EXAM SLOTS!!"
    #exam_slots = {exam: h for exam in exams}
    
    # finished loading basic data. Now everything is about format!
    # WARNING: DO NOT EDIT EXAMS AFTER THIS STEP!
    
    # convert to index notation
    exam_rooms_index = defaultdict(list)
    exam_slots_index = defaultdict(list)
    for exam in exams:
        
        exam_slots_index[exam] = [ h.index(slot) for slot in exam_slots[exam] ]
        exam_rooms_index[exam] = [ rooms.index(room) for room in exam_rooms[exam] ]
        
    # Load locking rooms from table
    locking_times = read_locked_rooms(semester, rooms, h)
    
    # If we dont plan the exam then we lock the room.
    for k, room in enumerate(rooms):
        for exam in [e for e in result_times if e not in exams]:
            if exam in result_rooms and room in result_rooms[exam] and result_times[exam] in h:
                l = h.index(result_times[exam])
                if l not in locking_times[k]:
                    locking_times[k].append(l)

    if verbose: print "Locking times", sum( len(locking_times[k]) for k in range(len(rooms)) )
    
    # remove locking times for all exams we found and which are planned in moses illegally
    for i, exam in enumerate(exams):
        if result_times[exam] in h:
            l = h.index(result_times[exam])
            for k in exam_rooms_index[exam]:
                if l in locking_times[k]:
                    locking_times[k].remove(l)
        
    if verbose: print "Locking times", sum( len(locking_times[k]) for k in range(len(rooms)) )
     
     
    # read conflict data from tumonline
    if verbose: print "Read conflicts..."
    Q, conflicts, K = read_conflicts(semester, exams = exams, threshold = threshold)
    if verbose: print "Mean number of conflicts", np.mean([ len(conflicts[i]) for i, e in enumerate(exams)])
    
    
    # convert to list of lists 
    exam_slots_list = []
    exam_slots_index_list = []
    exam_rooms_list = []
    exam_rooms_index_list = []
    exam_weeks_list = []
    
    for exam in exams:
        exam_slots_list.append(exam_slots[exam])
        exam_slots_index_list.append(exam_slots_index[exam])
        exam_rooms_list.append(exam_rooms[exam])
        exam_rooms_index_list.append(exam_rooms_index[exam])
        exam_weeks_list.append(exam_weeks[exam])
        
    exam_rooms_list = exam_rooms_index_list
    
    
    data = {}
    
    data['n'] = len(s)
    data['r'] = len(c)
    data['p'] = len(h)
    
    data['h'] = h
    data['s'] = s
    data['c'] = c
    
    data['conflicts'] = conflicts
    data['locking_times'] = locking_times
    
    data['data_version'] = semester
    data['exam_names'] = exams
    data['exam_slots'] = exam_slots_list
    data['exam_slots_index'] = exam_slots_index_list
    data['exam_rooms'] = exam_rooms_list
    data['exam_rooms_index'] = exam_rooms_index_list
    data['exam_weeks'] = exam_weeks_list
    
    data['result_times'] = result_times
    data['result_dates'] = result_dates
    data['result_rooms'] = result_rooms
    data['room_names'] = rooms
    
    return data


def load_data(dataset = "1", threshold = 0, verbose = False):

    assert dataset in ["1", "2", "3"], "We only have three different verisons of the data set"
    
    print "Loading data set", dataset
    
    if dataset == "1":
        # all exams relaxed
        data = read_data(semester = "15W", threshold = threshold, relax_total=True, math_only = False, verbose = verbose)
    elif dataset == "2":
        # all exams with time constraints
        data = read_data(semester = "15W", threshold = threshold, relax_total=False, math_only = False, verbose = verbose)
    elif dataset == "3":
        # math exams with time constraints only
        data = read_data(semester = "15W", threshold = threshold, relax_total=False, math_only = True, verbose = verbose)
    
    #data['similar_periods'] = htools.get_similar_periods(data) # not necessary since we have exam_slots
    return data
    

if __name__ == "__main__":
    
    data = load_data(dataset = "2", threshold = 0, verbose = True)
    
        
    print "n, r, p"
    print data['n'], data['r'], data['p']
    print "KEYS:", [key for key in data]
    
    n = data['n']
    Q = data['Q']
    conflicts = data['conflicts']
    exam_names = data['exam_names']
    
    #print data['exam_slots']
    counter = 0
    conflicts = 0
    
    for i in range(n):
        for j in range(n):
            counter += 1
            if Q[i][j] == 1:
                conflicts += 1
    print "Conflict ratio:", conflicts * 1. / counter