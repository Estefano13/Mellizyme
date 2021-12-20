import pandas as pd
import numpy as np
import json

"""
I start by loading the output of the previous two tasks.
"""

task_1 = pd.read_json('Output/Task_1_output.json') 
task_2 = pd.read_json('Output/Task_2_output.json')

"""
From task_2, I extracted all the descriptions and types per drug. To do 
this, I separated the names from the codes.
"""

all_names = task_2.iloc[:,0].values.tolist()
all_codes = task_2.iloc[:,1].values.tolist()

"""
Now, since the all_codes list contains lists of dictionaries for every stem
match, I've extracted all the dictionaries in a dataframe. Subsequently, I've 
computed the number of unique descriptions.
"""

all_codes_flat = [j for i in all_codes for j in i]
extended_df = pd.DataFrame(all_codes_flat)
unique_descriptions = extended_df.copy()
unique_descriptions = unique_descriptions.drop_duplicates()


"""
Now I create a list with the names to match the flattened description dataframe.
For instance, If a drug has four matching descriptions, a list is created in 
which that drug's name is repeated four times to match the descriptions dataframe
produced before, extended_df.  

I dropped the duplicates in the resulting dataframe. The reason is that
a drug such as Natalizumab has three identical matches to -mab, -umab and 
-zumab with identical description. Similarly, other trials could have used two
drugs with the same description. I assume we are interested in the 'class' of
drugs used, so there is no need to keep the duplicates. 
"""

num_of_entries = list(map(len, all_codes))
all_names_flat = [[a]*b for a, b in zip(all_names, num_of_entries)]
all_names_flat = [j for i in all_names_flat for j in i]
extended_df.insert(2, 'names', all_names_flat)
extended_df.drop_duplicates(inplace = True)

"""
Then I create a drugs column with all the drugs matching the description of 
each row. Then by dropping the names, I can then eliminate all the duplicates. 
The resulting dataframe has all unique descriptions and a list of drugs that 
match them. I then add a trials column with empty lists to which all matching 
trials can be appended.
"""

extended_df['drugs'] = extended_df.groupby(['description'])['names'].transform(lambda x: '|'.join(x))
extended_df.drop(['names'], axis = 1, inplace = True)
extended_df.drop_duplicates(inplace = True)
extended_df['drugs'] = extended_df['drugs'].str.split('|', expand = False)
extended_df['trials'] = np.empty((len(unique_descriptions), 0)).tolist() 

"""
These nested loops go through all the drugs used in a trial and check whether 
or not they matched any drugs in the extended_df dataframe. If they do, then 
the trial number is appended to the trial list corresponding to that description.
"""

import time
start_time = time.time()
for idx, trial in task_1.iterrows():
    for i in trial[1]:
        for idx, usan_codes in extended_df.iterrows():
            for j in usan_codes[2]:
                if i == j:
                    usan_codes[3].append(trial[0])
                    
"""
Lastly, the drugs column is dropped and the resulting dataframe is saved as a
json file.
"""

extended_df.drop(['drugs'], axis = 1, inplace = True)
parsed = [row.dropna().to_dict() for index, row in extended_df.iterrows()]

"""
Code to save the result as a json lines file:
    
with open('Output/Task_3_output.jsonl', 'w') as outfile:
    for entry in parsed:
        json.dump(entry, outfile)
        outfile.write('\n')
"""

with open('Output/Task_3_output.json', 'w') as json_file:
    json.dump(parsed, json_file, indent = 4)  

"""
Notes and assumptions:
    
  - In my machine, this script takes 3 minutes.
  
  - As mentioned before, I assume that since we are interested in the 'class'
    of the drug, meaning the description, then drugs with matches to stems with 
    identical descriptions and types have been considered duplicates and 
    removed.
    
"""

