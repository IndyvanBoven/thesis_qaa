#!/usr/bin/env python

import pandas as pd
import xml.etree.ElementTree as ET

def main():
    current_f = input("Annotated file that needs added addresseetypes to xml:")
    xmlname = input("What should the name be of the annotated xml file?")
    addtypes = pd.read_csv(current_f + '_addtype.tsv', sep='\t')

    addressee_tree = ET.parse(current_f + '.xml')
    addr_tree = addressee_tree.getroot()

    for quotes in addr_tree[1]:
        if quotes:
            for i in quotes:
                if 'quote' == i.tag:
                    adtype = ''.join(list(addtypes[addtypes['id'] == i.attrib['id']]['addresseetype']))

                    i.set('addresseetype', adtype)
                    if adtype == 'none' or adtype == '_unknowable':
                        i.set('speaker', adtype)
            if 'quote' == quotes.tag:
                    adtype = ''.join(list(addtypes[addtypes['id'] == quotes.attrib['id']]['addresseetype']))

                    quotes.set('addresseetype', adtype)
                    if adtype == 'none' or adtype == '_unknowable':
                        quotes.set('speaker', adtype)

        elif 'quote' == quotes.tag:
            print(quotes.attrib['id'])
            adtype = ''.join(list(addtypes[addtypes['id'] == quotes.attrib['id']]['addresseetype']))

            quotes.set('addresseetype', adtype)
            if adtype == 'none' or adtype == '_unknowable':
                 quotes.set('speaker', adtype)


    addressee_tree.write(xmlname)



if __name__ == '__main__':
    main()