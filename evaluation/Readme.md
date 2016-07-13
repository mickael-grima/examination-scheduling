This Readme explains how to start the different programs

# ILP

- use python evaluation/worker.py
- in worker.py specify which ILP formulations you want to evaluate
- in worker.py also specify from which data source you want to generate your data
- please be aware that not all ILP models work with all data(for example some ILPs do not consider locations)

# Random

- call python evaluation/random_heuristic.py
- In the file you can specify which dataset to use. Default is 2 (cf. inputData/Readme.md)
- Optimizes using purely random coloring vertex order.
