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

rows = defaultdict(list)
colnames = list()

with open("%sinput/Data/SzenarioergebnisSoSe2016.csv"%PROJECT_PATH) as ergebnis:
    for line in ergebnis:
        line = re.split(';', line)
        prfgnbr = line[0]
        line.pop(0)
        if re.match('.*PRFG-NUMMER.*', prfgnbr):
            colnames = line
        else:
            rows[prfgnbr] = filter(lambda x: len(x) > 0 and not re.match("\n", x), line)
    

# exam data
exam_names = defaultdict(str)
exam_dates = defaultdict(str)
exam_begin = defaultdict(str)
exam_end = defaultdict(str)
exam_rooms = defaultdict(list)

def format_timeslot(date, begin, end):
    #'8/23/2016|16:00|17:00'
    date = re.split("\/", date)
    for i, x in enumerate(date):
        if len(x) == 1:
            date[i] = "0%s" %x
    
    begin = re.split(":", begin)
    if len(begin[0]) == 1: begin[0] = "0%s" %begin[0]
    if len(begin[1]) == 1: begin[1] = "0%s" %begin[1]
    begin = "".join(begin)
    
    end= re.split(":", end)
    if len(end[0]) == 1: end[0] = "0%s" %end[0]
    if len(end[1]) == 1: end[1] = "0%s" %end[1]
    end = "".join(end)
    
    slotstring = "%s%s%s|%s|%s" %(date[2], date[0], date[1], begin, end)
    return slotstring

timeslots = set()
rooms = set()
for key in rows:
    #print key
    #print rows[key]
    exam_names[key] = rows[key][0]
    exam_dates[key] = rows[key][1]
    if len(rows[key]) < 3:
        continue
    exam_begin[key] = rows[key][2]
    exam_end[key] = rows[key][3]

    i = 4
    while i < len(rows[key]):
        if re.match("ORT_CODE_.*", colnames[i]):
            exam_rooms[key].append(rows[key][i])
        i += 1
    
    timeslots.add(format_timeslot(exam_dates[key], exam_begin[key], exam_end[key]))
    
    for room in exam_rooms[key]:
        rooms.add(room)

timeslots = sorted(timeslots)

# build h
from datetime import datetime, date, time, timedelta
#print timeslots[0]
#print re.split('\|', timeslots[0])


vormittag_begin = time(8, 00)
vormittag_end = time(11, 30)
mittag_begin = time(11, 30)
mittag_end = time(15, 00)
nachmittag_begin = time(15, 00)
nachmittag_end = time(19, 00)


def get_date_time(timeslot):
    datum, begin_time, end_time = re.split('\|', timeslot)
    d = date(int(datum[0:4]), int(datum[4:6]), int(datum[6:8]))
    t = time(int(begin_time[0:2]), int(begin_time[3:4]))
    
    # convert to different date time slots (vormittag, mittag, nachmittag)
    begin = datetime.combine(d, t)
    #TODO!
    timediff = 0

    if datetime.combine(d, vormittag_end) < (begin + timediff):
        return d, vormittag_begin, vormittag_end
    elif datetime.combine(d, vormittag_end) < (end - timediff):
        return d, mittag_begin, mittag_end
    else:
        return d, nachmittag_begin, nachmittag_end
    
h = []
time_differences = defaultdict(int)
for i, slot1 in enumerate(timeslots):
    datum1, slot1_begin, slot1_end = get_date_time(slot1)
    for j, slot2 in enumerate(timeslots):
        if j <= i: continue
        
        datum2, slot2_begin, slot2_end = get_date_time(slot2)
        
        begin1 = datetime.combine(datum1, slot1_begin)
        begin2 = datetime.combine(datum2, slot2_begin)
        end1 = datetime.combine(datum1, slot1_end)
        end2 = datetime.combine(datum2, slot2_end)
        
        if begin1 < begin2:
            time_differences[i,j] = begin2 - end1
        elif begin2 < begin1:
            time_differences[i,j] = begin1 - end2
        else: continue
        time_differences[i,j] = int(time_differences[i,j].seconds/3600.)
        time_differences[j,i] = time_differences[i,j]
        #print begin1, end1
        #print begin2, end2
        print time_differences[i,j]
        
    
#print time_differences
pickle.dump(time_differences, open("%sinput/time_differences.pl"%PROJECT_PATH, "w"))

#h.append(tdelta.days*24 + tdelta.seconds/3600.)
    
print len(timeslots)
print len(rooms)
