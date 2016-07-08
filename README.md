# examination-scheduling

This project consist in finding a solution to the examination scheduling at TUM (Munich). Heuristics, Optimization problems and algorithms will be developped.

# Main programmation language

Python

# Conventions

**Problems**
Two way have to be considered when creating a problem:  
  - create a class inheriting of class `BaseProblem` and complete method `build_constants`, `build_variables`, `build_constraints` and `build_dimensions`  
  - create a method that returns a model `guroby.Model`. Variable names are in this case: `"x_%s_%s_%s" % (i, j, k)` or `"x_%s_%s" % (i, j)`. `x` may be replaced by `y`. Only `x` and `y` can be used.

**Variables**
Two way to create new variables:  
  - if the variable is contained in a guroby model, its name has to be: `"x_%s_%s_%s" % (i, j, k)` or `"x_%s_%s" % (i, j)`. `x` may be replaced by `y`. Only `x` and `y` can be used  
  - if not x and y have to be dictionaries: `x = {(i, k): 0.0 for ...}` or `x = {(i, k, l): 0.0 for ..}`. `x` may be replaced by `y`. Only `x` and `y` can be used 

**Data**

---> For installing the data read the file "inputData/README.txt"!

The main data are:  
  - `c` for room capacities  
  - `s` for students capacities (for each exam)  
  - `T` for open time of rooms  
  - `Q` for conflicts  
  - `conflicts` for sparse version of `Q`  
  - `h` for beginning time of each timeslot  
  - `n` the number of exams  
  - `p` the number of timeslots  
  - `r` the number of rooms  
Upper cases are matrix `[[]]` and lower cases are lists `[]`  
Other data can be introduced, however they must be linked to the main data.  

**Usig the real data**

from inputData import examination_data
data = examination_data.read_data(semester = "15W")

Available Semesters: "15W" and "16S"

** Test **  
In the script `test_constraints.py`, in the method `SetUp(self)`, create the problem, solve it and add it to the lists depending which constraints you want to solve.  
If you want a best descriptif of eventual failures, do the same in `test_constraint_advanced.py`  

# Visualization  

To visualize the produced solutions of a problem or heuristics, first use function `update_variables` for a problem or `transform_variables` for variables to get the right form of x, y variables. These functions can be found in `tools/utils.py`. Then run the function `generate_file` (in script `tools/graphicer.py`). It will generate a file in the folder `model/Data/visualization/name.csv` where name is the name you gave if you gave one else `visual-date-time` where date and time are respectively the current date and time the current time.  

# Installation for github (Windows)

Git for windows:  
follow this link: https://github.com/git-for-windows/git/releases/tag/v2.8.1.windows.1  
Then download and install it being careful with your windows version  
  
Copy the project to your account:  
Create first a github account  
Then search for this project writing its name in the search bar  
Above right click on Fork  
  
clone the repository into your computer:  
```
$ cd folder_path
$ git clone https://github.com/username/examination-scheduling.git
$ git init
```
  
# Use github

Following command lines are essential to work on github
```
$ git commit -am "change descriptions" // To save localy all the change you did about the project
$ git push // to update on github the changes you saved with `git commit`
$ git remote add examination https://github.com/mickael-grima-TUM/examination-scheduling.git // Need to be done just one time. See `git pull` under
$ git pull examination master // update your code with the master banch. Conflicts may appear, solve them and commit then push
```