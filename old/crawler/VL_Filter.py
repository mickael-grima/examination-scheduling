

#!/usr/bin/python



import pickle
import re
import csv
import editdistance

kennungen = dict()
csvfile = open('SzenarioergebnisSoSe2016.csv', 'rb')
spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
for row in spamreader:
    kennungen[row[1]] = row[0]
csvfile.close()

anmeldungen = dict()

filename = "anmeldungen.p"
countdict = pickle.load(open(filename, "rb"))
for description in countdict:
    for key in countdict[description]:
        # only take vorlesungen
        if re.match(".*\sVO\s.*", key) is None:
            continue
        if len(re.split("VO\s", key)) != 2:
            print "ERROR! UNEXPECTED FORMAT: %s" %key
            continue
        key = re.split("VO\s", key)[1]
        key = reduce(lambda x, y: x + y, map(unichr, key))
        print key.encode('utf-8', 'ignore')
        
        if re.match(".*\s(I|\d).*", key) is not None:
            print("CAREFUL!", key)
        else:
            # search for matching key
            for matching_key in kennungen:
                if editdistance.eval(key, matching_key) <= 2:
                    print key
                    print matching_key
                    continue
