
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
paths = os.getcwd().split('/')
path = ''
for p in paths:
    path += '%s/' % p
    if p == 'examination-scheduling':
        break
sys.path.append(path)


from mpi4py import MPI

# global communication variables
WORKTAG = 0
DIETAG = 1

def master(comm, size, status, data, n_jobs):
    '''
        The master sends jobs to the children. It sends data only once in order to minimize communication.
        It returns the complete history of the optimisation.
    '''
    
    xs = []
    ys = []
    vs = []
    pending = [False] * size
    jobs = range(n_jobs)
    
    for i in range(1, size): 
        
        if len(jobs) == 0:
            break
        job = jobs[0]
        jobs.pop(0)
        
        comm.send(obj = data, dest = i, tag = WORKTAG)
        pending[i] = True
    
    # kill slaves which are not used
    for i in range(1,size):
        if not pending[i]:
            comm.send(obj=None, dest=i, tag=DIETAG)
         
         
    # send jobs while there is work to do  
    while len(jobs) > 0 and any(pending):
        
        # print status
        print "Progress: %d percent" %((1 - 1.0*len(jobs)/n_jobs)*100)
        
        # receive results
        x, y, v = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        pending[status.Get_source()] = False
        xs.append(x)
        ys.append(y)
        vs.append(v)
        
        job = jobs[0]
        jobs.pop(0)
        
        comm.send(obj=None, dest=status.Get_source(), tag=WORKTAG)
        pending[status.Get_source()] = True
    
    # receive jobs
    for i in range(1,size):
        if not pending[i]:
            comm.send(obj=None, dest=i, tag=DIETAG)
            
        x, y, v = comm.recv(None, source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        pending[status.Get_source()] = False
        xs.append(x)
        ys.append(y)
        vs.append(v)
        
    # terminate slaves
    for i in range(1,size):
        comm.send(obj=None, dest=i, tag=DIETAG)
    
    return xs, ys, vs
        
        
def slave(comm, rank, size, status, run_function):
    '''
        Slave expects tasks. 
        Data needs to be sent only once, as long as it is not modified (which should be the case for examination scheduling problem)
    '''
    data = None
    while 1:
        # receive
        if data is None:
            data = comm.recv(None, source=0, tag=MPI.ANY_TAG, status=status)
        else:
            msg = comm.recv(None, source=0, tag=MPI.ANY_TAG, status=status)
            if msg is not None:
                print "ERROR"
                break
            
        if status.Get_tag() == DIETAG: 
            break
        # get results
        x, y, v = run_function(data)
        #print v
        # send results to master
        # TODO: This could be done only for the best index if data is stored in slave.
        # TODO: Only do this if the communication is the overhead!!
        comm.send(obj=(x, y, v), dest=0)
    



