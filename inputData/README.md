

How to load data:

# Unzip the archive "examination_data.zip" using the password.

# Now the follwing folders should be presend: 

    examination-scheduling/inputData/15W
    examination-scheduling/inputData/16S
    examination-scheduling/inputData/Conflicts
    examination-scheduling/inputData/Rooms
    examination-scheduling/inputData/Teilnehmer

# For preparing the R script: 
    In the console change to the folder examination-scheduling/inputData
    In R, run the following command: source("read_in_all.R")
    Now the data should be preprocessed (Usually this is already contained in the zip archive)
    
Now the data can be used with the following commands:
    
    from inputData import examination_data
    data = examination_data.load_data(dataset=1)
    
Available data sets:

    if dataset == "1": all exams with relaxed time constraints
    if dataset == "2": all exams with full time constraints
    if dataset == "3": math exams with full time constraints only
    