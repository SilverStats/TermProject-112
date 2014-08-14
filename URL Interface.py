# URL Interface.py
# for downloading the Retrosheet files

import FileWriter
import urllib
import os
import subprocess as sp
import zipfile
import shutil
import cPickle as pickle

def setFolders():
    if not os.path.exists("C:/Retro"): os.makedirs("C:/Retro")
    if not os.path.exists("C:/Retro/Plays"): os.makedirs("C:/Retro/Plays")
    if not os.path.exists("C:/Retro/Rosters"): os.makedirs("C:/Retro/Rosters")
    if not os.path.exists("C:/Retro/AlphaBatter"):
        os.makedirs("C:/Retro/AlphaBatter")
    if not os.path.exists("C:/Retro/AlphaPitcher"):
        os.makedirs("C:/Retro/AlphaPitcher")
    open("C:/Retro/Empty.txt", "w").close() # for the name-based searches
    

def getPrograms():
    urllib.urlretrieve("http://www.retrosheet.org/bevent.zip",
                       "C:/Retro/Bevent.zip")
    urllib.urlretrieve("http://www.retrosheet.org/box.zip",
                       "C:/Retro/Box.zip")
    urllib.urlretrieve("http://www.retrosheet.org/bgame.zip",
                       "C:/Retro/Bgame.zip")

def getDecade(decade):
    decade = str(decade)
    urllib.urlretrieve("http://www.retrosheet.org/events/%sseve.zip"%decade,
                       "C:/Retro/%sseve.zip"%decade)

def unzipProgram(filename):
    zipped = zipfile.ZipFile("C:/Retro/%s.zip"%filename)
    zipped.extractall("C:/Retro")

def unzipPrograms():
    for program in ("bevent", "bgame", "box"):
        unzipProgram(program)

def unzipDecade(decade):
    decade = str(decade)
    if not os.path.exists("C:/Retro/%sseve"%decade):
        os.makedirs("C:/Retro/%sseve"%decade)
    zipped = zipfile.ZipFile("C:/Retro/%sseve.zip"%decade)
    zipped.extractall("C:/Retro/%sseve"%decade)

# rest is from FileWriter, modified to avoid messing up what I have
# mostly for testing purposes--I'll use FileWriter at the end

def moveTeamFiles(year1, year2):
    for year in xrange(year1, year2+1):
        decade = year-year%10
        path = "C:/Retro/%ssOeve" % str(decade)
        for filename in os.listdir(path):
            if "TEAM" in filename and filename not in os.listdir("C:/Retro"):
                shutil.copy(path + "/" + filename,
                            "C:/Retro/" + filename)

def makeEventFiles(year1, year2): # this is for the first time only
    plays = []
    filenames = {}
    for year in xrange(year1, year2+1):
        decade = year - year%10
        path = "C:/Retro/%ssOeve" % str(decade)
        for filename in os.listdir(path):
            if (((filename[0:7] + ".txt") not in os.listdir("C:/Retro/OPlays"))
                and (filename.endswith(".EVN") or filename.endswith(".EVA"))):
                # need to add pitcher responsibility fields
                # also need game log files to get pitcher wins (a terrible stat)
                sp.Popen("cd /Retro & bevent -y %s %s/%s"%(year,path,filename)+
                         ">C:/Retro/OPlays/%s.txt"%filename[0:7], shell=True)

def makeRosters(year1, year2): # puts them all in one folder
    if not os.path.exists("C:/Retro/ORosters"): os.makedirs("C:/Retro/ORosters")
    for year in xrange(year1, year2+1):
        decade = year-year%10
        path = "C:/Retro/%ssOeve" % str(decade)
        for filename in os.listdir(path):
            if (filename.endswith(".ROS") and filename not in
                os.listdir("C:/Retro/ORosters")):
                shutil.copy(path + "/" + filename,
                            "C:/Retro/ORosters/" + filename[0:7] + ".txt")


def makeBatterAlphabetizedFiles(letter):
    plays = []
    playsDict = PlayDict()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    batterIndex = 9
    for letter1 in alphabet:
        playsDict.addLetter(letter, letter1)
    for filename in os.listdir("C:/Retro/OPlays"):
        with open("C:/Retro/OPlays/"+filename, "r") as team:
            events = list(csv.reader(team))
            for event in events:
                if event[batterIndex][0] == letter:
                    playsDict.addPitchPlay(event)
    for letter1 in alphabet:
        with open("C:/Retro/OAlphaBatter/%s%s"%(letter,letter1),"w")as ab:
            pickle.dump(playsDict.playsDict[letter+letter1], ab)
            
def makePitcherAlphabetizedFiles(letter):
    plays = []
    playsDict = PlayDict()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    pitcherIndex = 11
    for letter1 in alphabet:
        playsDict.addLetter(letter, letter1)
    for filename in os.listdir("C:/Retro/OPlays"):
        with open("C:/Retro/OPlays/"+filename, "r") as team:
            events = list(csv.reader(team))
            for event in events:
                if event[pitcherIndex][0] == letter:
                    playsDict.addPitchPlay(event)
    for letter1 in alphabet:
        with open("C:/Retro/OAlphaPitcher/%s%s"%(letter,letter1),"w")as ab:
            pickle.dump(playsDict.playsDict[letter+letter1], ab)

class PlayDict(object):

    def __init__(self):
        self.playsDict = {}

    def addLetter(self, first, second):
        self.playsDict[first+second] = {}

    def addBatterPlay(self, play):
        batterIndex = 9
        try: self.playsDict[play[batterIndex][0]+play[batterIndex][1]][play[
            batterIndex]] += [play]
        except KeyError: self.playsDict[play[batterIndex][0]+play[batterIndex][
            1]][play[batterIndex]] = [play]

    def addPitchPlay(self, play):
        pitcherIndex = 11
        try: self.playsDict[play[pitcherIndex][0]+play[pitcherIndex][1]][play[
            pitcherIndex]] += [play]
        except KeyError:self.playsDict[play[pitcherIndex][0]+play[pitcherIndex][
            1]][play[pitcherIndex]]=[play]

def finalFileWriting():
    decade = 2010
    endYear = 2013
    setFolders()
    print "Downloading files..."
    getPrograms()
    unzipPrograms()
    getDecade(decade)
    unzipDecade(decade)
    print "Making play-by-play files..."
    FileWriter.moveTeamFiles(decade, endYear)
    FileWriter.makeRosters(decade, endYear)
    FileWriter.makeEventFiles(decade, endYear)
    print "Setting up events..."
    for letter in "abcdefghijklmnopqrstuvwxyz":
        FileWriter.makeBatterAlphabetizedFiles(letter)
        FileWriter.makePitcherAlphabetizedFiles(letter)
    print "Done!"

if __name__ == "__main__":
    finalFileWriting()
