#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import time

import os
PATHS = os.getcwd().split('/')
PROJECT_PATH = ''
for p in PATHS:
    PROJECT_PATH += '%s/' % p
    if p == 'examination-scheduling':
        break


def convert_performance_file_to_table(date=None, last_nb=-1):
    """ @param date: if given we only consider the results of the date: e.g. 12/03/2005
        we get the data from the file performance: for each kind of problem, we get the running time,
        the objectif value for each kind of data
    """
    results_tab = {}
    with open('%s/visualization/data/performance' % PROJECT_PATH, 'rb') as src:
        # We read over the hole file
        line = src.readline()
        start, prob_nb = False, 0  # Do we start a problem
        name, data, result = '', {}, {}
        while line:
            # If we start a new problem
            if line.startswith('--') and not start:
                start = True
                prob_nb += 1
            # if we end a problem we save it under some conditions
            elif line.startswith('--') and start:
                start = False
                # date correspond to pdate we save this prob
                if date is None or date == (result.get('date') or ''):
                    results_tab.setdefault(name, {})
                    results_tab[name][data] = {
                        'running_time': int(result['runtime'] * 100) / 100.,
                        'objval': int(result['objval'] * 100) / 100. if result['objval'] != 'NaN' else 'NaN',
                        'rank': prob_nb
                    }
                    result = {}

            # If we consider a problem
            if start:
                if line.startswith('@@@'):
                    part = line.split()[1]
                    if part == 'GENERAL':
                        # Get the problem name
                        line = src.readline()
                        name = line.rstrip('\n').split()[-1]
                        # Get the date
                        line = src.readline()
                        result['date'] = line.rstrip('\n').split()[1]
                    elif part == 'DATA':
                        # Get the data
                        line = src.readline()
                        data = line.rstrip('\n').split(':')[1].lstrip(' ')
                    elif part == 'TEST':
                        # Get the result of the test
                        line = src.readline()
                        result['test'] = line.rstrip('\n').split()[-1]
                    elif part == 'PERFORMANCE':
                        # Get the running time
                        line = src.readline()
                        result['runtime'] = float(line.rstrip('\n').split()[-1])
                        # Get the objval
                        line = src.readline()
                        result['objval'] = float(line.rstrip('\n').split()[-1]) if result['test'] == 'SUCCEED' else 'NaN'

            line = src.readline()

    # Keep only the problems corresponding to last_nb
    results, datas = {}, set()
    for prob, dct in results_tab.iteritems():
        results[prob] = {}
        for data, result in dct.iteritems():
            if last_nb < 0 or result['rank'] >= prob_nb - last_nb:
                datas.add(data)
                results[prob][data] = result
        if not results[prob]:
            del results[prob]

    # Give an order to datas
    datas = list(datas)

    # We write the gotten results in a file as a tab
    lines = []
    for prob, dct in results.iteritems():
        line_runtime = {'problem': prob, 'type': 'running time'}
        line_objval = {'problem': '', 'type': 'objectif value'}
        for data in datas:
            # running time
            runtime = results.get(prob, {}).get(data, {}).get('running_time') or 'no value'
            line_runtime.setdefault(data, runtime)
            # objectif value
            objval = results.get(prob, {}).get(data, {}).get('objval') or 'no value'
            line_objval.setdefault(data, objval)

        lines.append(line_runtime)
        lines.append(line_objval)

    header = ['problem', 'type'] + [d for d in datas]
    date = '%s-%s' % (date or time.strftime('%d/%m/%Y'), time.strftime('%H_%M_%S'))
    with open('%svisualization/data/tab_performance_%s.csv' % (PROJECT_PATH, date.replace('/', '_')), 'wb') as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(header)
        for line in lines:
            writer.writerow([line[n] for n in header])


def main():
    date = '%s' % time.strftime('%d/%m/%Y')
    convert_performance_file_to_table(date=date)


if __name__ == '__main__':
    main()
