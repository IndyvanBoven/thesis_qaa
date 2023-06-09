#!/usr/bin/env python
import pandas as pd
import xml.etree.ElementTree as ET
import os
import re


def create_tsv(speakers, char, addressees, xmlname):
    """Appends all information from the necessary attributes,
       by matching the quote/speaker attribution annotation file,
       with the addressee annotation file and appending
       the gender that was earlier extracted from the features,
       and saves this in a tsv file. """
    
    columns = ['ids', 'quote', 'speaker', 'speaker_gender', 'addressee', 'addressee_gender', 'addresseetype', 'ttokenno', 'begin', 'end']
    new_dict = {column : [] for column in columns}

    # uncomment to add speaker type
    # new_dict['type'] = []
    
    adr_nodes = addressees.findall('.//quote')
    print("Number of quotes according to adr:", len(adr_nodes))
    spr_nodes = speakers.findall('.//quote')
    print("Number of quotes according to speaker anno:", len(spr_nodes))

    for adr_node, spr_node in zip(adr_nodes, spr_nodes):
        if adr_node.attrib['id'] == spr_node.attrib['id']:
            new_dict['ids'].append(adr_node.attrib['id'])
        else:
            print("Warning: id is not matching for this quote!") #if warning then speaker/addresse files are not parallel!
            print(adr_node.attrib['id'], spr_node.attrib['id'])
            if adr_node.text.strip() == spr_node.text.strip():
                new_dict['ids'].append(spr_node.attrib['id'])
            else:
                print(adr_node.text, spr_node.text)
        
        new_dict['quote'].append(''.join(spr_node.itertext()))
        new_dict['ttokenno'].append(spr_node.attrib['ttokenno'])
        new_dict['begin'].append(spr_node.attrib['begin'])
        new_dict['end'].append(spr_node.attrib['end'])

        if 'speaker' in adr_node.attrib and 'speaker' in spr_node.attrib:
            new_dict['addressee'].append(adr_node.attrib['speaker'])
            new_dict['speaker'].append(spr_node.attrib['speaker'])
            if adr_node.attrib['speaker'] in char:
                new_dict['addressee_gender'].append(char[adr_node.attrib['speaker']])
            else:
                new_dict['addressee_gender'].append('none')

            if spr_node.attrib['speaker'] in char:
                new_dict['speaker_gender'].append(char[spr_node.attrib['speaker']])
            else:
                new_dict['speaker_gender'].append('none')
        
        if 'addresseetype' in adr_node.attrib:
            new_dict['addresseetype'].append(adr_node.attrib['addresseetype'])
        else:
            new_dict['addresseetype'].append('none')
        
        # uncomment to add speaker type, 
        # this is commented as many files do not have a speaker type annotated
        # if 'type' in spr_node.attrib:
        #     new_dict['type'].append(spr_node.attrib['type'])
        # else:
        #     new_dict['type'].append('')


    quotes_frame=pd.DataFrame(new_dict)
    #print(quotes_frame[:5])
    # specify filepath e.g. remove info/ to something else
    f_name = 'info/'+xmlname[:-4]+'.tsv'
    quotes_frame.to_csv(f_name, sep="\t")

def subtest_1(char):
    women, men = [], []
    count, men_count = 0, 0
    for gender in char:
        if char[gender] == 'f':
            women.append(gender)
            count += 1
        elif char[gender] == 'm':
            men.append(gender)
            men_count += 1
    return women, men, count, men_count


def find_mentions(features, char_mentions, character_span, char):
    """ Checks whether there are matching mentions from the characters
        and the mentions in the features file. If all mentions of the character
        is a subset of a row of mentions in the features file, 
        then this characters gets assigned the gender that belongs to these
        mentions. The second option find the mentions from the features file
        that have the most matching mentions, as sometimes mistakes are made in
        the annotations and not everything overlaps. 
        The third option checks whether the name of the character is in the features
        or whether the first mention of each row is in the mentions of the character, 
        and the mentions of this row is singular. Could be the case for misspellings etc.
        The fourth option deals with the other misspellings in the mentions of the charactername.
        Returns each option value and the dictionnary for option 1, which already contains
        the gender as it is a perfect match."""
    max = 0
    second_option, third_option, fourth_option = "", "", ""
    for i, mentions in enumerate(features['mentions']):       
        preserved_mention = re.sub(r'(\w+), ', r'\1#', mentions)
        mentions_list = preserved_mention.split('#')
        unique_characters = set(char_mentions[character_span])
        unique_mentions = set(mentions_list)

        if set(char_mentions[character_span]).issubset(mentions_list):
            if features['number'][i] == "sg":
                char[character_span] = features['gender'][i]
            else:
                char[character_span] = "(pl, " + str(features['gender'][i]) + ")"
            break
        
        else:
            count_double = len(list(unique_characters & unique_mentions))
            if count_double > max:
                max = count_double
                if max > 1:
                    second_option = [features['gender'][i], features['number'][i]]
                else:
                    fourth_option = [features['gender'][i], features['number'][i]]

            # third and fourth option are when the characters are not identically spelled as the mention (e.g. ommiting of komma's)
            elif (char_mentions[character_span][0] in mentions_list or mentions_list[0] in set(char_mentions[character_span])) and features['number'][i] == 'sg':
                fourth_option = [features['gender'][i], features['number'][i]]
            elif char_mentions[character_span][0].lower() in ''.join(mentions_list).lower() or char_mentions[character_span][0] in ' '.join((' '.join(mentions_list)).split(' , ')):
                third_option = [features['gender'][i], features['number'][i]]

    return second_option, third_option, fourth_option, char


def assign_gender(char_mentions, features):
    """Loops through the characters and calls find_mentions to match
       the mentions of the character with a gender. It thenk assigns these 
       based on the best option and whether the addressee is singular or plural.
       Returns a dictionnary containing the characters and their assigned gender."""
    char = {}
    # a_root[0] are the character spans
    for character_span in char_mentions:
        second_option, third_option, fourth_option, char = find_mentions(features, char_mentions, character_span, char)
        if not character_span in char:
            if second_option:
                if second_option[1] == "sg":
                    char[character_span] = second_option[0]
                else:
                    #str()-> when value is nan -> this means the mention is in the features file
                    # it just does not have a gender
                    char[character_span] = "(pl, " + str(second_option[0]) + ")"
            elif third_option:
                if third_option[1] == "sg":
                    char[character_span] = third_option[0]
                else:
                    char[character_span] = "(pl, " +str(third_option[0]) + ")"
            else:
                if fourth_option != "":
                    if fourth_option[1] == "sg":
                        char[character_span] = fourth_option[0]
                    else:
                        char[character_span] = "(pl, " + str(fourth_option[0]) + ")"
                elif "_en_" in character_span:
                    char[character_span] = "(pl)"
    return char


def get_char_mentions(char_mentions, adr_root, spr_root):
    '''Returns a dictionnary where the keys are all characters occuring in the fragment,
       and the values are all mentions linked to those characters within both speaker and addressee annotation files.'''

    adr_mentions = adr_root.findall('.//mention')
    spr_mentions = spr_root.findall('.//mention')

    for adr_mention, spr_mention in zip(adr_mentions, spr_mentions):
        if adr_mention.attrib['speaker'] != '':
            char_mentions[adr_mention.attrib['speaker']].append(adr_mention.text.strip()) # .strip 18-5 toegevoegd voor harry -> m ipv f
        
        if spr_mention.attrib['speaker'] != '':
            char_mentions[spr_mention.attrib['speaker']].append(spr_mention.text.strip())


    return char_mentions


def clean_chars(chars):
    """ Returns a dictionnary containing the names of the characters,
        where trailing whitespace and underscores are removed."""
    mentions = {}
    for characters in chars:
        if '_' in characters.attrib['aliases']:
            aliases = characters.attrib['aliases'].replace('_', ' ')
            mentions[characters.attrib['name']] = [aliases.lstrip()] #lstrip remove whitespace before a word _Grish-> Grish
        else:
            mentions[characters.attrib['name']] = [characters.attrib['aliases']]
    return mentions


def main():
    # annotations = the path to the additional addressee annotation files
    #annotations = 'openboek_annotaties_indy'
    annotations = 'riddlecoref_annotations_indy'
    for f in os.listdir(annotations):
        current_f = os.path.join(annotations, f)
        print("\n")
        print(current_f)
        
        # Depending on your file path, you neet to slice the string,
        # so you only end up with the name of the file and not the path.
        #OPENBOEK
        #xmlname = current_f[25:]
        #RIDDLECOREF
        xmlname = current_f[29:]

        addressee_tree = ET.parse(current_f)

        # Depending on which folder you store the speaker quote attribution,
        # the paths in tree and features change.
        #OPENBOEK
        #tree = ET.parse('quotes/'+xmlname)
        #features =pd.read_csv('features/'+xmlname[:-4]+'.tsv', sep='\t')
        #RIDDLECOREF
        tree = ET.parse('riddlecoref/quotes/'+xmlname)
        features =pd.read_csv('riddlecoref/features/'+xmlname[:-4]+'.tsv', sep='\t')

        root = tree.getroot()
        a_root = addressee_tree.getroot()
        
        mentions = clean_chars(a_root[0])
        char_mentions = get_char_mentions(mentions, a_root[1], root[1])
        char = assign_gender(char_mentions, features)

        #subtest 1
        women, men, count, men_count = subtest_1(char)

        if count >= 2:
            print("PASS subtest 1 Bechdel test (woman), count is:",count, "characters:",women)
        else:
            print("FAIL subtest 1 Bechdel test (woman), count is:",count, "characters:",women)

        if men_count >= 2:
            print("PASS subtest 1 reverse Bechdel test (man), count is:",men_count, "characters:",men)
        else:
            print("FAIL subtest 1 reverse Bechdel test (man), count is:",men_count, "characters:",men)

        # creates tsv in folder
        create_tsv(root, char, a_root, xmlname)


if __name__ == '__main__':
    main()