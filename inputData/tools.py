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

def write_csv(filename, columns, sep=","):
    
    assert type(columns) == dict
    colnames = [name for name in columns]
    
    with open(filename, "w") as csvfile:
        line = sep.join([ "%s" %name for name in colnames ])
        csvfile.write('%s\n'%line) 
        for i in range(len(columns[colnames[0]])):
            line = sep.join([ "%f" %columns[name][i] for name in colnames ])
            csvfile.write('%s\n'%line) 
    

def read_csv(filename, key, cols, sep=","):

    '''
    Read csv file and extract data with column names in cols. Takes first value found!
    '''
    if type(cols) != list:
        cols = [cols]
        
    columns = defaultdict(dict)
    colnames = []
    with open(filename) as csvfile:
        for line in csvfile:
            line = re.sub('\"', '', line)
            line = re.sub('\n', '', line)
            line = re.sub('\r', '', line)
            line = re.split("\s*%s\s*" %sep, line)

            assert len(line) > len(cols)
            
            #print colnames

            if len(colnames) == 0:
                colnames = line
            else:
                
                # get identifier
                if type(key) == list:
                    ident = " ".join([ line[colnames.index(k)] for k in key ])
                else:
                    ident = line[colnames.index(key)]
                for i in range(0, len(colnames)):
                    name = colnames[i]
                    if name in cols and ident not in columns[name]:
                        columns[name][ident] = line[i]
#                        print columns[name]
                        
    return columns
