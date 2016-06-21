import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pickle

driver = webdriver.Chrome(executable_path="/home/roland/Downloads/chromedriver")

driver.get("http://www.campus.tum.de")
time.sleep(10)
#ga79wis

filename = "anmeldungen.p"

teilnehmerzahlen = dict()
start = 950155245
start = 950161365

index = start
counter = 0
while index < 950240393:
    index = start + counter
    url = "https://campus.tum.de/tumonline/sa9.lvAnmeldInfoSeite?pStPersonNr=1744253&pStpSpNr=%d&pOpener=" %(index)
#    print url
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content)
    meta = soup.find("table", { "id" : "idTopPageHeader" }).find("span", { "class" : "s" }).span
    tnmr = soup.find("table", {"class" : "list"}).findAll("tr")
    tns = map( lambda x: x.find("td", {"headers" : "hdrTN hdrTNIST"}), tnmr )
    tns = [ int(tn.text) for tn in tns if tn is not None ]
    if meta is not None and len(tns) > 0:
 #       print (meta.text.encode("utf-8"))
  #      print (sum(tns))
  #      print tns, sum(tns)
        teilnehmerzahlen[index] = { meta.text.encode("utf-8") : sum(tns) }
    else: 
   #     print "-"
        pass
    
    counter = counter + 1
    
    if len(teilnehmerzahlen) % 100 == 0:
        pickle.dump(teilnehmerzahlen, open(filename, "wb"))
        print(len(teilnehmerzahlen)), 1.0*(950240393-index)/(950240393-start)

driver.close()