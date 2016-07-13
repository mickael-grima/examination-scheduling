v_1: First try to model the linear programm
v_2_Q: First try to implement quadratic model
v_3: reducing number of variables: doesnt create x_i,k,l if room k is closed in period l
v_4: some implementation of clique constraints to cut of non-integer solutions
v_5: changed obj because the sum over the distance between exams doest work for cliques Because the total distance between them would be in a clique of 3 independent of the period of the third exam
v_6: found out that c6 is completly redundant so simple removed it
v_7: testing new objective function
v_8: removed the new objective function again
v_9: testing slightly different objective function again
v_10: implementing locations meaning that exams are only written where the lecture is
v_11: replacing wuicksum in constraint building to speed up model by more than 2
v_12: reduced the M in the Big Method dependent of the number of students participating in an exam
v_13: adding some cover inequalities for the periods
v_14: Testin different cut parameter settings
v_15: tested some covers but removed them again-no change
v_16: First symmetry approach by given an order on the variables: Only use small rooms if big rooms are in use
v_17_lexicographic: First try to force lexicographic order
v_17_pertubate:  implementing idea of v_16 as an pertubation of the objective function
v_18: Different lexicographic order
v_19: trying out setting branch priority ont the periods first
v_20: rudimentary try to implement Orbital branching in gurobi using some pretty simple grouping idea and constraint branching - doesnt work well grouping fails because of conflicts
v_21: some more lexicograpic ordering constraints test
v_22: again some more lexicograpic ordering constraints test - strengthening the constraint from v_22
v_23: Implementing that some examc cannot be in a given period to test real data

Q_v_1,Q_v_2 implementing quadratic model, geting used to python, Gurobi










