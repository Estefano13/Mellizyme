import pandas as pd
import json

from rapidfuzz import fuzz, process

"""
I start by importing and cleaning/transforming the files.
Then, I remove the trademark symbols in both files, which I assume are irrelevant 
for this task (i.e. osmeprazol should match to osmeprazol®). 

For the drugs dataframe, I join the primary name of the drug at the beginning 
of the alternate names string with a vertical line separator. Subsequently, 
I create a list with all the names, using the vertical line as a delimiter.

I assume we are only interested in the trials whose intervention_type is "Drug",
so I create a dataframe considering just them.
"""

drugs = pd.read_csv('drugs.csv')
clinical_trials = pd.read_json('clinical_trials_2015.jsonl', lines = True) 

drugs = drugs.replace({'®':'','™':''},regex=True)
drugs['All names'] = drugs.iloc[:,0] + '|' + drugs.iloc[:,1]
drugs_names = drugs['All names'].str.split('|', expand = False).to_frame()

clinical_trials = clinical_trials.replace({'®':'','™':''},regex=True)
clinical_trials_drug_intervention = clinical_trials.loc[
    clinical_trials['intervention_type'] == 'Drug'].reset_index(drop = True)
clinical_trials_drug_intervention.drop(['intervention_type'], 
                                       axis = 1, inplace = True)

"""
For the matching task, I used fuzzy string matching. However, to 
increase accuracy, I separated the intervention_name into substrings the
size of the drug. For instance, if the drug name is "labetalol", then the
intervention_name "labetalol (seizure prevention)" is split into the list
['labetalol', '(seizure', 'prevention)']. 

For multiword names such as "megestrol acetate", I split the 
intervention_name into two word substrings, 
e.g., "labetalol (seizure prevention)" is split into the list
['labetalol (seizure', '(seizure prevention)']. Then the drug name can be 
compared against intervention_name substrings of equal word count.  
"""

def get_substrings(string, spaces):
    """
    Splits a string into its constituent substrings with a set number
    of whitespaces.

    Parameters
    ----------
    string : Input string to be separated into substrings.
    spaces : Desired amount of whitespaces in the resulting substrings.

    Returns
    -------
    substrings : List of substrings.

    """
    substrings = []
    string = string.split()
    words = spaces + 1
    start = 0
    while words+start <= len(string):
        substrings.append(' '.join(string[start:words+start]))
        start += 1
    return substrings

def find_match(drug_name, notes):
    """
    Takes a drug name and an intervention_name strings, splits the 
    intervention_name into substrings of equal word count to the drug (by 
    calling .split() method or the get_substrings() function), and 
    performs fuzzy matching using the quick ratio function of the rapidfuzz 
    library. The commented lines are there in case another scorer is used. Since
    Qratio is case insensitive, they are not needed in this implementation.

    Parameters
    ----------
    drug_name : Drug name string.
    notes : intervention_name string.

    Returns
    -------
    bool
        TRUE if the quick ratio score is above the 97.5 threshold.
        FALSE otherwise.
    """
    spaces = drug_name.count(' ')
    length = len(drug_name)
    if (length<=2) | (spaces>(notes.count(' '))) | (length>len(notes)) :
        pass
    else:
        #drug_name = drug_name.lower()
        #notes = notes.lower()
        if spaces == 0:
            words_in_notes = notes.split(' ')
        else:
            words_in_notes = get_substrings(notes, spaces)
        if words_in_notes:
            best_match = process.extractOne(drug_name, words_in_notes, 
                                            scorer = fuzz.QRatio)
            if best_match[1] > 97.5:
                return True
            else:
                pass
        else:
            pass


"""
In the following code, the first loop visit all rows in the intervention_name 
column of the clinical_trials_drug_intervention dataframe. The second loop 
visits all rows in the drugs_names dataframe. 

Subsequently, the code applies the find_match() function between the 
intervention_name string and all the names registered for a drug. If a match 
is found, then the primary name is appended to a list containing all the 
recorded matches for that clinical trial.

This list is then appended to the matches list containing all the matches for all 
clinical trials.

"""
matches = []

for w in clinical_trials_drug_intervention.iloc[:,1]:
    matches_to_notes = []
    for i in drugs_names.iloc[:,0]:
        drug_matches = list(filter(lambda x: find_match(x, w), i))
        if drug_matches: 
            matches_to_notes.append(i[0])
    matches.append(matches_to_notes)
 
"""
The matches list is appended to the nct_id column from the 
clinical_trials_drug_intervention dataframe. All clinical trials without a 
match are dropped from the final file.
"""  
 
result = clinical_trials_drug_intervention.copy()
result['drugs'] = matches
result.drop(['intervention_name'], axis = 1, inplace = True)
result = result[result['drugs'].map(lambda x: len(x)) > 0]

"""Lastly, the result dataframe is saved as a json file."""

parsed = [row.dropna().to_dict() for index, row in result.iterrows()]

"""
Code to save the result as a json lines file:

with open('Output/Task_1_output.jsonl', 'w') as outfile:
    for entry in parsed:
        json.dump(entry, outfile)
        outfile.write('\n')
"""

with open('Output/Task_1_output.json', 'w') as json_file:
    json.dump(parsed, json_file, indent = 4)   

 
"""
Notes and assumptions:
    
  - In my machine, this script takes 8 to 9 minutes.
    
  - I have left out drug names with a length of fewer than two characters. 
    A quick analysis of the clinical trials (analysis not present in the 
    code) data revealed that most, if not all of the two length words in the 
    intervention_name column were prepositions. 

  - To speed up performance, I've disregarded cases in which the drug name is 
    longer than the intervention_name string. Some cases in which this is 
    detrimental are, for instance: drug_name "recombinant GM-CSF", which is 
    not matched to intervention name "GM-CSF". In order to improve this 
    performance, a combination of partial ratios and quick ratios could be used, 
    or alternatively, a more sophisticated approach to substring splitting.
    
  - I chose a relatively strict threshold for the QRatio function (97.5).
    Obviously, this choice of threshold and scorer can be tweaked a lot 
    depending on the trade-offs we are willing to take. QRatio is case and 
    special characters insensitive, the latter of which can result in 
    mismatches. For instance, an intervention with omeprazole is matched with 
    the drug esomeprazole, which has the alternative name: (-)-omeprazole. Ratio 
    and WRatio are scorers that might be worth exploring (WRatio, in particular, 
    shows a lot of success matching drug names without the need to split the 
    intervention name into substrings. However, both of them take much longer 
    to process the data set (a different find_match() function with WRatio took 
    my machine about 90 minutes).
 
""" 
