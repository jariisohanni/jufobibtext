from pybtex.database.input import bibtex
from pylatexenc.latex2text import LatexNodes2Text

import requests
import urllib.parse
import json
from itertools import chain
from difflib import SequenceMatcher

#Accepted book publishers
book_pulisher = ['ACM', 'Springer', 'Elsevier', 'CRC press', 'John Wiley & Sons', 'Wiley', 'Prentice hall'] 

#This list contains entries that author has inspected
verified = ['jain1988algorithms','minkowski1910geometrie','pennebaker1992jpeg','sokal1958statistical','sharma1995applied','dunn1973fuzzy','alpaydin2020introduction','deisenroth2020mathematics','shalev2014understanding','hristev1998ann','haykin2009neural','goodfellow2016deep','kingma2014adam','zeiler2012adadelta','hirsch2022light','NokiaN9','bayer','ISO17321','ISO2846','ISO13586','isohanni_2024_11079897','jari_isohanni_2023_7749912','Harvey','japkowicz2011evaluating']

def findJournalFromJufo(journal,publisher, isbn = None, issn = None):

    if publisher == None and journal.startswith('IEEE'):
        publisher = 'IEEE'

    #nimi	Julkaisukanavan nimi	a-Z0-9	50	Voit hakea julkaisukanavaa nimellä tai sen osalla
    #isbn	ISBN tunniste (juuri)	0-9-	20	ISBN-tunnisteen juuri numerokoodina, esim. 978-963-46.
    #Julkaisukanavatietokannassa on vain ISBN-tunnisteen juuriosa eli kustantajan tunniste.
    #issn	ISSN tunniste	0-9-	10	
    #Julkaisukanavan ISSN-tunniste

    #lyhenne	Konferenssin lyhenne	a-Z0-9	20	Konferenssin vakiintunut lyhenne
    #tyyppi	Julkaisukanavan tyyppi	1-3	1

    url_journal = journal[:journal.rfind("&")] #Cut from &, maybe could use replace too
    

    url = None
    if isbn != None:
        url = "https://jufo-rest.csc.fi/v1.1/etsi.php?nimi="+urllib.parse.quote(url_journal)
    elif isbn != None : #TODO
        url = "https://jufo-rest.csc.fi/v1.1/etsi.php?nimi="+urllib.parse.quote(url_journal)
    else: #TODO
        url = "https://jufo-rest.csc.fi/v1.1/etsi.php?nimi="+urllib.parse.quote(url_journal)[:50]
    r = requests.get(url)

    if(r.status_code != 200):
        return False
    
    json_object = r.json()
    for entry in json_object:
        fixedName = journal.replace("&", "and")
        if(entry['Name'].lower() == journal.lower()  or entry['Name'].lower() == fixedName.lower() ):
            entryurl = entry['Link']
            entry_r = requests.get(entryurl)
            json_object_entry = entry_r.json()

            for entry_item in json_object_entry:
                if publisher == None:
                    if len(json_object_entry) == 1 and int(entry_item['Level']) > 0:
                        return True
                elif(int(entry_item['Level']) > 0 and SequenceMatcher(None, entry_item['Publisher'].lower(), publisher.lower()).ratio() > 0.7 ):
                    return True
                elif (int(entry_item['Level']) > 0 and  publisher.lower()  in entry_item['Publisher'].lower()):
                    return True
                #else:
                    #print("No match:" + entry_item['Publisher'] + "And" + publisher)

    #print(r.json()) 
    return False

def processBibFiles(entries):

    ok = 0

    print("NOT PROCESSED:")

    for key in entries:
        item = entries[key]

        if "jufo" in item.fields: #You can add Jufo to .bib entries -> considered ok sources
            ok = ok + 1
            continue

        if key in verified: #Verified sources added directly to source
            ok = ok + 1
            continue

        if "notok" in item.fields: #recognised as not ok, so no need to process
            continue


        if item.type == "article":
            journal = LatexNodes2Text().latex_to_text(item.fields['journal'])
            publisher = ""
            if 'publisher' in item.fields.keys():
                publisher = LatexNodes2Text().latex_to_text(item.fields['publisher'])
            year = item.fields['year']

            if findJournalFromJufo(journal,publisher) == False:
                    print (key + " -> Tarkista: " + journal)
            else:
                ok = ok + 1

        elif item.type == "book":
 
            if 'publisher' in item.fields.keys():
                publisher = item.fields['publisher']
                publisher = LatexNodes2Text().latex_to_text(publisher)

                if publisher not in book_pulisher:
                    print ("KIRJA:" + key + " / " + publisher +" -> Tarkista")
        else:
             print (key + " -> Tarkista")

    print("DONE:" + str(ok) + " / " +  str(len(entries.keys())))

    print("THESE NOT OK :")
    for key in entries:
        item = entries[key]

        if "notok" in item.fields: #recognised as not ok, so no need to process
            print(key)


parser = bibtex.Parser()
bib_data = parser.parse_file('Bib_chapter2.bib')

#Total entries in .bib file:438

print("Total entries in .bib file:" + str(len(bib_data.entries.keys())))

processBibFiles(bib_data.entries)

