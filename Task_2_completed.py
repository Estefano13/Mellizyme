import pandas as pd
import numpy as np
import csv
import json
import re 

"""
In this task, I start by loading the drug file and extracting the primary name.
Then I remove all special characters and numbers and separate the names into 
words to account for multi-word names (This way, all words in a drug name can 
be analysed separately).
"""

drugs_file = pd.read_csv('drugs.csv')
drug_prim_name = drugs_file[['itemLabel']].copy()

drug_prim_name['itemLabel'] = drug_prim_name['itemLabel'].map(
    lambda x: re.sub(r'\W+', ' ', x))
drug_prim_name['itemLabel'] = drug_prim_name['itemLabel'].map(
    lambda x: re.sub(r'\d+', ' ', x))
drug_prim_name['itemLabel'] = drug_prim_name['itemLabel'].map(
    lambda x: x.strip())
drug_prim_name['itemLabel'] = drug_prim_name['itemLabel'].str.split(
    ' ', expand = False)

"""
I load the usan_stem file and create a dataframe. I assume the examples can be 
ignored. I remove the " from the dataframe, rename the columns and remove 
whitespaces from the stem column. I've loaded the file with this method instead
of the read_json() function due to 2 rows produced errors and would've had to be 
ignored otherwise.


I create a column for the type (class or subclass) and remove all rows without
any stem (the rows used to differentiate groups and subgroups). 
I remove the name column and create a list of stems for each string in the 
column stem (e.g. '-adol,-adol-' turns into ['-adol', '-adol-']).
Subsequently, the description and type are grouped into a dictionary and placed
in the usan_codes column (this is done to match the desired output format). 
The description and type columns are dropped.  
"""

with open("usan_stems.csv") as file:
    csvreader = csv.reader(file)
    header = next(csvreader)
    usan_stem = []
    for row in csvreader:
        usan_stem.append(row)

usan_stem = pd.DataFrame(usan_stem)
usan_stem = usan_stem.iloc[:,:3]
usan_stem = usan_stem.replace({'"':''}, regex=True)
usan_stem.columns = ['name', 'stem', 'description']
usan_stem['stem'] = usan_stem['stem'].replace({' ':''}, regex = True)

usan_stem.loc[usan_stem['name'] == '','type'] = 'subclass'
usan_stem['type'] = usan_stem['type'].fillna(0)
usan_stem.loc[usan_stem['type'] == 0,'type'] = 'class'
usan_stem.loc[usan_stem['stem'] == '', 'type'] = None

usan_stem.drop(['name'], axis = 1, inplace = True)
usan_stem = usan_stem.dropna(axis = 0, inplace = False)
usan_stem['stem'] = usan_stem['stem'].str.split(',',expand = False)
usan_stem['usan_codes']=usan_stem[['description', 'type']].to_dict(orient = 'records')
usan_stem.drop(['description', 'type'], axis = 1, inplace = True)

"""
A new dataframe is created to include the drug name and the column usan_codes 
filled with empty lists into which the matching description will be appended.
"""
drugs_df = drug_prim_name.copy()
drugs_df['usan_codes'] = np.empty((len(drugs_df), 0)).tolist()
drugs_df.columns = ['drug', 'usan_codes']

"""
The following piece of code describes four nested loops that visit all the 
words in each drug name and compare them with all the stems. If a prefix, 
infix or suffix is found to be a match, then the accompanying dictionary, which 
contains the description and type, is appended to usan_codes column in the 
corresponding drug's row.   
"""

drugs = drugs_df.iloc[:,0]
stems = usan_stem.iloc[:,0]

for idx_drug, drug in enumerate(drugs):
    for word in drug:
        for idx_stem, stem in enumerate(stems):
            for element in stem:
                if element.endswith('-') and not element.startswith('-'):  # is a prefix
                    if word.startswith(element[:-1]):
                        drugs_df.iloc[idx_drug,1].append(usan_stem.iloc[idx_stem, 1])
                elif element.startswith('-') and element.endswith('-'):  # It is a infix
                    if element[1:-1] in word[1:-1]:
                        drugs_df.iloc[idx_drug,1].append(usan_stem.iloc[idx_stem, 1])
                elif element.startswith('-') and not element.endswith('-'):  # It is a sufix
                    if word.endswith(element[1:]):
                        drugs_df.iloc[idx_drug,1].append(usan_stem.iloc[idx_stem, 1])
                        
"""
I've replace the column with the list of words in each drug name with the drug name 
string (with special characters and digits) to match the desired output and 
drop all rows without a match.
"""
drugs_df['drug'] = drugs_file['itemLabel']
drugs_trimmed = drugs_df[drugs_df['usan_codes'].map(lambda x: len(x)) > 0]

"""Lastly, the result dataframe is saved as a json file."""

parsed = [row.dropna().to_dict() for index,row in drugs_trimmed.iterrows()]

with open('Output/Task_2_output.json', 'w') as json_file:
    json.dump(parsed, json_file, indent = 4)                    

"""
Notes and assumptions:
    
  - In my machine, this script takes 2.5 seconds.
    
  - As advised by Neil, I've worked on the assumption that a drug name can 
    match any number of prefixes, suffixes and infixes.
    
  - I've also assumed that the examples in the usan_stem file were not to be 
    taken into account. 
    
  - Again, after communication with Neil, I decided to only analyse the primary 
    names of each drug.

"""
