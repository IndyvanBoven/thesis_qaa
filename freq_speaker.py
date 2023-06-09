#!/usr/bin/env python
import pandas as pd
import os


def update_info(features, f_s, m_s, f_a, m_a, fe_types, ma_types):
    for i,gender in enumerate(features['speaker_gender']):
        if gender == "f":
            f_s += 1
            #print(features_riddle['addresseetype'][i])
            #types[features_riddle['addresseetype'][i]] +=1
        elif gender == "m":
            m_s += 1

        if features['addressee_gender'][i] == "f":
            f_a += 1
            #print(features_riddle['addresseetype'][i])
            fe_types[features['addresseetype'][i]] +=1
        elif features['addressee_gender'][i] == "m":
            m_a += 1
            ma_types[features['addresseetype'][i]] +=1
    return f_s, m_s, f_a, m_a, fe_types, ma_types


def main():
    paths = ['riddlecoref_annotations_indy', 'openboek_annotaties_indy']
    #print("List of books in RiddleCoref corpus and their frequencies speaker that are women compared to men:")
    for path in paths:
        fe_types = {'implicit':0, 'explicit':0, 'anaphoric_pronoun':0, 'anaphoric_other':0, 'none':0}
        ma_types = fe_types.copy()
        f_s, m_s, f_a, m_a = 0, 0, 0, 0
        print("These are the values for the following corpus path:",path)
        for f in os.listdir(path):
            current_f = os.path.join(path, f)
            #print(current_f)
            #f_r, m_r, f_a, m_a = 0, 0, 0, 0

            #RIDDLECOREF
            if 'riddlecoref' in current_f:
                xmlname = current_f[29:]
            else:
                xmlname = current_f[25:]
            #fe_types = {'implicit':0, 'explicit':0, 'anaphoric_pronoun':0, 'anaphoric_other':0, 'none':0}
            #ma_types = fe_types.copy()
            features_riddle =pd.read_csv('info/'+xmlname[:-4]+'.tsv', sep='\t')
            f_s, m_s, f_a, m_a, fe_types, ma_types = update_info(features_riddle, f_s, m_s, f_a, m_a, fe_types, ma_types)
        print("freq speaker women:", f_s, "freq_men speaker", m_s)
        print("\n", "freq addressee women:", f_a, fe_types, "freq_men addressee", m_a, ma_types, "\n")



if __name__ == '__main__':
    main()