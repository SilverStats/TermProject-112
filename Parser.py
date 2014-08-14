# play-by-play parser

# from http://stackoverflow.com/questions/11539938/
# reading-from-a-file-directly-into-a-2d-list-python

###

import csv
from datetime import datetime, date

###

# based on mrallen1's parser found online

class RetrosheetPerson(object):
    #__slots__ = ['type', 'id', 'name', 'position']

    def __init__(self, id, firstName, lastName, position):
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.name = firstName + " " + lastName 
        self.position = position
        self.type = None

    def __str__(self):
        return self.id # this also helps in the dictionary references

    def __repr__(self):
        return self.id
        #return "%s: %s (%s) - %s" % (self.type,self.name,self.id,self.position)

class RetrosheetPlayer(RetrosheetPerson):
    #__slots__ = ['type', 'id', 'name', 'position']
    players = []

    def __init__(self, id, firstName, lastName, position):
        super(RetrosheetPlayer, self).__init__(id, firstName,lastName,position)
        self.type = 'player'
        self.seasons = {}
        RetrosheetPlayer.players += [self.id] # for dropdowns

    def addBatterEvent(self, event):
        if event.batter != self.id:
            if self.id in [event.firstBase,event.secondBase,event.thirdBase]:
                self.updateBaserunning(event)
                if event.id not in self.season.games:
                    self.season.games[event.id] = event.id
            return None # stops from adding other players' stats to this one's         
        if event.year not in self.seasons:
            self.season = PlayerSeason(event.year)
            self.seasons[event.year] = self.season
        self.season = self.seasons[event.year]
        if event.team not in self.season.teams and event.team != "":
            self.season.teams += [event.team]
            # add to teams--this yields the "+" for multi-team seasons
        if event.id not in self.season.games:
            self.season.games[event.id] = event.id
        self.addStats(event)

    def addStats(self, event):
        self.season.stats["PA"] += event.batterEvent
        self.season.stats["AB"] += event.atBat
        self.season.stats["PH"] += (event.pinchHit == "T")
        self.season.stats["SH"] += (event.SH == "T")
        self.season.stats["SF"] += (event.SF == "T")
        self.season.stats["RBI"] += int(event.RBI)
        self.season.stats["1B"] += (event.hitVal == "1")
        self.season.stats["2B"] += (event.hitVal == "2")
        self.season.stats["3B"] += (event.hitVal == "3")
        self.season.stats["HR"] += (event.hitVal == "4")
        self.season.stats["R"] += (event.hitVal == "4")
        self.season.stats["H"] += (int(event.eventType) in [20,21,22,23])
        self.season.stats["BB"] += (event.eventType == "14")
        self.season.stats["IBB"] += (event.eventType == "15")
        self.season.stats["HBP"] += (event.eventType == "16")
        self.season.stats["SO"] += (event.eventType == "3")
        self.season.stats["DP"] += (event.outsMade == "2")
        self.season.stats["G"] = len(self.season.games)
        advances = self.calcAdvances(event)
        self.season.stats["AO"] += advances[0]
        self.season.stats["AC"] += advances[1]

    def calcAdvances(self, event):
        advances = [4,0]
        runners = [event.firstBase, event.secondBase, event.thirdBase]
        endings = [int(event.firstDest), int(event.secondDest),
                   int(event.thirdDest)]
        for index in xrange(3):
            if (endings[index] > 0):
                advances[1] += min(4, endings[index]) - index - 1
        for runner in runners:
            if (runner != ""):
                advances[0] += 3 - runners.index(runner)
        advances[1] += min(4, int(event.batterDest))
        return advances
                
        
    def calcSummaryBattingStats(self):
        for year in self.seasons:
            self.season = self.seasons[year]
            if self.season.stats["AB"] > 0:
                self.season.stats["BA"] = float(
                    self.season.stats["H"])/self.season.stats["AB"]
                self.season.stats["TB"] = (self.season.stats["1B"]+
                                            2*self.season.stats["2B"]+
                                            3*self.season.stats["3B"]+
                                            4*self.season.stats["HR"])
                self.season.stats["OBP"] = (
                    float(self.season.stats["H"])+self.season.stats["BB"]+
                    self.season.stats["HBP"])/(self.season.stats["AB"]+
                                               self.season.stats["BB"]+
                                               self.season.stats["HBP"]+
                                               self.season.stats["SF"])
                self.season.stats["SLG"] = (float(self.season.stats["TB"])/
                                            self.season.stats["AB"])
                self.season.stats["OPS"] = (self.season.stats["OBP"]+
                                            self.season.stats["SLG"])
                self.season.stats["AP"] = (float(self.season.stats["AC"])/
                                           self.season.stats["AO"])

    def updateBaserunning(self, event):
        runners = [event.firstBase, event.secondBase, event.thirdBase]
        for runner in runners:
            if runner == self.id:
                base = runners.index(runner)+1
        if "SB%s"%(base+1) in event.outcome: self.season.stats["SB"] += 1
        if "CS%s"%(base+1) in event.outcome: self.season.stats["CS"] += 1
        if base == 1:
            if int(event.firstDest) in (4, 5, 6): self.season.stats["R"] += 1
        elif base == 2:
            if int(event.secondDest) in (4, 5, 6): self.season.stats["R"] += 1
        elif base == 3:
            if int(event.thirdDest) in (4, 5, 6): self.season.stats["R"] += 1
            
        # still not dealing with runs, baserunning stats, GIDP, or fielding
        # references dictionary to get the correct season stat
        
    def addPitcherEvent(self, event):
        if event.pitcher != self.id: return None
        # not going to calculate this because pitcher wins are very difficult
        # pitching will have to wait for a future version

class PlayerSeason(RetrosheetPlayer): # not an intuitive subclass, but it works

    def __init__(self, year):
        self.name = year
        self.year = year
        self.games = {}
        self.teams = []
        (self.PA, self.AB, self.runs, self.hits, self.doub, self.trip, self.HR,
         self.RBI, self.SB, self.CS, self.BB, self.SO, self.DP, self.HBP,
         self.SH, self.SF, self.IBB, self.pinchHits, self.sing, self.AO,
         self.AC) = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
        self.stats = {"PA":self.PA, "AB":self.AB, "R":self.runs, "H":self.hits,
                      "2B":self.doub,"3B":self.trip,"HR":self.HR,"1B":self.sing,
                      "RBI":self.RBI, "SB":self.SB, "CS":self.CS, "BB":self.BB,
                      "SO":self.SO, "DP":self.DP, "HBP":self.HBP, "SH":self.SH,
                      "SF":self.SF, "IBB":self.IBB, "PH":self.pinchHits,
                      "AO":self.AO, "AC":self.AC}
        
        
class Event(object):

    def __init__(self):
        self.keys = {0:"Unknown", 1:"None", 2:"Out", 3:"Strikeout", 4:"SB",
                     5:"Indifference", 6:"CS", 7:"Pickoff Error", 8:"Pickoff",
                     9:"WP", 10:"PB", 11:"Balk", 12:"Advance", 13:"Foul error",
                     14:"BB", 15:"IBB", 16:"HBP", 17:"Interference", 18:"E",
                     19:"FC", 20:"1B", 21:"2B", 22:"3B", 23:"HR", 24:"Missing"}

    def __str__(self):
        return self.keys[int(self.eventType)]
    

class Parser(object):

    def __init__(self, filename):
        self.filename = filename
        self.plays = []
        dictData = {}
        with open(filename, 'r') as inf:
            data = list(csv.reader(inf, skipinitialspace=True))
            data = [i for i in data if i] # from stackOverflow--skips blanks
            self.data = data

    def parse(self): # this is just a really looooong function. But it needs
        d = self.data  # to be that way for clarity
        events = []
        for play in d:
            event = Event()
            play[0].replace("[", "")
            play[0].replace("'", "")
            event.homeTeam = play[0][0:3]
            event.year = play[0][3:7]
            event.month = play[0][7:9]
            event.day = play[0][9:11]
            event.doubleHeader = play[0][11:]
            event.id = play[0]
            event.visTeam = play[1]
            event.inning = play[2]
            event.battingTeam = play[3]
            event.team = event.homeTeam if (
                event.battingTeam == "1") else event.visTeam
            event.outs = play[4]
            event.balls = play[5]
            event.strikes = play[6]
            event.visScore = play[7]
            event.homeScore = play[8]
            event.batter = play[9]
            event.batterHand = play[10]
            event.pitcher = play[11]
            event.pitcherHand = play[12]
            event.firstBase = play[13]
            event.secondBase = play[14]
            event.thirdBase = play[15]
            event.outcome = play[16]
            event.leadoff = play[17]
            event.pinchHit = play[18]
            event.batterPos = play[19]
            event.lineupSpot = play[20]
            event.eventType = play[21]
            event.batterEvent = True if play[22] == "T" else False
            event.atBat = True if play[23] == "T" else False
            event.hitVal = play[24]
            event.SH = play[25]
            event.SF = play[26]
            event.outsMade = play[27]
            event.RBI = play[28]
            event.WP = True if play[29] == "T" else False
            event.PB = True if play[30] == "T" else False
            event.errorsMade = play[31]
            event.batterDest = play[32]
            event.firstDest = play[33]
            event.secondDest = play[34]
            event.thirdDest = play[35]
            events.append(event)
        return events

class ListParser(Parser):

    def __init__(self, listInfo):
        self.data = listInfo

"""

THIS CODE MOVED TO fileWriter.py
"""
def getStats():
    test = Parser("C:/Retro/pbp.txt")
    plays = test.parse()
    id = raw_input("Enter a player id: ")
    firstName = raw_input("Enter the player's first name: ")
    lastName = raw_input("Enter the player's last name: ")
    position = raw_input("Enter the player's position: ")
    players = {}
    players[id] = RetrosheetPlayer(id, firstName, lastName, position)
    player = players[id]
    for play in plays:
        player.addBatterEvent(play)
    year = raw_input("Enter a year of interest: ")
    stat = raw_input("Enter the stat you want to calculate: ")
    print
    print eval("players['%s'].seasons['%s'].%s" % (player, year, stat))
    print players[str(player)].seasons[str(year)].stats[str(stat)]
    print players[str(player)].seasons[str(year)].__getattr__(stat)
"""
if __name__ == "__main__":
    import subprocess as sp
    import os
    plays = []
    filenames = {}
    for year in xrange(2000, 2012):
        decade = year - year%10
        path = "C:/Retro/%sseve" % str(decade)
 #       for filename in os.listdir(path):
  #          print filename
   #         sp.Popen("cd \Retro & bevent -y %s %s/%s > C:/Retro/plays/%s" % (
    #            year, decade, filename, "%s.txt" % filename[0:7]), shell=True)
    
"""       
