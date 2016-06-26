#!/usr/bin/env python
# -*- coding: utf-8 -*-

# In this file we can find every functions concerning the visualization
# The principal function make a visualisation for two variable: x[i, k] and y[i, l]
# i=exam, k=room, l=period
# If we have an other variable, we transform it to both variables above

from tools import convert_to_table, get_dimensions_from
import csv
import time

import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break


def print_variables(x, y):
    """ x, y have to be 2-dimensional variables
    """
    n, r, p = get_dimensions_from(x, y)
    res = 'VARIABLES: \n'
    # ----- x -------
    res += '-------- x --------  lines=rooms, columns=exams\n'
    res += convert_to_table(x, n, r)
    # ----- y -------
    res += '-------- y --------  lines=periods, columns=exams\n'
    res += convert_to_table(y, n, p)
    return res


def get_rooms_name_from_file(input_file):
    """ Get the name of the rooms and the corresponding capacity.
        @return: a list of tuple (name, capacity) sorted with respect to the capacity
    """
    with open(input_file, 'rb') as src:
        reader = csv.reader(src, delimiter='\t')
        columns = reader.next()

        # Get first the index of the informations we want to store
        ind_name, ind_cap = -1, -1
        if columns:
            for i in range(len(columns)):
                if columns[i] == 'Name':
                    ind_name = i
                if columns[i] == 'Sitzplaetze':
                    ind_cap = i

        # We get now the informations we want
        rooms = []
        columns = reader.next()
        while columns:
            rooms.append((columns[ind_name], columns[ind_cap]))
            try:
                columns = reader.next()
            except:
                break

        return sorted(rooms, key=lambda x: x[1], reverse=True)
    return []


def generate_file(x, y, data, name=None, with_room_label=True, with_exam_label=True):
    """ Generate an excel file
    """
    # Dimensions of the problem
    n, r, p = data['n'], data['r'], data['p']
    c = data['c']

    # rows to write in the final csv file
    rows = []

    # Some special name to use: for days, timeslots, rooms and exams
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    timeslots = ['9:00 - 11:00', '12:00 - 14:00', '15:00 - 17:00']

    # we split the time slots into days and weeks
    nb_weeks = p / len(days) / len(timeslots) + (p % (len(days) * len(timeslots)) > 0)
    nb_days, nb_timeslots = len(days), len(timeslots)
    nb_time_per_week = nb_days * nb_timeslots

    # we give to each room a name
    rooms_name = get_rooms_name_from_file('%sutils/data/Raumuebersicht.csv' % PROJECT_PATH)
    rooms_sorted = sorted([(k, c[k]) for k in range(r)], key=lambda x: x[1], reverse=True)
    rooms_by_name, ind = {}, 0
    for i, _ in rooms_sorted:
        rooms_by_name[i] = rooms_name[ind][0]
        ind += 1

    # We give to each exam a name
    # TODO: improve it with data from Pruefungsamt
    exams_by_name = {i: 'P%s' % i for i in range(n)}

    # for each week we check wich room is used
    rooms_week = []
    for w in range(nb_weeks):
        rooms = []
        for k in range(r):
            exams = []
            for l in range(w * nb_time_per_week, min((w + 1) * nb_time_per_week, p)):
                exams.extend([i for i in range(n) if x[i, k] * y[i, l] == 1.0])
            if exams:
                rooms.append(k)
        rooms_week.append(rooms)

    # We write first the weeks
    row = []
    for w in range(nb_weeks):
        row.extend(['Week %s' % w] + ['' for k in range(len(rooms_week[w]) + 1)])
    rows.append(row)

    # We write now the rooms
    row = []
    for w in range(nb_weeks):
        row.extend([''] + [rooms_by_name[k] for k in range(len(rooms_week[w]))] + [''])
    rows.append(row)

    # We write the days and the different timeslots
    for l in range(len(days) * (len(timeslots) + 2)):
        row = []
        if l % (len(timeslots) + 2) == 0:
            for w in range(nb_weeks):
                row.extend([days[l / (nb_timeslots + 2)]] + ['' for k in range(len(rooms_week[w]) + 1)])
        elif l % (len(timeslots) + 2) == 4:
            for w in range(nb_weeks):
                row.extend(['' for k in range(len(rooms_week[w]) + 2)])
        else:
            for w in range(nb_weeks):
                row.append(timeslots[(l - 1) % (len(timeslots) + 2)])
                t = l / (nb_timeslots + 2) * nb_timeslots + (l - 1) % (nb_timeslots + 2) + w * nb_time_per_week
                for k in rooms_week[w]:
                    # find the exam happening in room k for timeslot t
                    if t < p:
                        exam_k = [exams_by_name[i] for i in range(n) if x[i, k] * y[i, t] == 1.0]
                        row.append(exam_k[0] if exam_k else '')
                    else:
                        row.append('')
                row.append('')
        rows.append(row)

    name = 'visual-%s' % time.strftime('%d%m%Y-%H%M%S"') if name is None else name
    with open('model/Data/visualization/%s.csv' % name, 'wb') as f:
        writer = csv.writer(f, delimiter="\t")
        for row in rows:
            writer.writerow(row)


def convert_performance_file_to_table(date=''):
    """ @param date: if given we only consider the results of the date: e.g. 12/03/2005
        we get the data from the file performance: for each kind of problem, we get the running time,
        the objectif value for each kind of data
    """
    LINES_PER_PROB = 18
    results_tab, datas = {}, set()
    with open('%s/visualization/data/performance' % PROJECT_PATH, 'rb') as src:
        # We read over the hole file
        lines = src.readlines()
        prob = 0
        while prob * LINES_PER_PROB < len(lines):
            # We collect the data for the given prob
            name = lines[prob * LINES_PER_PROB + 2].rstrip('\n').split()[-1]
            pdate = lines[prob * LINES_PER_PROB + 3].rstrip('\n').split()[-1]
            data = lines[prob * LINES_PER_PROB + 6].rstrip('\n').split(':').lstrip(' ')
            datas.add(data)
            runtime = float(lines[prob * LINES_PER_PROB + 14].rstrip('\n').split()[-1])
            objval = float(lines[prob * LINES_PER_PROB + 15].rstrip('\n').split()[-1])
            test = lines[prob * LINES_PER_PROB + 11].rstrip('\n').split()[-1]

            # If test are success and date correspond to pdate we save this prob
            if test == 'SUCCEED' and (not date or date == pdate):
                results_tab.setdefault(name, {})
                results_tab[name][data] = {
                    'running_time': int(runtime * 100) / 100.,
                    'objval': int(objval * 100) / 100.
                }

            prob += 1

    # Give an order to datas
    datas = list(datas)

    # We write the gotten results in a file as a tab
    header = ['prob', 'type'] + [data for data in datas]
    lines, column_size = [], {'type': 14}
    column_size.update({data: 8 for data in datas})
    for prob, dct in results_tab.iteritems():
        column_size['prob'] = max(column_size.get('prob', 0), len(dct[prob]))
        line_runtime = {'prob': prob, 'type': 'running time'}
        line_objval = {'prob': '', 'type': 'objectif value'}
        for data in datas:
            column_size[data] = max(column_size[data], len(data))
            # running time
            runtime = results_tab[prob].get(data, {}).get('running_time') or 'no data'
            line_runtime.setdefault(data, runtime)
            # objectif value
            objval = results_tab[prob].get(data, {}).get('objval') or 'no value'
            line_objval.setdefault(data, objval)

        lines.append(line_runtime)
        lines.append(line_objval)
