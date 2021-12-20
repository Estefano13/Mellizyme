import pandas as pd
import json

import itertools
import collections

"""
I start by loading the prevous task's output.
"""

task_3 = pd.read_json('Output/Task_3_output.json')

"""
Similarly to task 3, I extract the codes(description plus type) and the list 
of trials. Subsequently, I extract all the trials into a list and create a 
list of the codes repeated per number of associated trials(i.e. if a 
description has three trials, then the description is repeated three times).
These two lists are put together as all_trials_flat dataframe.
"""

all_codes = task_3.iloc[:,:2].values.tolist()
all_trials = task_3.iloc[:,2].values.tolist()

all_trials_flat = [j for i in all_trials for j in i]
all_trials_flat = pd.DataFrame(all_trials_flat)

num_of_trials = list(map(len,all_trials))
codes = [[a]*b for a,b in zip(all_codes, num_of_trials)]
codes = [j for i in codes for j in i]

all_trials_flat.insert(1, 'codes', codes)

"""
The codes column is then split into description and type. Codes column is 
dropped, as well as the rows with type = subclass. Then the type column is also 
dropped.
"""
all_trials_flat[['description', 'type']] = pd.DataFrame(all_trials_flat['codes'].to_list())
all_trials_flat.drop(['codes'], axis = 1, inplace = True)
all_trials_flat = all_trials_flat[all_trials_flat['type'] == 'class']
all_trials_flat.drop(['type'], axis = 1, inplace = True)

"""
The columns are renamed, and the duplicates are dropped. As I did with task 3, I 
assume that only drug classes matter here. I duplicates were not dropped, then 
it would be possible to count pairs like:
    
    {
    'description_1': 'iodine-containing contrast media', 
    'description_2': 'iodine-containing contrast media'
    } 

Which I assume is undesirable given my understanding of the task. 
"""

all_trials_flat.columns = ['trial', 'description']
all_trials_flat.drop_duplicates(inplace = True)

"""
Here I create a new dataframe named duplicated_trials with only the rows that 
have a with a duplicated trial in the dataset, meaning that the 
duplicated_trials dataframe only contains trials that matched to more than 
one drug class. 

Sorting by trial is unnecessary, but the reassignment of the duplicated_trials
dataframe avoids a warning message issued by line 79. The same can be 
accomplished by deep copying the dataframe. 
"""

duplicated_trials =  all_trials_flat[all_trials_flat['trial'].duplicated(keep = False)]
duplicated_trials = duplicated_trials.sort_values(by = ['trial'])

"""
The following step is to create a new column in which all the descriptions 
associated with a trial number are grouped together. We then drop the 
description column and the duplicates.
"""

duplicated_trials['Groups'] = duplicated_trials.groupby(['trial'])['description'].transform(lambda x: '|'.join(x))
duplicated_trials.drop(['description'], axis = 1, inplace = True)
duplicated_trials.drop_duplicates(inplace = True)

"""
In order to count how frequent a pair of drug classes is, the code below visits
every row in the duplicated_trials dataframe and generates unique pairs of the
descriptions found on each row and counts them. Every row processed, the pairs
are updated so that every existing pair's count in the variable counter is
updated, and if a new pair is encountered, it is added to counter.  

The results are stored and sorted in descending order.
"""

counter = collections.Counter() 

for row in duplicated_trials['Groups']:
    row = row.split('|')
    counter.update(collections.Counter(itertools.combinations(row, 2)))

result = counter.most_common()

"""
Lastly, the result is formatted correctly and saved as a json file.
"""

result_df = pd.DataFrame(result, columns = ['pairs', 'trial_count'])
result_df[['description_1', 'description_2']] = pd.DataFrame(
    result_df['pairs'].to_list())
result_df.drop(['pairs'], axis = 1, inplace = True)
result_df = result_df[['description_1', 'description_2', 'trial_count']]

parsed = [row.dropna().to_dict() for index,row in result_df.iterrows()]

with open('Output/Task_4_output.json', 'w') as json_file:
    json.dump(parsed, json_file, indent = 4)  

"""
Notes and assumptions:
    
  - In my machine, this script takes less than a second.
  
  - As mentioned before, I assume that since we are interested in the 'class'
    of the drug, meaning the description. Hence, identical trial and description 
    pairs have been considered duplicates and removed.
    
  - I have assumed that trial numbers can be combined. In the 
    clinical_trials.jsonl file, some nct_ids are repeated with a different 
    intervention_name. Although I didn't join them explicitly in task 1,
    the methods used in subsequent tasks do not differentiate between different 
    rows with the same trial number. This result in all descriptions under the 
    same trial number being considered as happening in the same trial. 
    For instance, trial NCT00293735 has two entries in the clinical trial data:
        
        {"nct_id": "NCT00293735", "drugs": ["labetalol"]},
        {"nct_id": "NCT00293735", "drugs": ["magnesium sulfate"]}
    
    The respective drugs match for the following usan codes:
        
            "drug": "labetalol", "usan_codes": [
                {
                    "description": "combined alpha and beta blockers",
                    "type": "class"
                    }
                ]
    and
    
            "drug": "magnesium sulfate", "usan_codes": [
                {
                    "description": "quaternary ammonium derivatives",
                    "type": "class"
                    },
                {
                    "description": "antimicrobials (sulfonamides derivatives)",
                    "type": "class"
                    }
                ]

    My implementation counts trial NCT00293735 as a match for the pair
    ("quaternary ammonium derivatives", "combined alpha and beta blockers") 
    even though they appear on separate rows. I asked Neil about this in the 
    context of task 1 (whether or not it was ok to combine the drugs used on 
    trials with the same number) and was given a positive answer, which is why 
    I've decided to keep this assumption.  
"""    
 
