# Purpose

Here we can find the greedy algorithm and the random version of the greedy algorithm to solve the graph colouring problem.
pickle files and pictures for animation can be created and visualized here

# Use pickle
pickle file can be open directly with python.
First go the booth directory
open a python terminal (`$ ipython` for example) and write the following python line:
```
>>> from colouring import ColorGraph
>>> import pickle
>>>
>>> graphs = pickle.load(open('files/relevant_graphs', 'rb'))
```
You got here the graphs we created in relevant_graphs file. Of course you can get other object importing the needed classe and loading the right file.