#!/usr/bin/env python

import pandas as pd
import xml.etree.ElementTree as ET

def main():
    """Creates tsv files with id, quote, addressee and empty addresseetype.
       Annotater can fill this in a sheet and save this. 
       to_xml.py will insert the types back in the xml annotions files."""
    #f = 'zijndood(12).xml'
    f = input("Annotated xml file that needs addresseetypes:")
    tree = ET.parse(f)
    print(tree)
    
    root = tree.getroot()
    

    quotes_mentions = root[1]
    # q_dict = {}
    # q_dict['quote'] = []
    # q_dict['addresseetype'] = ''
    # q_dict['addressee'] = []
    # q_dict['id'] = []

    attributes = ['id', 'quote', 'addressee', 'addresseetype']
    q_dict = {column : [] for column in attributes}
    for quotes in quotes_mentions:
        if quotes:
            for i in quotes:
                if 'quote' == i.tag:
                    # complete = ET.tostring(i)
                    # quote = re.sub('<[/,a-z =\"0-9\_A-Z>]+>', '', str(complete))
                    # speech = re.sub(r'b\'\\\'(.*)', r'\1', quote)
                    # sentence = re.sub(r'\\\'.*', '', speech)
                    # q_dict['quote'].append(sentence)
                    q_dict['quote'].append(''.join(quotes.itertext()))
                    q_dict['id'].append(i.attrib['id'])
                    if 'speaker' in i.attrib:
                        addressees = i.attrib['speaker']
                        q_dict['addressee'].append(addressees)

            if 'quote' == quotes.tag:
                # complete = ET.tostring(quotes)
                # quote = re.sub('<[/,a-z =\"0-9\_A-Z>]+>', '', str(complete))
                # speech = re.sub(r'b\'\\\'(.*)', r'\1', quote)
                # sentence = re.sub(r'\\\'.*', '', speech)
                # q_dict['quote'].append(sentence)
                q_dict['quote'].append(''.join(quotes.itertext()))
                q_dict['id'].append(quotes.attrib['id'])
                if 'speaker' in quotes.attrib:
                    addressees = quotes.attrib['speaker']
                    q_dict['addressee'].append(addressees)
            else:
                print(quotes)
        elif 'quote' == quotes.tag:
            q_dict['quote'].append(quotes.text)
            q_dict['id'].append(quotes.attrib['id'])
            if 'speaker' in quotes.attrib:
                addressees = quotes.attrib['speaker']
                q_dict['addressee'].append(addressees)
        else:
            print(quotes)

    quotes_frame=pd.DataFrame(q_dict)
    print(quotes_frame)
    new_name = f[:-4] + '_addtype.tsv'
    quotes_frame.to_csv(new_name, sep="\t")


if __name__ == '__main__':
    main()
