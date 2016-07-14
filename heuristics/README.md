
# Structure

The architecture of our heuristics is implemented in **schedule_exams.py**.

The time sub-problem using Simulated Annealing is solved in **schedule_times.py**.

The room sub-problem is solved in **schedule_rooms.py**.

The Ant Colony Optimization can be found in **AC.py** and the Johnson heuristic is in **johnson.py**.

Bothe make use of the **ConstrainedColorGraph** classes implemented in the file with the same name.

Also, a heuristic using random colorings is implemented in **Metaheuristic.py**.


###
Please use the folder 'evaluation' for runs