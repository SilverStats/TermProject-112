# for creating the play-by-play files
# some user cooperation is required in terms of file storage at this point
# they need to have the right directories, programs saved/created

import subprocess as sp
import os
import Parser
import cPickle as pickle
import zlib

def getBattingStats(player, startYear, endYear):
    plays = {}
    players = {}
    players[str(player)] = player # dictionary for easy reference
    rPlayer = players[str(player)] # r for Retrosheet
    with open("C:/Retro/AlphaBatter/%s%s" % (
        rPlayer.id[0], rPlayer.id[1])) as playFile:
        events = pickle.load(playFile)
    parser = Parser.Parser("C:/Retro/Empty.txt")
    if str(player) in events: parser.data = events[str(player)]
    else: return None # stops the function--Screens.py uses this fact
    plays = parser.parse()
    for play in plays:
        if int(play.year) >= startYear and int(play.year) <= endYear:
            rPlayer.addBatterEvent(play)
    return (players, rPlayer)
    
def getStats2(): # console-based
    id = raw_input("Enter a player id: ")
    firstName = raw_input("Enter the player's first name: ")
    lastName = raw_input("Enter the player's last name: ")
    position = raw_input("Enter the player's position: ")
    (plays, players) = ({}, {})
    players[id] = Parser.RetrosheetPlayer(id, firstName, lastName, position)
    player = players[id]
    year = raw_input("Enter a year of interest: ")
    files = getFiles(int(year))
    for filename in files:
        if year in filename:
            events = Parser.Parser("C:/Retro/Plays/%s" % filename)
            plays[str(year)] = events.parse()
            for play in plays[str(year)]:
                player.addBatterEvent(play)
    stat = raw_input("Enter the stat you want to calculate: ")
    print players[str(player)].seasons[str(year)].stats[str(stat)]
    # dictionary makes it easy to reference player in question

def getFiles(year): # speeds up the process without data-dumping!
    files = os.listdir("C:/Retro/Plays")
    length = len(files)
    digits = 4
    fileYear = int(files[length/2][0:digits])
    while fileYear != year:
        if fileYear > year: files = files[0:length/2]
        else: files = files[length/2:]
        length = len(files)
        fileYear = int(files[length/2][0:digits])
    return files

def makeEventFiles(year1, year2): # this is for the first time only
    plays = []
    filenames = {}
    for year in xrange(year1, year2+1):
        decade = year - year%10
        path = "C:/Retro/%sseve" % str(decade)
        for filename in os.listdir(path):
            if (((filename[0:7] + ".txt") not in os.listdir("C:/Retro/Plays"))
                and (filename.endswith(".EVN") or filename.endswith(".EVA"))):
                # need to add pitcher responsibility fields
                # also need game log files to get pitcher wins (a terrible stat)
                sp.Popen("cd /Retro & bevent -y %s %s/%s >C:/Retro/Plays/%s.txt"
                         %(year, path, filename, filename[0:7]), shell=True)
import shutil
import csv

def moveTeamFiles(year1, year2):
    for year in xrange(year1, year2+1):
        decade = year-year%10
        path = "C:/Retro/%sseve" % str(decade)
        for filename in os.listdir(path):
            if "TEAM" in filename and filename not in os.listdir("C:/Retro"):
                shutil.copy(path + "/" + filename,
                            "C:/Retro/" + filename)

def makeRosters(year1, year2): # puts them all in one folder
    if not os.path.exists("C:/Retro/Rosters"): os.makedirs("C:/Retro/Rosters")
    for year in xrange(year1, year2+1):
        decade = year-year%10
        path = "C:/Retro/%sseve" % str(decade)
        for filename in os.listdir(path):
            if (filename.endswith(".ROS") and filename not in
                os.listdir("C:/Retro/Rosters")):
                shutil.copy(path + "/" + filename,
                            "C:/Retro/Rosters/" + filename[0:7] + ".txt")

def makeRosterList():
    players = []
    playerDict = {}
    a = os.listdir("C:/Retro/Rosters")
    a.reverse()
    for filename in a:
        with open("C:/Retro/Rosters/"+filename, "r") as roster:
            players += list(csv.reader(roster))
    for player in players:
        playerDict[player[0]] = player
        playerDict[player[2] + " " + player[1]] = player
    # creates a hash based on name and id
    return playerDict

def makeDateSortedFiles(year): # ended up not using this--it's slower than ever
    (year, plays, playsDict) = (str(year), [], PlayDict())
    yearIndex = (3,7)
    months = ["03","04","05","06","07","08","09","10","11"] # no games Dec-Feb
    days = ["01","02","03","04","05","06","07","08","09","10","11","12","13",
            "14","15","16","17","18","19","20","21","22","23","24","25","26",
            "27","28","29","30","31"]
    for month in months:
        for day in days:
            playsDict.addDay(month, day)
    for filename in os.listdir("C:/Retro/Plays"):
        if year in filename:
            with open("C:/Retro/Plays/"+filename, "r") as team:
                events = list(csv.reader(team))
                for event in events:
                    playsDict.addDayPlay(event)
    for month in months:
        for day in days:
            with open("C:/Retro/DateSorted/%s%s"%(month,day),"w") as date:
                pickle.dump(playsDict.playsDict[year+str(month)+str(day)], date)
    
def makeBatterAlphabetizedFiles(letter):
    plays = []
    playsDict = PlayDict()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    batterIndex = 9
    for letter1 in alphabet:
        playsDict.addLetter(letter, letter1)
    for filename in os.listdir("C:/Retro/Plays"):
        with open("C:/Retro/Plays/"+filename, "r") as team:
            events = list(csv.reader(team))
            for event in events:
                if event[batterIndex][0] == letter:
                    playsDict.addBatterPlay(event)
    for letter1 in alphabet:
        with open("C:/Retro/AlphaBatter/%s%s"%(letter,letter1),"w")as ab:
            pickle.dump(playsDict.playsDict[letter+letter1], ab)

def makePitcherAlphabetizedFiles(letter):
    plays = []
    playsDict = PlayDict()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    pitcherIndex = 11
    for letter1 in alphabet:
        playsDict.addLetter(letter, letter1)
    for filename in os.listdir("C:/Retro/Plays"):
        with open("C:/Retro/Plays/"+filename, "r") as team:
            events = list(csv.reader(team))
            for event in events:
                if event[pitcherIndex][0] == letter:
                    playsDict.addPitchPlay(event)
    for letter1 in alphabet:
        with open("C:/Retro/AlphaPitcher/%s%s"%(letter,letter1),"w")as ab:
            pickle.dump(playsDict.playsDict[letter+letter1], ab)

class PlayDict(object):

    def __init__(self):
        self.playsDict = {}

    def addLetter(self, first, second):
        self.playsDict[first+second] = {}

    def addDay(self, month, day):
        self.playsDict[month+day] = []

    def addBatterPlay(self, play):
        batterIndex = 9
        if play[batterIndex] in self.playsDict[play[batterIndex][0]+play[
            batterIndex][1]]:
            self.playsDict[play[batterIndex][0]+play[batterIndex][1]][play[
            batterIndex]] += [play]
        else:  self.playsDict[play[batterIndex][0]+play[batterIndex][
            1]][play[batterIndex]] = [play]

    def addPitchPlay(self, play):
        pitcherIndex = 11
        if play[pitcherIndex] in self.playsDict[play[pitcherIndex][0]+play[
            pitcherIndex][1]]:
            self.playsDict[play[pitcherIndex][0]+play[pitcherIndex][1]][play[
            pitcherIndex]] += [play]
        else: self.playsDict[play[pitcherIndex][0]+play[pitcherIndex][
            1]][play[pitcherIndex]] = [play]

    def addDayPlay(self, play):
        (monthIndex, dayIndex) = ((7,8),(9,10))
        self.playsDict[play[0][monthIndex[0]:dayIndex[1]+1]] += [play]


if __name__ == "__main__":
    #makeRosters(1940, 2012)
    #makeBatterAlphabetizedList()
    #getStats2()
    pass

