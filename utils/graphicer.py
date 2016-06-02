#!/usr/bin/env python
# -*- coding: utf-8 -*-

# In this file we can find every functions concerning the visualization
# The principal function make a visualisation for two variable: x[i, k] and y[i, l]
# i=exam, k=room, l=period
# If we have an other variable, we transform it to both variables above

from tools import convert_to_table, get_dimensions_from
import csv
import time


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


def generate_file(x, y, data, name=None):
    """ Generate an excel file
    """
    n, r, p = data['n'], data['r'], data['p']

    rows = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timeslots = ['9:00 - 11:00', '12:00 - 14:00', '15:00 - 17:00']
    nb_weeks = p / len(days) / len(timeslots) + (p % (len(days) * len(timeslots)) > 0)

    # for each week we check wich room is used
    rooms_week = []
    for w in range(nb_weeks):
        rooms = []
        for k in range(r):
            exams = []
            for l in range(w * (len(days) * len(timeslots)), min((w + 1) * (len(days) * len(timeslots)), p)):
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
        row.extend([''] + ['Room %s' % k for k in range(len(rooms_week[w]))] + [''])
    rows.append(row)

    # We write the days and the different timeslots
    for l in range(len(days) * (len(timeslots) + 2)):
        row = []
        if l % (len(timeslots) + 2) == 0:
            for w in range(nb_weeks):
                row.extend([days[l / (len(timeslots) + 2)]] + ['' for k in range(len(rooms_week[w]) + 1)])
        elif l % (len(timeslots) + 2) == 4:
            for w in range(nb_weeks):
                row.extend(['' for k in range(len(rooms_week[w]) + 2)])
        else:
            for w in range(nb_weeks):
                row.append(timeslots[(l - 1) % (len(timeslots) + 2)])
                t = l / (len(timeslots) + 2) * len(timeslots) + (l - 1) % (len(timeslots) + 2) + w * len(days) * len(timeslots)
                for k in rooms_week[w]:
                    # find the exam happening in room k for timeslot t
                    if t < p:
                        exam_k = ['P%s' % i for i in range(n) if x[i, k] * y[i, t] == 1.0]
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
