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
    LINES_PER_PROB = 18
    results_tab, datas = {}, set()
    with open('%s/utils/data/performance' % PROJECT_PATH, 'rb') as src:
        # We read over the hole file
        lines = src.readlines()
        prob_nb = 0
        while prob_nb * LINES_PER_PROB < len(lines):
            # We collect the data for the given prob
            name = lines[prob_nb * LINES_PER_PROB + 2].rstrip('\n').split()[-1]
            pdate = lines[prob_nb * LINES_PER_PROB + 3].rstrip('\n').split()[1]
            data = lines[prob_nb * LINES_PER_PROB + 6].rstrip('\n').split(':').lstrip(' ')
            datas.add(data)
            runtime = float(lines[prob_nb * LINES_PER_PROB + 14].rstrip('\n').split()[-1])
            objval = float(lines[prob_nb * LINES_PER_PROB + 15].rstrip('\n').split()[-1])
            test = lines[prob_nb * LINES_PER_PROB + 11].rstrip('\n').split()[-1]

            # If test are success and date correspond to pdate we save this prob
            if test == 'SUCCEED' and (date is None or date == pdate):
                results_tab.setdefault(name, {})
                results_tab[name][data] = {
                    'running_time': int(runtime * 100) / 100.,
                    'objval': int(objval * 100) / 100.,
                    'rank': prob_nb
                }

            prob_nb += 1

    # Give an order to datas
    datas = list(datas)

    # We write the gotten results in a file as a tab
    lines = []
    for prob, dct in results_tab.iteritems():
        # We consider only the last problems regarding last_nb
        if last_nb < 0 or dct['rank'] >= prob_nb - last_nb:
            line_runtime = {'problem': prob, 'type': 'running time'}
            line_objval = {'problem': '', 'type': 'objectif value'}
            for data in datas:
                # running time
                runtime = results_tab[prob].get(data, {}).get('running_time') or 'no data'
                line_runtime.setdefault(data, runtime)
                # objectif value
                objval = results_tab[prob].get(data, {}).get('objval') or 'no value'
                line_objval.setdefault(data, objval)

            lines.append(line_runtime)
            lines.append(line_objval)

    header = ['problem', 'type'] + [d for d in datas]
    with open('%svisualization/data/tab_performance_%s.csv' % (PROJECT_PATH, date.replace('/', '_')), 'wb') as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(header)
        for line in lines:
            writer.writerow([lines[n] for n in header])


def main():
    date = '%s' % time.strftime('%d/%m/%Y')
    convert_performance_file_to_table(date=date)


if __name__ == '__main__':
    main()
