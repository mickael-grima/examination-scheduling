# examination-scheduling

This project consist in finding a solution to the examination scheduling at TUM (Munich). Heuristics, Optimization problems and algorithms will be developped.

# Main programmation language

Python

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