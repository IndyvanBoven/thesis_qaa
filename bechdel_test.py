#!/usr/bin/env python
import pandas as pd
import re
import os


def gendered_quotes(doc_info, coreferences, features, gender, opposite_g):
    """Calculates the number of quotes that pass subtest 2,
       and the number of quotes that pass subtest 3, by 
       calling mentions_check and last_gender_check.
       Returns counts for subtest 2 and 3."""
    subtest2, subtest3_counter = 0, 0
    for doc_index, doc_row in enumerate(doc_info['speaker_gender']):
        if doc_row == gender and doc_info['addressee_gender'][doc_index] == gender:
            if doc_info['begin'][doc_index] != 0:
                minus = doc_info['end'][doc_index] - doc_info['begin'][doc_index]
            else:
                minus = doc_info['end'][doc_index]
            num = doc_info['ttokenno'][doc_index] + minus
            correct_index = doc_info['ttokenno'][doc_index] - 1
            subtest2 += 1

            mention_g = mentions_check(coreferences[correct_index:num], features)
            if last_gender_check(mention_g, opposite_g) != False:
                subtest3_counter += 1
            
            # uncomment to print the quotes that failed subtest 3
            # else:
            #    print("fail\t"+doc_info['quote'][doc_index], doc_info['addresseetype'][doc_index])
    return subtest2, subtest3_counter


def check_for_mention(word, features,parsed):
    '''Check whether the mention from coref is in features file,
        and if so, return the gender(s) of this mention.
        Gender(s) as the coref mention could be in more than one mentions column.
        However, if the word is zij or ze and is singular, this recieves the f gender,
        as it is references a woman. 
        This is done to as "ze" and "zij" can also be used for plural forms.'''

    genders = [features['gender'][i] for i, mentions in enumerate(features['mentions']) if word in mentions.split(', ')]
    mention = word.lower()
    if mention.strip() == 'ze' or mention.strip() == 'zij':
        if "ev" in parsed and len(set(genders)) > 1:
            genders = 'f'

    return genders


def mentions_check(coref_quote, features):
    """ Extract the mentions in the quote by use of coreferences,
        and calls check_for_mention to extract the gender
        of these mentions. Returns the mentions with their genders."""
    current_mention, nested_mention = "", ""
    mentions_to_genders = {}
    for i, word_coref in enumerate(coref_quote):
        column = word_coref.split('\t')
        if re.search(r'\d', column[11]):
            # check if word belongs to more than one mention
            if re.fullmatch(r'.*[|]+.*', column[11]):
                diff_mentions = column[11].split("|")

                for mention in diff_mentions:
                    # check if word is the beginning of a mention
                    if re.fullmatch(r'\([0-9]+', mention):
                        if current_mention == "":
                            current_mention = column[3]
                        else:
                            nested_mention = column[3]
                            current_mention = current_mention + " " + column[3]
                    # check if word is the ending of a mention  
                    elif re.fullmatch(r'[0-9]+\)', mention):

                        # check voor 339)|289)
                        if nested_mention != "":
                            nested_mention = nested_mention + " " + column[3]
                            current_mention = current_mention + " " + column[3]

                            genders = check_for_mention(nested_mention, features,column[4])
                            mentions_to_genders[nested_mention] = genders
                            nested_mention = ""
                        else:
                            if mention == diff_mentions[1] and not re.fullmatch(r'[0-9]+\)', diff_mentions[0]):
                                current_mention = current_mention + " " + column[3]
                            elif mention == diff_mentions[0]:
                                current_mention = current_mention + " " + column[3]
                            genders = check_for_mention(current_mention, features,column[4])
                            mentions_to_genders[current_mention] = genders
                            current_mention = ""
                    # check if word is mention on its own
                    elif re.fullmatch(r'\([0-9]*\)', mention):
                        genders = check_for_mention(column[3], features,column[4])
                        mentions_to_genders[column[3]] = genders

            # check if word is the beginning of a mention
            elif re.fullmatch(r'\([0-9]+', column[11]):
                if current_mention == "":
                    current_mention = column[3]
                else:
                    nested_mention = column[3]
                    #added
                    current_mention = current_mention + " " + column[3]
            # check if word is the ending of a mention    
            elif re.fullmatch(r'[0-9]+\)', column[11]):
                current_mention = current_mention + " " + column[3]

                genders = check_for_mention(current_mention, features,column[4])
                mentions_to_genders[current_mention] = genders
                current_mention = ""
                if nested_mention != "":
                    nested_mention = nested_mention + " " + column[3]

                    genders = check_for_mention(nested_mention, features,column[4])
                    mentions_to_genders[nested_mention] = genders
                    nested_mention = ""
            # check if word is mention on its own
            elif re.fullmatch(r'\([0-9]*\)', column[11]):
                if current_mention == "":
                    genders = check_for_mention(column[3], features,column[4])
                    mentions_to_genders[column[3]] = genders
                else:
                    current_mention = current_mention + " " + column[3]
                    if nested_mention != "":
                        nested_mention = nested_mention + " " + column[3]
                    genders = check_for_mention(column[3], features,column[4])
                    mentions_to_genders[column[3]] = genders
        # check if word has no number but is in the middle of mention
        elif current_mention != "":
            current_mention = current_mention + " " + word_coref.split('\t')[3]
            if nested_mention != "":
                nested_mention = nested_mention + " " + column[3]
    return mentions_to_genders


def last_gender_check(mentions_g, gender):
    '''Disregards pronouns of speaker/addressee,
       as these could have been annotated as "m" or "f",
       as a mention of another character,
       ans as we already know the gender of the speaker/addressee.'''

    me_you = ['ik', 'Ik', 'jij', 'mij', 'jou', 'jouw', 'mijn', 'je', 'u', 'uw']
    for k,v in mentions_g.items():
        if not k.lower() in me_you:
            # remove "" values
            g = [el for el in v if str(el) != '']
            if gender == ''.join(set(g)):
                return False


def main():
    # specify your path to the data concatenated by concatenate.py
    f_path = 'info'
    for file in os.listdir(f_path):
        current_f = os.path.join(f_path, file)
        #OPENBOEK
        #tsvname = current_f[9:]
        tsvname = current_f[5:]

        # open tsv file with all info
        doc_info = pd.read_csv(current_f, sep='\t')

        #total number of quotes
        #print(len(doc_info['quote']))

        # open features tsv file with all genders of all mentions
        #openboek
        #features =pd.read_csv('features/'+tsvname, sep='\t')
        f =pd.read_csv('riddlecoref/features/'+tsvname, sep='\t')
        features = f.fillna("")
        with open('riddlecoref/coref/'+tsvname[:-4]+'.conll', 'r') as f:
            info = f.read()
            sentences = info.split('\n')

            # remove empty elements and remove #begin and #end of doc
            coreferences = [word for word in sentences if word != '' and not word.startswith('#')]

        test2_vrouw, test3_vrouw = gendered_quotes(doc_info, coreferences, features, "f", "m")
        test2_man, test3_man = gendered_quotes(doc_info, coreferences, features, "m", "f")



        print(tsvname, "\n" "subtest2 Bechdel test:", test2_vrouw, "subtest 3 Bechdel test:", test3_vrouw)
        print("subtest2 reverse Bechdel test:", test2_man, "subtest 3 reverse Bechdel test:", test3_man, "\n")

if __name__ == '__main__':
    main()