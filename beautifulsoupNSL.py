# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 16:46:00 2016

@author: butticorn
"""

#Import Statements
import os.path
import bs4 as BeautifulSoup     
import urllib.request
import csv

#Cache and CSV file variables to minimize possible errors
url6578 = 'cache/suffolk6578.php'
teachersCsv = 'cache/faculty-education.csv'   

def findli(type):
    if not pdegree[pvar].get_text().find(type) == -1:
        plist[2] = type
        plist[3] = pdegree[pvar].get_text().replace('\xa0', '').split(', ')[1].split('\n')[0]
                        
def findp(type):
    if not pdegree[pvar].find(type) == -1:
        plist[2] = type
        plist[3] = pdegree[pvar].replace('\xa0', '').split(', ')[1]
        
        
if not os.path.isfile(url6578):
    print("Attempting to cashing the data...")
    if not os.path.isdir("cache"):
        os.mkdir("cache")
    main = urllib.request.urlopen("http://www.suffolk.edu/college/6578.php").read().decode("utf-8")
    main = main.replace(u'\u2013', u'-')
    main = main.replace(u'\xa0', u' ')
    main = main.replace(u'\u2019', u"\'")
    outfile = open(url6578, "w")
    outfile.write(main)
    outfile.close()

with open(url6578) as infile:
    soup = BeautifulSoup.BeautifulSoup(infile, 'lxml')

modefind = soup.find('ul', { "class" : "mod-showhide" })
dlen = len(modefind.find_all('h2'))+1 #department count
dcounter = 0
if not os.path.isfile(teachersCsv): #create the teachers.csv file, if not already created
    header = ["Name", "Rank", "Degree", "Institution"]
    print("Creating teachers.csv to store data")
    with open(teachersCsv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
else: 
    print("recreating teachers.csv...")
    os.remove(teachersCsv)
    header = ["Name", "Rank", "Degree", "Institution"]
    print("Creating teachers.csv to store data")
    with open(teachersCsv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
    

#Here's where the "Fun" begins
dcounter = 0
while dcounter < dlen:
    plen = len(modefind.find_all('ul')[dcounter].find_all('li'))
        #finding out how many professors are in the current department
    pcounter = 0
        #resetting the current professor count for each department
    while pcounter < plen:
        plist = ["", "", "", ""]
        rowcount = 0
            #splits pname and rank into a tuple, used variable to slim down for next two
        
        if len(modefind.find_all('ul')[dcounter].find_all('li')[pcounter].find_all('a')) > 0:
            #if length of websites is greater than 0 (has a website)
            profhref = modefind.find_all('ul')[dcounter].find_all('a')[pcounter].get('href')
            #find the href and set to profhref
            if profhref.startswith('http://www.suffolk.edu'): #just in case it starts with prefix
                profhref = profhref.split('http://www.suffolk.edu')[1] #get the current website
                        #About to get full of bullshit code right here...
            pdata = urllib.request.urlopen("http://www.suffolk.edu" + profhref).read().decode("utf-8")
                #Just in case of errors in translation. Most were needed on original site, might as well incorporate.
            pdata = pdata.replace(u'\u2013', u'-')
            pdata = pdata.replace(u'\xa0', u' ')
            pdata = pdata.replace(u'\u2019', u"\'")
                #set current web address to pdata
                #All of these are for the single case instances where it's not following a standard design
            if pdata.find('3>Education') > 0:
                ploc = pdata.find('3>Education')
                pdata2 = pdata[ploc:]
            elif pdata.find('Education\n') > 0:
                ploc = pdata.find('Education\n')
                pdata2 = pdata[ploc:]
            elif pdata.find('<strong>Education') > 0:
                ploc = pdata.find('<strong>Education')
                pdata2 = pdata[ploc:]
            elif pdata.find('Education</strong>') > 0:
                ploc = pdata.find('Education</strong>')
                pdata2 = pdata[ploc:]
            #set temp location to shorten soup            
                
                #temporary psoup size, reduced in next steps in case of lists that follow education                        
            psoup = BeautifulSoup.BeautifulSoup(pdata[ploc:ploc+250], 'lxml') 
                #if there's a header following education, location 2 is before that
            if len(psoup.find_all('h3')) > 0:
                ploc2 = pdata2.find('<h3')
            else: #if no header following, use the last ul as a point set location to after that
                if len(psoup.find_all('ul')) > 0:
                    ploc2 = pdata2.find('/ul>')+5
                else: #if no ul because paragraph form, do the same thing but with paragraph tag
                    ploc2 = pdata2.find('/p>')+4
                    #overwrite psoup to new end location
            pdata2 = pdata2[:ploc2]
            psoup = BeautifulSoup.BeautifulSoup(pdata2, 'lxml')
                #determine if psoup is list form or paragraph form
            if not len(psoup.find_all('li')) == 0:
                pdegree = psoup.find_all('li')
                countli = 1
            else:
                if ploc == -1:
                    pdegree = psoup
                    #to cover instances where p is somewhere else or not used
                if ploc > 0:
                    if len(psoup.find_all('p')) > 1:
                        pdegree = psoup.find_all('p')[1].get_text().split('\n ')
                    elif len(psoup.find_all('p')) == 1:
                        pdegree = psoup.find_all('p')[0].get_text().split('\n ')
                    else:
                        pdegree = psoup.find_all('body')[0].get_text().split('\n')
                        pdegree = pdegree[1:]
                countli = 0
            lenpdegree = len(pdegree)
            pvar = 0
                    
            while pvar < lenpdegree:
                #if in list format
                if countli == 1:
                    pname = modefind.find_all('ul')[dcounter].find_all('li')[pcounter].get_text().split(', ')
                    #set name and rank, and clear previous degree and institution to prepare for new
                    plist[0] = pname[0]
                    plist[1] = pname[1]
                    plist[2] = ''
                    plist[3] = ''
                    #checking current li for the following. will skip if it can't find it's trigger
                    findli('PhD')
                    findli('MS')
                    findli('BS')
                    #only use this mode if a findli commands worked
                    if not plist[2] == '':
                        with open(teachersCsv, 'a', newline='') as csvfile:
                        #'a' to append instead of overwrite the first line each time
                            writer = csv.writer(csvfile)
                            writer.writerow(plist)
                        rowcount += 1
                    #will only be used if it's the last li and there haven't been any additions
                    if plist[2] == '' and (pvar+1) == lenpdegree and rowcount == 0:
                        with open(teachersCsv, 'a', newline='') as csvfile:
                        #'a' to append instead of overwrite the first line each time
                            writer = csv.writer(csvfile)
                            writer.writerow(plist)
                    pvar += 1
                #if in paragraph form or break form
                if countli == 0:
                    pname = modefind.find_all('ul')[dcounter].find_all('li')[pcounter].get_text().split(', ')
                    #set name and rank, and clear previous degree and institution to prepare for new
                    plist[0] = pname[0]
                    plist[1] = pname[1]
                    plist[2] = ''
                    plist[3] = ''
                    #check current paragraph for following. will skip if can't find it's trigger
                    findp('PhD')
                    findp('MS')
                    findp('BS')
                    #will only be used if a findp command worked
                    if not plist[2] == '':
                        with open(teachersCsv, 'a', newline='') as csvfile:
                        #'a' to append instead of overwrite the first line each time
                            writer = csv.writer(csvfile)
                            writer.writerow(plist)
                        rowcount += 1
                    #will only be used if no commands worked and last paragraph item
                    if plist[2] == '' and (pvar+1) == lenpdegree:
                        with open(teachersCsv, 'a', newline='') as csvfile:
                        #'a' to append instead of overwrite the first line each time
                            writer = csv.writer(csvfile)
                            writer.writerow(plist)
                    pvar += 1
        else:
            #if there was no education information
            pname = modefind.find_all('ul')[dcounter].find_all('li')[pcounter].get_text().split(', ')
            #setting name and rank. plist 2 and 3 are empty
            plist[0] = pname[0]
            plist[1] = pname[1]
            plist[2] = ''
            plist[3] = ''
            with open(teachersCsv, 'a', newline='') as csvfile:
                            #'a' to append instead of overwrite the first line each time
                writer = csv.writer(csvfile)
                writer.writerow(plist)
        pcounter += 1
        
    dcounter += 1
    #move to next department until finished with all departments

