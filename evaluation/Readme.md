This Readme explains how to start the different programs

# MOSES

- call python evaluation/moses.py
- inside the file specify the dataset to use (cf. inputData/Readme.md)
- receive an evaluation of the MOSES result for the dataset

# ILP

- use python evaluation/worker.py
- in worker.py specify which ILP formulations you want to evaluate
- in worker.py also specify from which data source you want to generate your data
- please be aware that not all ILP models work with all data(for example some ILPs do not consider locations)

# Random

- call python evaluation/random_heuristic.py
- In the file you can specify which dataset to use. Default is 2.
- Optimizes using purely random coloring vertex order.

# Compare AC, Johnson and Random Performance

- call python evaluation/comparison_tests.py
- In the file specify which Heuristic to use (lines 36-38)
- also specify the parameters of the run (lines 24-28)