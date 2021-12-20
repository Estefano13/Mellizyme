# Mellizyme coding exercise solutions

This repository holds four .py files corresponding to the four tasks in the Mellizyme coding exercise. Task_1_completed.py reads files "drugs.csv" and "clinical_trials_2015.jsonl", whereas Task_2_completed.py reads files "drugs.csv" and "usan_stems.csv". They are written so that the .csv and jsonl files must be in the same directory for them to run. I have not included these files in the repo. Task_3_completed.py takes the output from the first two tasks, and Task_4_completed.py reads the output of task 3. 

The outputs of each .py file are stored in the Outputs directory. Task_3_completed.py and Task_4_completed.py will read the files they need from this directory when it is in the same directory as the .py files.

There should be no problems running the files from the terminal or with an IDE (I used Spyder). 

Each file includes the code and my comments interspersed within the code, explaining my thought process and the decisions I made with my implementation. Finally, at the end of each script, there are some notes regarding the task, as well as the assumptions I made and some of their potential trade-offs. 

In my machine, each scrip took this time to run(from terminal):

- Task_1: ~10 minutes
- Task_2: ~4 seconds
- Task_3: ~3 minutes
- Task_4: >1 second

List of libraries used:

- pandas
- numpy
- re
- json
- rapidfuzz
- csv
- itertools
- collections
