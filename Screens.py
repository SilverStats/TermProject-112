# Screens.py
# Steven Silverman; ssilverm; Section E. Mentor: Jordan Zink
# various user interface screens
# this is where you actually run the program from
# it interfaces with the back end processing to display the data

import Parser # based on mrallen1's parser found online
import FileWriter # with thanks to StackOverflow for ideas
import Autocomplete # created by Mitja Martini. NOT MY CODE

from Tkinter import *
import tkMessageBox
import ttk
import math
import os
import csv
import cPickle as pickle

###################
# home screen
###################

def drawTitles(canvas):
    xOffset = 20
    yOffset = 45
    canvas.create_text(canvas.data.width/2, yOffset,
                       text="Welcome to Silver Stats!", font="Arial 28 bold")
    canvas.create_text(canvas.data.width/2-xOffset, 2*yOffset, fill="white",
                       text="Pick a type of search.", font="Arial 24 bold")
    canvas.create_text(3*canvas.data.width/5, canvas.data.height-2*yOffset,
                       text="The information used here was obtained free of"+
                       "\ncharge from and is copyrighted by Retrosheet.",
                       font="Arial 14")
    canvas.create_text(3*canvas.data.width/5, canvas.data.height-yOffset,text=
                       "Interested parties may contact Retrosheet at "+
                       "20 Sunset Rd., Newark, DE 19711.", font="Arial 14")

def drawPlaysButton(root, canvas):
    (width, height) = (15, 2)
    canvas.data.buttons["playsButton"]=Button(
        root,text="Specific Plays",font="Arial 14 bold",
        width=width,height=height,command=lambda:playsPressed(root, canvas))
    canvas.data.buttons["playsButton"].place(relx=.13, rely=.3, anchor=CENTER)

def drawSummaryButton(root, canvas):
    (width, height) = (15, 2)
    canvas.data.buttons["summaryButton"]=Button(
        root, text="Summary Statistics", font="Arial 14 bold",
        width=width,height=height,command=lambda: summaryPressed(root, canvas))
    canvas.data.buttons["summaryButton"].place(relx=.87, rely=.3,anchor=CENTER)

def drawHomeInfoButton(root, canvas):
    (width, height) = (15, 2)
    canvas.data.buttons["homeInfoButton"]=Button(
        root, text="Instructions", font="Arial 14 bold",
        width=width,height=height,command=lambda:homeInfoPressed())
    canvas.data.buttons["homeInfoButton"].place(relx=.6,rely=.6,anchor=CENTER)

def homeInfoPressed():
    text = ("Specific Plays: when given a set of criteria, outputs a list of" +
            " up to 100 plays matching the description, starting with the" +
            " least recent." + "\n\n" + "Summary Statistics: when given a" +
            " player, type of statistics, and a range of years, outputs the" +
            " year-by-year totals for that player." + "\n" + "A plus sign (+)" +
            " denotes that the player was on multiple teams in the given year."
            "\nNOTE: Pitching totals not available in this version." + "\n\n" +
            "WARNING: Entering a wide range of years without entering a" +
            " player name could result in very long search times." + "\n\n" +
            "The text entry fields will auto-complete: lowercase letters" +
            " will result in Retrosheet IDs being displayed, while " +
            "Mixed Case will yield actual names.")
    tkMessageBox.showinfo("How to use Silver Stats", text)    

def drawHomeScreen(root, canvas):
    drawTitles(canvas)
    drawPlaysButton(root, canvas)
    drawSummaryButton(root, canvas)
    drawHomeInfoButton(root, canvas)

def drawPlaysBase(canvas):
    canvas.delete(ALL)
    canvas.create_rectangle(0, 0, canvas.data.width, canvas.data.height,
                            fill="#000000888") # matching blue color in logo

def drawSummaryBase(canvas):
    canvas.delete(ALL)
    canvas.create_rectangle(0, 0, canvas.data.width, canvas.data.height,
                            fill="#bbb222222")

def homeRedrawAll(root, canvas):
    forgetButtons(canvas)
    photo = PhotoImage(file="MLB_Logo2.gif")
        # image from www.sports-logos-screensavers.com/user/MLB_Logo.jpg
    canvas.data.photo=photo # keep a reference so it actually shows up
    canvas.create_image(canvas.data.width/2,canvas.data.height/2,
                        anchor=CENTER,image=photo)
    drawHomeScreen(root, canvas)
    initStartingValues(canvas) # so going back to home clears the values

def init(root, canvas):
    canvas.pack()
    canvas.data.players = FileWriter.makeRosterList()
    canvas.data.playerList = canvas.data.players.keys()
    canvas.data.error = False
    canvas.data.screen = 0
    canvas.data.years = set() # avoids repetition of years
    for filename in os.listdir("C:/Retro/Plays"):
        canvas.data.years.add(filename[0:4])
    homeRedrawAll(root, canvas)
    getEventCodes(canvas)
    getTeams(canvas)
    

def run():
    # create the root and the canvas
    root = Tk()
    (width, height) = (1200, 700)
    canvas = Canvas(root, width=width, height=height)
    root.resizable(width=FALSE, height=FALSE)
    # Store canvas in root and in canvas itself for callbacks
    root.canvas = canvas.canvas = canvas
    # Set up canvas data and call init
    class Struct: pass
    canvas.data = Struct()
    (canvas.data.width, canvas.data.height) = (width, height)
    canvas.data.buttons = {}
    init(root, canvas)
    # set up events
    #root.bind("<Button-1>", mousePressed)
    root.bind("<Key>", lambda event: keyPressed(root, canvas, event))
    #timerFired(canvas)
    # and launch the app
    root.mainloop()  # This call BLOCKS

###################
# Plays button
###################


def playsPressed(root, canvas):
    playsRedrawAll(root, canvas)
    canvas.data.typeOfQuery = "plays"

def playsRedrawAll(root, canvas):
    canvas.delete(ALL)
    canvas.data.firstPlayCalculation = True
    canvas.data.screen = 0
    forgetButtons(canvas)
    drawPlaysBase(canvas)
    drawPlaysTitle(canvas)
    drawPlaysScreen(root, canvas)

def drawPlaysTitle(canvas):
    (row, col) = (0, 1.5)
    (relx, rely) = getPlaysCoords(row, col)
    (cx, cy) = (canvas.data.width*relx, canvas.data.height*rely)
    canvas.create_text(cx, cy, text="Choose some play criteria!",
                       font = "Arial 24", fill="white")

def drawPlaysScreen(root, canvas): # filters from thebaseballcube.com
    drawStartYear(root, canvas)
    drawEndYear(root, canvas)
    drawInning(root, canvas)
    drawLineupSpot(root, canvas)
    drawBatterDefPos(root, canvas)
    drawBatterTeam(root, canvas)
    drawPitcherTeam(root, canvas)
    drawBatterHand(root, canvas)
    drawPitcherHand(root, canvas)
    drawOutcome(root, canvas)
    drawLocation(root, canvas)
    drawLeadoff(root, canvas)
    drawOuts(root, canvas)
    drawCount(root, canvas)
    drawRunners(root, canvas)
    drawBatter(root, canvas)
    drawPitcher(root, canvas)
    drawSortingMethod(root, canvas)
    drawSelectionBoxes(root, canvas)
    # all these do much the same thing: draw user input boxes
    # they're largely self-documenting, so I don't have comments in all of them
    # and they're all graphics functions, so this can be 25 lines

def drawSelectionBoxes(root, canvas):
    drawHomeBox(root, canvas)
    drawInfoBox(root, canvas)
    drawMakePlayBox(root, canvas)

def drawFilterTitle(canvas, relx, rely, text): # for the label above the entry
    yOffset = .05
    cx = canvas.data.width*relx
    cy = canvas.data.height*(rely-yOffset)
    canvas.create_text(cx, cy, text=text, font="Arial 16", fill="white")

def getPlaysCoords(row, col): # for easy, gridlike placement of entry options
    return (1.0/8+col/4.0, 1.0/12+row/6.0)

def initStartingValues(canvas):
    canvas.data.iStartYear = min(canvas.data.years)
    canvas.data.iEndYear = max(canvas.data.years)
    canvas.data.iInning = "Any"
    canvas.data.iLineupSpot = "Any"
    canvas.data.iPosition = "Any"
    (canvas.data.iBTeam, canvas.data.iPTeam) = ("Any", "Any")
    (canvas.data.iBHand, canvas.data.iPHand) = ("Any", "Any")
    (canvas.data.iOutcome, canvas.data.iLocation) = ("Any", "Any")
    (canvas.data.iLeadoff, canvas.data.iOut) = ("Any", "Any")
    (canvas.data.iCount, canvas.data.iRunner) = ("Any", "Any")
    (canvas.data.iBatter, canvas.data.iPitcher) = ("", "")
    canvas.data.iSorting = "Old to New"
    
def drawStartYear(root, canvas):
    (row, col) = (1, 0)
    (relx, rely) = getPlaysCoords(row, col)
    startYear = IntVar(root)
    startYear.set(canvas.data.iStartYear) 
    yearChoices = sorted(list(canvas.data.years))
    yearChoices.reverse()
    startYears = OptionMenu(root, startYear, *yearChoices)
    startYears.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["startYears"] = startYears
    canvas.data.startYear = startYear
    drawFilterTitle(canvas, relx, rely, "Start Year")

def drawEndYear(root, canvas):
    (row, col) = (1, 1)
    (relx, rely) = getPlaysCoords(row, col)
    endYear = IntVar(root)
    endYear.set(canvas.data.iEndYear)
    yearChoices = sorted(list(canvas.data.years))
    yearChoices.reverse()
    endYears = OptionMenu(root, endYear, *yearChoices)
    endYears.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["endYears"] = endYears
    canvas.data.endYear = endYear
    drawFilterTitle(canvas, relx, rely, "End Year")    

def drawInning(root, canvas):
    (row, col) = (1, 2)
    (relx, rely) = getPlaysCoords(row, col)
    inning = StringVar(root)
    inning.set(canvas.data.iInning)
    inningChoices = ("Any", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                     "Extra", "1-3", "4-6", "7-9")
    innings = OptionMenu(root, inning, *inningChoices)
    innings.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["innings"] = innings
    canvas.data.inning = inning
    drawFilterTitle(canvas, relx, rely, "Inning(s)")

def drawLineupSpot(root, canvas):
    (row, col) = (1, 3)
    (relx, rely) = getPlaysCoords(row, col)
    spot = StringVar(root)
    spot.set(canvas.data.iLineupSpot)
    spotChoices = ("Any", "1", "2", "3", "4", "5", "6", "7", "8", "9")
    lineup = OptionMenu(root, spot, *spotChoices)
    lineup.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["lineupSpot"] = lineup
    canvas.data.lineupSpot = spot
    drawFilterTitle(canvas, relx, rely, "Lineup Spot")

def drawBatterDefPos(root, canvas):
    (row, col) = (2, 0)
    (relx, rely) = getPlaysCoords(row, col)
    pos = StringVar(root)
    pos.set(canvas.data.iPosition)
    posChoices = ("Any", "P", "C", "1B", "2B", "3B", "SS", "LF",
                  "CF", "RF", "DH", "PH")
    positions = OptionMenu(root, pos, *posChoices)
    positions.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["positions"] = positions
    canvas.data.position = pos
    drawFilterTitle(canvas, relx, rely, "Defensive Position")

def drawBatterTeam(root, canvas):
    data = canvas.data
    (row, col) = (2, 1)
    (relx, rely) = getPlaysCoords(row, col)
    bTeam = StringVar(root)
    bTeam.set(canvas.data.iBTeam)
    bTeamChoices = canvas.data.teamList
    bTeams = OptionMenu(root, bTeam, *bTeamChoices)
    bTeams.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["bTeams"] = bTeams
    canvas.data.bTeam = bTeam
    drawFilterTitle(canvas, relx, rely, "Batter Team")

def getTeams(canvas):
    teamSet = set() # avoid repeats
    teamIndex = 4 # skips the year characters
    for filename in os.listdir("C:/Retro/Plays"):
        teamSet.add(filename[teamIndex:teamIndex+3]) # gets the team code
    teamList = ["Any"] + sorted(list(teamSet))
    canvas.data.teamList = teamList

def drawPitcherTeam(root, canvas):
    (row, col) = (2, 2)
    (relx, rely) = getPlaysCoords(row, col)
    pTeam = StringVar(root)
    pTeam.set(canvas.data.iPTeam)
    pTeamChoices = canvas.data.teamList
    pTeams = OptionMenu(root, pTeam, *pTeamChoices)
    pTeams.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["pTeams"] = pTeams
    canvas.data.pTeam = pTeam
    drawFilterTitle(canvas, relx, rely, "Pitching Team")

def drawBatterHand(root, canvas):
    (row, col) = (2, 3)
    (relx, rely) = getPlaysCoords(row, col)
    bHand = StringVar(root)
    bHand.set(canvas.data.iBHand)
    bHandChoices = ("Any", "Left", "Right")
    bHands = OptionMenu(root, bHand, *bHandChoices)
    bHands.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["bHand"] = bHands
    canvas.data.bHand = bHand
    drawFilterTitle(canvas, relx, rely, "Batter Hand")

def drawPitcherHand(root, canvas):
    (row, col) = (3, 0)
    (relx, rely) = getPlaysCoords(row, col)
    pHand = StringVar(root)
    pHand.set(canvas.data.iPHand)
    pHandChoices = ("Any", "Left", "Right")
    pHands = OptionMenu(root, pHand, *pHandChoices)
    pHands.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["pHand"] = pHands
    canvas.data.pHand = pHand
    drawFilterTitle(canvas, relx, rely, "Pitcher Hand")

def drawOutcome(root, canvas):
    (row, col) = (3, 1)
    (relx, rely) = getPlaysCoords(row, col)
    outcome = StringVar(root)
    outcome.set(canvas.data.iOutcome)
    outcomeChoices = ("Any", "Single", "Double", "Triple", "Home Run", "Walk",
                      "Strikeout", "Hit by Pitch", "Generic Out", "Stolen Base",
                      "Caught Stealing", "Error", "Unknown Event", "No Event",
                      "Balk", "Fielder's Choice", "Intentional Walk",
                      "Interference", "Wild Pitch", "Passed Ball", "Pickoff",
                      "Error on Pickoff", "Error on foul", "Missing Play",
                      "Fielder's Indifference", "Other advance")
    # these are all the plays you can look for easily in Retrosheet
    canvas.data.outcomeChoices = outcomeChoices
    outcomes = OptionMenu(root, outcome, *outcomeChoices)
    outcomes.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["outcomes"] = outcomes
    canvas.data.outcome = outcome
    drawFilterTitle(canvas, relx, rely, "Outcome of Play")

def drawLocation(root, canvas):
    (row, col) = (3, 2)
    (relx, rely) = getPlaysCoords(row, col)
    location = StringVar(root)
    location.set(canvas.data.iLocation)
    locationChoices = ("Any", "Home", "Away")
    locations = OptionMenu(root, location, *locationChoices)
    locations.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["locations"] = locations
    canvas.data.location = location
    drawFilterTitle(canvas, relx, rely, "Home/Away")

def drawLeadoff(root, canvas):
    (row, col) = (3, 3)
    (relx, rely) = getPlaysCoords(row, col)
    leadoff = StringVar(root)
    leadoff.set(canvas.data.iLeadoff)
    leadoffChoices = ("Any", "Yes", "No")
    leadoffs = OptionMenu(root, leadoff, *leadoffChoices)
    leadoffs.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["leadoff"] = leadoffs
    canvas.data.leadoff = leadoff
    drawFilterTitle(canvas, relx, rely, "Leadoff?")

def drawOuts(root, canvas):
    (row, col) = (4, 0)
    (relx, rely) = getPlaysCoords(row, col)
    out = StringVar(root)
    out.set(canvas.data.iOut)
    outChoices = ("Any", "1", "2", "3")
    outs = OptionMenu(root, out, *outChoices)
    outs.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["outs"] = outs
    canvas.data.out = out
    drawFilterTitle(canvas, relx, rely, "Number of Outs")

def drawCount(root, canvas):
    (row, col) = (4, 1)
    (relx, rely) = getPlaysCoords(row, col)
    count = StringVar(root)
    count.set(canvas.data.iCount) # below are all possible counts on a batter
    countChoices = ("Any", "0-0", "0-1", "0-2", "1-0", "1-1", "1-2", "2-0",
                    "2-1", "2-2", "3-0", "3-1", "3-2")
    counts = OptionMenu(root, count, *countChoices)
    counts.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["count"] = counts
    canvas.data.count = count
    drawFilterTitle(canvas, relx, rely, "Count")

def drawRunners(root, canvas):
    (row, col) = (4, 2)
    (relx, rely) = getPlaysCoords(row, col)
    runner = StringVar(root)
    runner.set(canvas.data.iRunner) # below are base combinations ("-" empty)
    runnerChoices = ("Any", "---", "1--", "-2-", "--3", "12-", "1-3", "123")
    runners = OptionMenu(root, runner, *runnerChoices)
    runners.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["runners"] = runners
    canvas.data.runner = runner
    drawFilterTitle(canvas, relx, rely, "Runners On")

def drawBatter(root, canvas):
    (row, col) = (5, 0.25)
    (relx, rely) = getPlaysCoords(row, col)
    batter=Autocomplete.AutocompleteEntry(root) # autocomplete by Mitja Martini
    batter.set_completion_list(canvas.data.playerList)
    batter.insert(0, canvas.data.iBatter)
    batter.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["batter"] = batter
    drawFilterTitle(canvas, relx, rely, "Batter (Name or ID)")

def drawPitcher(root, canvas):
    (row, col) = (5, 2.75)
    (relx, rely) = getPlaysCoords(row, col)
    pitcher = Autocomplete.AutocompleteEntry(root) # autocomplete as above
    pitcher.set_completion_list(canvas.data.playerList)
    pitcher.insert(0, canvas.data.iPitcher)
    pitcher.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["pitcher"] = pitcher
    drawFilterTitle(canvas, relx, rely, "Pitcher (Name or ID)")

def drawSortingMethod(root, canvas):
    (row, col) = (4, 3)
    (relx, rely) = getPlaysCoords(row, col)
    sorting = StringVar(root)
    sorting.set(canvas.data.iSorting)
    sortingChoices = ("Old to New", "New to Old")
    sortings = OptionMenu(root, sorting, *sortingChoices)
    sortings.place(relx=relx, rely=rely, anchor=CENTER)
    canvas.data.buttons["sortings"] = sortings
    canvas.data.sorting = sorting
    drawFilterTitle(canvas, relx, rely, "Sorting Type")

def drawHomeBox(root, canvas):
    (row, col) = (0, 0)
    (relx, rely) = getPlaysCoords(row, col)
    (width, height) = (18, 3)
    canvas.data.buttons["homeButton"]=Button(
        root, text="Back to Home (Plate)", width=width,height=height,
        command=lambda: homeRedrawAll(root, canvas))
    canvas.data.buttons["homeButton"].place(relx=relx, rely=rely, anchor=CENTER)

def drawInfoBox(root, canvas):
    (row, col) = (5, 1.5)
    (relx, rely) = getPlaysCoords(row, col)
    (width, height) = (18, 3)
    canvas.data.buttons["infoButton"]=Button(
        root, text="Help with ID Codes", width=width, height=height,
        command=lambda: drawIdCodeInfoBox(root, canvas))
    canvas.data.buttons["infoButton"].place(relx=relx, rely=rely, anchor=CENTER)

def drawMakePlayBox(root, canvas):
    (row, col) = (0, 3)
    (relx, rely) = getPlaysCoords(row, col)
    (width, height) = (18, 3)
    canvas.data.buttons["makePlayButton"]=Button(
        root, text="Get Plays!", width=width, height=height,
        command=lambda: getInfo(root, canvas))
    canvas.data.buttons["makePlayButton"].place(
        relx=relx, rely=rely, anchor=CENTER)
    
def drawIdCodeInfoBox(root, canvas):
    text = """These are unique 8-character codes for each player.
They "are of the form 'llllfnnn' where 'llll' are the first four letters
of the last name, 'f' is the first letter of the first name, and 'nnn' are
numbers. The first number is 0 for players who appeared in 1984 or later and
1 for players whose career ended before 1984. The next two numbers are sequence
numbers starting with 01." (Source: http://www.retrosheet.org)"""
    text = text.replace("\n", " ")
    tkMessageBox.showinfo("Help with Retrosheet ID Codes", text)

def keyPressed(root, canvas, event):
    if event.keysym == "Return":
        if canvas.data.typeOfQuery == "plays":
            getInfo(root, canvas)
        else:
            getSummaryStats(root, canvas)

###################
# displaying the plays
###################

def getInfo(root, canvas):
    data = canvas.data
    (data.iStartYear, data.iEndYear) = (data.startYear.get(),data.endYear.get())
    (data.iInning, data.iLineupSpot) = (data.inning.get(),data.lineupSpot.get())
    data.iPosition = data.position.get()
    (data.iBTeam, data.iPTeam) = (data.bTeam.get(), data.pTeam.get())
    (data.iBHand, data.iPHand) = (data.bHand.get(), data.pHand.get())
    (data.iOutcome, data.iLocation) = (data.outcome.get(), data.location.get())
    (data.iLeadoff, data.iRunner) = (data.leadoff.get(), data.runner.get())
    (data.iOut, data.iCount) = (data.out.get(), data.count.get())
    data.iSorting = data.sorting.get()
    data.iBatter = data.buttons["batter"].get()
    data.iPitcher = data.buttons["pitcher"].get()
    canvas.data.error = False
    calcFilters(root, canvas) # i is for info (what's in the button),
                              # f is for filter (what the program needs to run)
    if canvas.data.error == False:
        drawLoadingScreen(canvas)
        canvas.after(5, displayPlaysRedrawAll, root, canvas)
        # the delay lets Tkinter render the loading screen

def displayPlaysRedrawAll(root, canvas):
    if canvas.data.firstPlayCalculation: getPlays(canvas) # avoid redundancy
    if len(canvas.data.events) == 0: displayNullError(root, canvas)
    else:
        canvas.delete(ALL)
        forgetButtons(canvas)
        drawPlaysBase(canvas)
        drawGrid(canvas)
        drawHeadings(canvas)
        canvas.data.firstPlayCalculation = False # not the first time anymore,
        drawInfo(canvas)                         # since we already drew it once
        drawNavButtons(root, canvas)
        drawScreenText(canvas)

def displayNullError(root, canvas):
    text = ("There are no plays matching those criteria." + "\n" +
            "Please refine your search.")
    tkMessageBox.showerror("Whoops, that's an error!", text)
    canvas.delete(canvas.data.rectangle)
    canvas.delete(canvas.data.loading)

def drawNavButtons(root, canvas): # to switch between sets of 20 plays
    (width, height) = (15, 2)
    if (canvas.data.screen < 4 and
        len(canvas.data.events) > canvas.data.rows*(canvas.data.screen+1)):
        nextButton = Button(root,text="Next 20 Plays",width=width,height=height,
                            command=lambda: nextScreen(root, canvas))
        nextButton.place(relx=.8, rely=.9, anchor=CENTER)
        canvas.data.buttons["nextButton"] = nextButton
    if canvas.data.screen > 0:
        prevButton = Button(root,text="Previous 20 Plays",width=width,
                            height=height,
                            command=lambda: prevScreen(root, canvas))
        prevButton.place(relx=.2, rely=.9, anchor=CENTER)
        canvas.data.buttons["prevButton"] = prevButton
    drawPlayBackButtons(root, canvas)

def nextScreen(root, canvas):
    canvas.data.screen += 1
    displayPlaysRedrawAll(root, canvas)

def prevScreen(root, canvas):
    canvas.data.screen -= 1
    displayPlaysRedrawAll(root, canvas)
        
def drawPlayBackButtons(root, canvas): # back to other screens
    (width, height) = (18, 2)
    backButton=Button(root, text="Back to Play Filters", width=width,
                      height=height,command=lambda:playsRedrawAll(root,canvas))
    backButton.place(relx = .25, rely = .0625, anchor=CENTER)
    canvas.data.buttons["backButton"] = backButton
    pHomeButton=Button(root, text="Back to Home (Plate)", width = width,
                       height=height,command=lambda:homeRedrawAll(root,canvas))
    pHomeButton.place(relx = .1, rely = .0625, anchor=CENTER)
    canvas.data.buttons["pHomeButton"] = pHomeButton
    

def drawGrid(canvas): # draws the spreadsheet for the text to go in
    (xOffset, yOffset) = (50, 130)
    verticalGap = 21 # height of one row
    rows = 20
    (canvas.data.xOffset, canvas.data.yOffset) = (xOffset, yOffset)
    (canvas.data.verticalGap, canvas.data.rows) = (verticalGap, rows)
    for row in xrange(rows+1): # draws horizontals
        canvas.create_line(xOffset,yOffset+verticalGap*row,
                           canvas.data.width-xOffset,yOffset+verticalGap*row,
                           fill="white")
    fieldWidths = (10, 16, 3, 5, 16, 3, 5, 3, 4, 3, 3, 5, 4, 14, 22)
    canvas.data.fieldWidths = fieldWidths
    extra = (canvas.data.width-xOffset*2)/float(sum(fieldWidths))
    canvas.data.extra = extra
    canvas.create_line(xOffset,yOffset,xOffset,
                       yOffset+verticalGap*(rows),fill="white")
    for position in xrange(len(fieldWidths)):
        canvas.create_line(xOffset+sum(fieldWidths[0:position+1])*extra,yOffset,
                           xOffset+sum(fieldWidths[0:position+1])*extra,
                           yOffset+verticalGap*(rows),fill="white") # verticals
                           
def drawHeadings(canvas): # info labels
    data = canvas.data
    fields = ["Date","Batter", "Hand","Team","Pitcher", "Hand","Team","Def.",
              "Spot", "Inn.", "Outs", "Count", "Ldoff","Event Type",
              "Scorebook-Style Details"]
    for position in xrange(len(data.fieldWidths)):
        canvas.create_text(data.xOffset+(sum(data.fieldWidths[
            0:position])+data.fieldWidths[position]/2.0)*data.extra,
                           data.yOffset, text=fields[position], anchor="s",
                           font = "Times 12", fill="white")
    
def drawInfo(canvas):
    (xOffset, yOffset) = (canvas.data.xOffset, canvas.data.yOffset)
    extra = canvas.data.extra
    fieldWidths = canvas.data.fieldWidths
    verticalGap = canvas.data.verticalGap
    xOffset -= 2 # buffer from right edge of cell
    yOffset += verticalGap/2 # move into center of cell (vertically)
    for index in xrange(
        min(canvas.data.rows, # don't draw extra rows for plays != 0 % 20
            len(canvas.data.events)-canvas.data.rows*canvas.data.screen)):
        playIndex = index + canvas.data.rows*canvas.data.screen
        event = canvas.data.events[playIndex]
        info = getPlayInfo(canvas, event)
        for position in xrange(len(info)):
            canvas.create_text(xOffset+sum(fieldWidths[0:position+1])*extra,
                               yOffset+verticalGap*index, text=info[position],
                               font = "Times 12", anchor="e", fill="white")
            
def drawScreenText(canvas): # tells you which plays you're looking at
    canvas.create_text(canvas.data.width/2,
                       canvas.data.height-canvas.data.yOffset/2, text =
                       "Plays %d-%d of %d" %
                       (1+canvas.data.rows*canvas.data.screen,
                        min(len(canvas.data.events),
                            canvas.data.rows*(canvas.data.screen+1)),
                        len(canvas.data.events)),
                        font = "Arial 24", fill="white")

def getPlayInfo(canvas, event): # turns into useful text
    date = event.month + "/" + event.day + "/" + event.year
    batter = canvas.data.players[
        event.batter][2] + " " + canvas.data.players[event.batter][1]
    pitcher = canvas.data.players[
        event.pitcher][2] + " " + canvas.data.players[event.pitcher][1]
    (batterHand, pitcherHand) = getHandedness(canvas, event)
    (batterTeam, pitcherTeam, defPos, spot, inning, outs, count, leadoff,
     outcome, details) = getSecondaryPlayInfo(canvas, event)
    return (date,batter,batterHand,batterTeam,pitcher,pitcherHand,pitcherTeam,
            defPos, spot, inning, outs, count, leadoff, outcome, details)

def getHandedness(canvas, event):
    batter = canvas.data.players[
        event.batter][2] + " " + canvas.data.players[event.batter][1]
    pitcher = canvas.data.players[
        event.pitcher][2] + " " + canvas.data.players[event.pitcher][1]
    pitcherHand = canvas.data.players[event.pitcher][4]
    batterHandPref = canvas.data.players[event.batter][3] # doesn't change
    if event.batterHand == "?" and batterHandPref == "B": # sets switch-hitters
        batterHand = "L" if pitcherHand == "R" else "R"
    else:
        batterHand = canvas.data.players[event.batter][3]
    return (batterHand, pitcherHand)

def getSecondaryPlayInfo(canvas, event):
    eventCodes = canvas.data.eventCodes # number --> play type
    maxLength = 26 # size of details box (some strings are too long to fit)
    batterTeam = event.visTeam if (event.battingTeam=="0") else event.homeTeam
    pitcherTeam = event.visTeam if (event.battingTeam=="1") else event.homeTeam
    (defPos, spot) = (event.batterPos, event.lineupSpot)
    (inning, leadoff) = (event.inning, "" if event.leadoff == "F" else "Y")
    (count,outs) = (str(event.balls)+"-"+str(event.strikes), event.outs)
    (outcome,details) = (eventCodes[int(event.eventType)], event.outcome)
    if len(details) > maxLength: details = details[:maxLength-2] + "..."
    return (batterTeam, pitcherTeam, defPos, spot, inning,
            outs, count, leadoff, outcome, details)
     
    
def getEventCodes(canvas): # this is Retrosheet's numbering system
    eventCodes = {0:"Unknown Event",1:"No Event",2:"Generic Out",3:"Strikeout",
                  4:"Stolen Base",5:"Fielder's Indifference",
                  6:"Caught Stealing",7:"Error on Pickoff",8:"Pickoff",
                  9:"Wild Pitch",10:"Passed Ball",11:"Balk",12:"Other advance",
                  13:"Error on foul",14:"Walk",15:"Intentional Walk",
                  16:"Hit by Pitch",17:"Interference",18:"Error",
                  19:"Fielder's Choice",20:"Single",21:"Double",22:"Triple",
                  23:"Home Run",24:"Missing Play"}
    canvas.data.eventCodes = eventCodes
                                    

def getPlays(canvas): # picks the type of search based on user input
    number = 0
    events = []
    if canvas.data.fBatter != "":
        events = alphaBatter(canvas)
    elif canvas.data.fPitcher != "":
        events = alphaPitcher(canvas)
    else: events = yearsRange(canvas)
    canvas.data.events = events

def drawLoadingScreen(canvas):
    canvas.data.rectangle = canvas.create_rectangle(
        0,0,canvas.data.width,canvas.data.height,fill="green",stipple="gray25")
    canvas.data.loading = canvas.create_text(
        canvas.data.width/2, canvas.data.height/2,
        text="Loading...",font="Arial 24 bold", anchor="s")

def yearsRange(canvas): # for when no name is given, look by years
    (good, number) = ([], 0)
    if canvas.data.iSorting == "New to Old": canvas.data.fYears.reverse()
    for year in canvas.data.fYears:
        files = FileWriter.getFiles(year)
        for filename in files:
            if str(year) in filename:
                events = Parser.Parser("C:/Retro/Plays/%s" % filename)
                plays = events.parse()
                if canvas.data.iSorting == "New to Old": plays.reverse()
                for play in plays:
                    if criteriaMatch(canvas, play):
                        good += [play] # keep the ones that match up
                        number += 1
                    if number >= 100: break # stops after 100 plays
                if number >= 100: break
        if number >= 100: break
    return good

def criteriaMatch(canvas, play): # is this the play we're looking for?
    data = canvas.data
    (first, second, third) = getRunners(play)
    bTeam = play.homeTeam if play.battingTeam == "1" else play.visTeam
    pTeam = play.homeTeam if play.battingTeam == "0" else play.visTeam
    (batterHand, pitcherHand) = getHandedness(canvas, play)
    return ((int(play.year) in data.fYears) and
            ((int(play.inning) in data.fInning)
             or ((int(play.inning) > 9) and (0 in data.fInning)))                                               
            and (int(play.lineupSpot) in data.fLineupSpot) and
            (int(play.batterPos) in data.fPosition) and (bTeam in data.fBTeam)
            and (pTeam in data.fPTeam) and (batterHand in data.fBHand) and
            (pitcherHand in data.fPHand) and
            (int(play.eventType) in data.fOutcome) and
            (int(play.battingTeam) in data.fLocation) and
            (play.leadoff in data.fLeadoff) and (int(play.outs) in data.fOut)and
            ((int(play.balls), int(play.strikes)) in data.fCount) and
            ((first, second, third) in data.fRunner) and
            (data.fBatter in play.batter) and (data.fPitcher in play.pitcher))
            
def getRunners(play): # to use in criteriaMatch()
    first = 0 if play.firstBase == "" else 1
    second = 0 if play.secondBase == "" else 1
    third = 0 if play.thirdBase == "" else 1
    return (first, second, third)
    
def alphaBatter(canvas): # alphabetically by batter (in pickled dictionaries)
    (number, good) = (0, [])
    with open("C:/Retro/AlphaBatter/%s%s"%(
        canvas.data.fBatter[0],canvas.data.fBatter[1])) as filename:
        playsDict = pickle.load(filename)
    listEvents = playsDict[ # controls for people with no PAs
        canvas.data.fBatter] if canvas.data.fBatter in playsDict else []
    events = Parser.ListParser(listEvents)
    plays = events.parse()
    if canvas.data.iSorting == "New to Old": plays.reverse()
    for play in plays:
        if criteriaMatch(canvas, play):
            good += [play] # keep the ones that match
            number += 1
        if number == 100: break
    return good

def alphaPitcher(canvas): # alphabetically by pitcher (in pickled dictionaries)
    (number, good) = (0, [])
    with open("C:/Retro/AlphaPitcher/%s%s"%(
        canvas.data.fPitcher[0],canvas.data.fPitcher[1])) as filename:
        playsDict = pickle.load(filename)
    listEvents = playsDict[ # controls for non-pitchers
        canvas.data.fPitcher] if canvas.data.fPitcher in playsDict else []
    events = Parser.ListParser(listEvents)
    plays = events.parse()
    if canvas.data.iSorting == "New to Old": plays.reverse()
    for play in plays:
        if criteriaMatch(canvas, play):
            good += [play] # keep the ones that match
            number += 1
        if number == 100: break
    return good

##################
# getting all the info
##################

def calcFilters(root, canvas): # these all do exactly the same thing:
    calcStartYear(canvas)      # turn user input into retrosheet-compatible info
    calcEndYear(canvas)        # I use lists of possible values and "in"
    calcInning(canvas)         # statements to check for matches
    calcLineupSpot(canvas)
    calcPosition(canvas)
    calcBTeam(canvas)
    calcPTeam(canvas)
    calcBHand(canvas)
    calcPHand(canvas)
    calcOutcome(canvas)
    calcLocation(canvas)
    calcLeadoff(canvas)
    calcOut(canvas)
    calcCount(canvas)
    calcRunner(canvas)
    calcBatter(canvas) 
    calcPitcher(canvas)
    checkImpossible(root, canvas)

def calcStartYear(canvas):
    canvas.data.fStartYear = int(canvas.data.iStartYear)

def calcEndYear(canvas):
    canvas.data.fEndYear = int(canvas.data.iEndYear)
    canvas.data.fYears = range(canvas.data.fStartYear, canvas.data.fEndYear+1)

def calcInning(canvas):
    if canvas.data.iInning == "Any": canvas.data.fInning = range(10)
    elif canvas.data.iInning == "Extra": canvas.data.fInning = [0]
    elif canvas.data.iInning == "1-3": canvas.data.fInning = [1,2,3]
    elif canvas.data.iInning == "4-6": canvas.data.fInning = [4,5,6]
    elif canvas.data.iInning == "7-9": canvas.data.fInning = [7,8,9]
    else: canvas.data.fInning = [int(canvas.data.iInning)]

def calcLineupSpot(canvas):
    if canvas.data.iLineupSpot == "Any": canvas.data.fLineupSpot = range(1, 11)
    else: canvas.data.fLineupSpot = [int(canvas.data.iLineupSpot)]

def calcPosition(canvas):
    positions = {"P":1,"C":2,"1B":3,"2B":4,"3B":5,"SS":6,
                     "LF":7,"CF":8,"RF":9,"DH":10,"PH":11}
    if canvas.data.iPosition=="Any":canvas.data.fPosition=range(len(positions)+1)
    else: canvas.data.fPosition = [positions[canvas.data.iPosition]]

def calcBTeam(canvas):
    if canvas.data.iBTeam == "Any":canvas.data.fBTeam=list(canvas.data.teamList)
    else: canvas.data.fBTeam = [canvas.data.iBTeam]

def calcPTeam(canvas):
    if canvas.data.iPTeam == "Any":canvas.data.fPTeam=list(canvas.data.teamList)
    else: canvas.data.fPTeam = [canvas.data.iPTeam]

def calcBHand(canvas):
    if canvas.data.iBHand == "Any": canvas.data.fBHand = ["?", "L", "R"]
    elif canvas.data.iBHand == "Left": canvas.data.fBHand = ["L"]
    else: canvas.data.fBHand = ["R"]

def calcPHand(canvas):
    if canvas.data.iPHand == "Any": canvas.data.fPHand = ["?", "L", "R"]
    elif canvas.data.iPHand == "Left": canvas.data.fPHand = "L"
    else: canvas.data.fPHand = "R"
    
def calcOutcome(canvas):
    if canvas.data.iOutcome == "Any": canvas.data.fOutcome = range(25)
    else:
        for (key, outcome) in canvas.data.eventCodes.items():
            if outcome == canvas.data.iOutcome:
                canvas.data.fOutcome = [key]

def calcLocation(canvas):
    if canvas.data.iLocation == "Any": canvas.data.fLocation = [0, 1]
    elif canvas.data.iLocation == "Home": canvas.data.fLocation = [1]
    else: canvas.data.fLocation = [0]

def calcLeadoff(canvas):
    if canvas.data.iLeadoff == "Any": canvas.data.fLeadoff = ["?", "T", "F"]
    elif canvas.data.iLeadoff == "Yes": canvas.data.fLeadoff = "T"
    else: canvas.data.fLeadoff = "F"

def calcOut(canvas):
    if canvas.data.iOut == "Any": canvas.data.fOut = [0,1,2]
    else: canvas.data.fOut = [int(canvas.data.iOut)]

def calcCount(canvas):
    if canvas.data.iCount == "Any":
        canvas.data.fCount = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),
                              (2,0),(2,1),(2,2),(3,0),(3,1),(3,2)] # all counts
    else: canvas.data.fCount = [(int(canvas.data.iCount[0]),
                               int(canvas.data.iCount[2]))]

def calcRunner(canvas):
    if canvas.data.iRunner == "Any":
        canvas.data.fRunner = [(0,0,0),(1,0,0),(0,1,0),(0,0,1),
                               (1,1,0),(1,0,1),(0,1,1),(1,1,1)]
    else:
        first = 0 if canvas.data.iRunner[0] == "-" else 1
        second = 0 if canvas.data.iRunner[1] == "-" else 1
        third = 0 if canvas.data.iRunner[2] == "-" else 1
        canvas.data.fRunner = [(first, second, third)]

def calcBatter(canvas):
    if canvas.data.iBatter == "":
        canvas.data.fBatter = ""
    elif canvas.data.iBatter in canvas.data.players:
        canvas.data.fBatter = canvas.data.players[canvas.data.iBatter][0]
    else:
        canvas.data.error = True
        displayBatterError()     

def calcPitcher(canvas):
    if canvas.data.iPitcher == "":
        canvas.data.fPitcher = ""
    elif canvas.data.iPitcher in canvas.data.players:
        canvas.data.fPitcher = canvas.data.players[canvas.data.iPitcher][0]
    else:
        canvas.data.error = True
        displayPitcherError()

def getNameFromID(canvas):
    for row in xrange(len(canvas.data.players)):
        if canvas.data.iBatter in canvas.data.players[row]:
            canvas.data.fBatterName = 0
            
def displayBatterError():
    text = """Sorry, that's not a valid batter name or ID.
Click the "Help with ID Codes" button for more."""
    tkMessageBox.showerror("Swing and a miss!", text)

def displayPitcherError():
    text = """Sorry, that's not a valid pitcher name or ID.
Click the "Help with ID Codes" button for more."""
    tkMessageBox.showerror("Swing and a miss!", text)

def checkImpossible(root, canvas): # scenarios that can never happen
    # I didn't control for all of them, but this is a reasonable sampling
    baserunningEvents = [4, 5, 6, 7, 8, 9, 10, 12, 19] # only with runners on
    if canvas.data.fStartYear > canvas.data.fEndYear:
        canvas.data.error = True
        displayImpossibleError()
    if canvas.data.fPTeam == canvas.data.fBTeam and len(
        canvas.data.fBTeam) == 1:
        canvas.data.error = True
        displayImpossibleError()
    elif canvas.data.fLeadoff == "T" and 0 not in canvas.data.fOut:
        canvas.data.error = True
        displayImpossibleError()
    elif canvas.data.fLeadoff == "T" and (0,0,0) not in canvas.data.fRunner:
        canvas.data.error = True
        displayImpossibleError()
    elif canvas.data.fOutcome[0] in baserunningEvents and (
        canvas.data.fRunner == [(0,0,0)]):
        canvas.data.error = True
        displayImpossibleError()

def displayImpossibleError():
    text = """That combination of circumstances can never happen.
Please refine your search."""
    tkMessageBox.showerror("What are you, an umpire?", text)
    
    

###################
# Summary Button
###################

def forgetButtons(canvas):
    for button in canvas.data.buttons:
        canvas.data.buttons[button].place_forget()

def summaryPressed(root, canvas):
    summaryRedrawAll(root, canvas)
    canvas.data.typeOfQuery = "summary"

def summaryRedrawAll(root, canvas):
    canvas.delete(ALL)
    forgetButtons(canvas)
    drawSummaryBase(canvas)
    drawSummaryTitle(canvas)
    drawSummaryScreen(root, canvas)

def drawSummaryTitle(canvas):
    yOffset = 50
    canvas.create_text(canvas.data.width/2, yOffset,
                       text=
                       "Enter a player, type of stats, and years of interest:",
                       font = "Arial 24")

def drawSummaryScreen(root, canvas):
    drawPlayerEntryBox(root, canvas)
    drawStatType(root, canvas)
    drawStartYearEntryBox(root, canvas)
    drawEndYearEntryBox(root, canvas)
    drawGetStatsBox(root, canvas)
    drawSummaryHomeButton(root, canvas)
    drawSummaryInfoButton(root, canvas)
    drawSummaryBoxTitles(canvas)

def drawPlayerEntryBox(root, canvas):
    (relx, rely) = (.1, .225)
    player = Autocomplete.AutocompleteEntry(root) # see citation above
    player.set_completion_list(canvas.data.playerList)
    player.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["player"] = player
    canvas.data.player = player

def drawStatType(root, canvas):
    (relx, rely) = (.3, .225)
    statType = StringVar(root)
    statType.set("Batting")
    statChoices = ("Batting", "Pitching (Not available in this version)")
    statTypes = OptionMenu(root, statType, *statChoices)
    statTypes.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["statTypes"] = statTypes
    canvas.data.statType = statType

def drawStartYearEntryBox(root, canvas):
    (relx, rely) = (.5, .225)
    startYear = IntVar(root)
    earliest = min(canvas.data.years)
    startYear.set(earliest) 
    yearChoices = sorted(list(canvas.data.years))
    yearChoices.reverse()
    startYears = OptionMenu(root, startYear, *yearChoices)
    startYears.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["summaryStartYears"] = startYears
    canvas.data.summaryStartYear = startYear

def drawEndYearEntryBox(root, canvas):
    (relx, rely) = (.7, .225)
    endYear = IntVar(root)
    latest = max(canvas.data.years)
    endYear.set(latest) 
    yearChoices = sorted(list(canvas.data.years))
    yearChoices.reverse()
    endYears = OptionMenu(root, endYear, *yearChoices)
    endYears.place(relx = relx, rely = rely, anchor=CENTER)
    canvas.data.buttons["summaryEndYears"] = endYears
    canvas.data.summaryEndYear = endYear

def drawGetStatsBox(root, canvas):
    (relx, rely) = (.9, .225)
    (width, height) = (18, 2)
    canvas.data.buttons["getStatsButton"]=Button(
        root, text="Get Stats!", width=width, height=height,
        command=lambda: getSummaryStats(root, canvas))
    canvas.data.buttons["getStatsButton"].place(
        relx=relx, rely=rely, anchor=CENTER)

def drawSummaryHomeButton(root, canvas):
    (relx, rely) = (.1, .0825)
    (width, height) = (18, 2)
    canvas.data.buttons["summaryHomeButton"]=Button(
        root, text="Back to Home (Plate)", width=width, height=height,
        command=lambda: homeRedrawAll(root, canvas))
    canvas.data.buttons["summaryHomeButton"].place(
        relx=relx, rely=rely, anchor=CENTER)

def drawSummaryInfoButton(root, canvas):
    (relx, rely) = (.9, .0825)
    (width, height) = (18, 2)
    canvas.data.buttons["infoButton"]=Button(
        root, text="Help with ID Codes", width=width, height=height,
        command=lambda: drawIdCodeInfoBox(root, canvas))
    canvas.data.buttons["infoButton"].place(relx=relx, rely=rely, anchor=CENTER)

def drawSummaryBoxTitles(canvas):
    relx = (.1,.3,.5,.7)
    rely = .2
    text = ("Player (Name or ID)", "Type of Statsitics", "Start Year",
            "End Year")
    info = [(.1, .225, "Player (Name or ID)"), (.3, .225, "Type of Statistics"),
            (.5, .225, "Start Year"), (.7, .225, "End Year")]
    yOffset = .05
    for (relx, rely, text) in info:
        canvas.create_text(canvas.data.width*relx,canvas.data.height*(
            rely-yOffset), text=text, font="Arial 14")

def drawSummaryBoxTitle(canvas, relx, rely, text):
    yOffset = .05
    canvas.create_text(canvas.data.width*relx,canvas.data.height*(rely-yOffset),
                       text=text, font="Arial 14")

#################
# getting the summary stats
#################

def getSummaryStats(root, canvas):
    postSummaryStats(root, canvas)

def postSummaryStats(root, canvas):
    canvas.data.error = False
    calcSummaryStats(root, canvas)
    if canvas.data.fSummaryPlayer != "":
        if canvas.data.error == False:
            canvas.after(5, summaryPostRedrawAll, root, canvas)

def summaryPostRedrawAll(root, canvas):
    if canvas.data.error == False:
        canvas.delete(ALL)
        drawSummaryBase(canvas)
        drawSummaryTitle(canvas)
        drawSummaryBoxTitles(canvas)
        if canvas.data.iStatType == "Batting": drawSummaryBatting(root, canvas)
        # nothing else to do since pitching isn't in yet
        

def calcSummaryStats(root, canvas):
    canvas.data.fSummaryPlayer = ""
    canvas.data.iSummaryPlayer = canvas.data.player.get()
    canvas.data.iSummaryStartYear = canvas.data.summaryStartYear.get()
    canvas.data.iSummaryEndYear = canvas.data.summaryEndYear.get()
    canvas.data.iStatType = canvas.data.statType.get()
    getPlayer(root, canvas)
    if canvas.data.fSummaryPlayer != "":
        if canvas.data.iStatType == "Batting":
            drawLoadingScreen(canvas)
            canvas.after(5, calcBattingStats, canvas)
        else: displayPitchingStatsError(canvas)

def getPlayer(root, canvas):
    if canvas.data.iSummaryPlayer == "":
        canvas.data.fSummaryPlayer = ""
        canvas.data.error = True
        displayNoEntryError()
    elif canvas.data.iSummaryEndYear-canvas.data.iSummaryStartYear < 0:
        canvas.data.error = True
        displayBadYearError()
    elif canvas.data.iSummaryPlayer in canvas.data.players:
        canvas.data.fSummaryPlayer=canvas.data.players[
            canvas.data.iSummaryPlayer]
    else:
        canvas.data.error = True
        displayPlayerError()

def displayBadYearError():
    text = "Pick an end year that's the same as or after the start year!"
    tkMessageBox.showerror("Steee-rrriike Three!", text)

def displayNoEntryError():
    text = """You need to enter a player!
Click the "Help with ID Codes" button for more."""
    tkMessageBox.showerror("Swing and a miss!", text)

def displayPlayerError():
    text = """Sorry, that's not a valid player name or ID.
Click the "Help with ID Codes" button for more."""
    tkMessageBox.showerror("Swing and a miss!", text)

def displayNoPAsError(canvas):
    text = ("That player didn't have any plate appearances during the given" +
    " years.\nTry refining your search.")
    tkMessageBox.showerror("You're Out!", text)
    canvas.delete(canvas.data.rectangle)
    canvas.delete(canvas.data.loading)

def calcBattingStats(canvas):
    player = canvas.data.fSummaryPlayer
    tPlayer = Parser.RetrosheetPlayer(player[0],player[2],player[1],player[3])
    if FileWriter.getBattingStats(tPlayer, canvas.data.iSummaryStartYear,
                                  canvas.data.iSummaryEndYear) == None:
        canvas.data.error = True
        displayNoPAsError(canvas)
    else:
        tPlayer=Parser.RetrosheetPlayer(player[0],player[2],player[1],player[3])
        # redefine to avoid doubling all the data
        (players, rPlayer) = FileWriter.getBattingStats(
            tPlayer, canvas.data.iSummaryStartYear, canvas.data.iSummaryEndYear)
        rPlayer.calcSummaryBattingStats()
        canvas.data.retroPlayer = rPlayer

def displayPitchingStatsError(canvas): # the pitching calculations were too much
    # for this project, but I decided to leave it in as something that will
    # be added at some point in the future.
    text = """Pitching statistics aren't available yet.
Please wait for updates before searching for them."""
    tkMessageBox.showerror("You're out!", text)

def drawSummaryBatting(root, canvas):
    if len(canvas.data.retroPlayer.seasons) == 0:
        drawNoDataError()
    else:
        drawSummaryBattingGrid(canvas)
        drawSummaryBattingHeadings(root, canvas)
        drawSummaryBattingInfo(canvas)

def drawNoDataError():
    text = "The player in question didn't appear during those years. Try again."
    tkMessageBox.showerror("Steee-rrriike Three!", text)

def drawSummaryBattingGrid(canvas): # same as play-by-play version
    (sXOffset, sYOffset) = (50, 3*canvas.data.height/10)
    (canvas.data.sXOffset, canvas.data.sYOffset) = (sXOffset, sYOffset)
    verticalGap = 17 if len(canvas.data.retroPlayer.seasons) > 20 else 20
    rows = len(canvas.data.retroPlayer.seasons) # verticalGap sizes to fit
    (canvas.data.verticalGap, canvas.data.rows) = (verticalGap, rows)
    for row in xrange(rows+3):
        canvas.create_line(sXOffset, sYOffset+verticalGap*row,
                           canvas.data.width-sXOffset, sYOffset+verticalGap*row)
    fieldWidths = (5,4,4,4,4,4,3,3,3,4,3,4,4,4,4,4,4,4,3,3,3,5,4,4)
    canvas.data.fieldWidths = fieldWidths
    extra = (canvas.data.width-sXOffset*2)/(float(sum(fieldWidths)))
    canvas.data.extra = extra
    canvas.create_line(sXOffset,sYOffset,sXOffset,sYOffset+verticalGap*(rows+2))
    for position in xrange(len(fieldWidths)):
        canvas.create_line(sXOffset+sum(fieldWidths[0:position+1])*extra,
                           sYOffset,
                           sXOffset+sum(fieldWidths[0:position+1])*extra,
                           sYOffset+verticalGap*(rows+2*(position != 0)))

def drawSummaryBattingHeadings(root, canvas):
    data = canvas.data # fields based on Baseball-Reference arrangement
    fields = ["Year","Team","G","PA","AB","H","2B","3B","HR","RBI",
              "BB","SO","BA","OBP","SLG","OPS","TB","HBP","SH","SF","IBB",
              "AO", "AC", "AP"]
    data.fields = fields
    for position in xrange(len(data.fieldWidths)):
        canvas.create_text(data.sXOffset+(sum(data.fieldWidths[
            0:position])+data.fieldWidths[position]/2.0)*data.extra,
                           data.sYOffset,
                           text=fields[position],anchor="s",font = "Times 14")

def calcSummaryBattingInfo(canvas, year): # massive function to get every stat
    (year, self) = (str(year), canvas.data.retroPlayer) # needed for the table
    (team, G) = (self.seasons[year].teams, self.seasons[year].stats["G"])
    (PA, AB) = (self.seasons[year].stats["PA"], self.seasons[year].stats["AB"])
    (H, R) = (self.seasons[year].stats["H"], self.seasons[year].stats["R"])
    (doub,trip)=(self.seasons[year].stats["2B"], self.seasons[year].stats["3B"])
    (HR, RBI) = (self.seasons[year].stats["HR"],self.seasons[year].stats["RBI"])
    (SB, CS) = (self.seasons[year].stats["SB"], self.seasons[year].stats["CS"])
    (BB, SO) = (self.seasons[year].stats["BB"], self.seasons[year].stats["SO"])
    (BA, OBP) = (self.seasons[year].stats["BA"],self.seasons[year].stats["OBP"])
    (SLG, OPS)=(self.seasons[year].stats["SLG"],self.seasons[year].stats["OPS"])
    (TB, HBP) = (self.seasons[year].stats["TB"],self.seasons[year].stats["HBP"])
    (SH, SF) = (self.seasons[year].stats["SH"], self.seasons[year].stats["SF"])
    (IBB,AO) = (self.seasons[year].stats["IBB"], self.seasons[year].stats["AO"])
    (AC, AP) = (self.seasons[year].stats["AC"], self.seasons[year].stats["AP"])
    AP = float(AC) / AO
    (BA, OBP) = ("%.3f" % round(BA, 3), "%.3f" % round(OBP, 3))
    (SLG, OPS) = ("%.3f" % round(SLG, 3), "%.3f" % round(OPS, 3))
    AP = ("%.3f" % round(AP, 3))
    (BA, OBP, SLG, OPS, AP) = (BA[1:5], OBP[1:5], SLG[1:5], OPS[1:5], AP[1:5])
    if len(team) > 1: team = team[0]+"+" # shows midseason trades in aggregate
    return (year, team, G, PA, AB, H, doub, trip, HR, RBI, BB, SO,
            BA, OBP, SLG, OPS, TB, HBP, SH, SF, IBB, AO, AC, AP)    

def initBattingTotals(): # everything starts as 0
    [tG, tPA, tAB, tR, tH, tdoub, ttrip, tHR, tRBI, tSB, tCS, tBB, tSO,
            tBA, tOBP, tSLG, tOPS, tTB, tHBP, tSH, tSF, tIBB, tAO, tAC, tAP] = [
                0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    totals = [tG, tPA, tAB, tH, tdoub, ttrip, tHR, tRBI, tBB, tSO,
            tBA, tOBP, tSLG, tOPS, tTB, tHBP, tSH, tSF, tIBB, tAO, tAC, tAP]
    return totals # list rather than tuple so I can assign into it later

def updateBattingTotals(totals, info):
    for stat in xrange(len(info)-2):
        totals[stat] += float(info[stat+2])
    (tG, tPA, tAB, tH, tdoub, ttrip, tHR, tRBI, tBB, tSO, tAB, tOBP,
            tSLG, tOPS, tTB, tHBP, tSH, tSF, tIBB, tAO, tAC, tAP) = totals
    (tBA, tOBP) = (float(tH)/tAB, float(tH+tBB+tHBP)/(tAB+tBB+tHBP+tSF))
    tSLG = float(tTB)/tAB
    tOPS = tOBP + tSLG # does the totals and the averages
    tAP = float(tAC) / tAO
    (tBA, tOBP) = ("%.3f" % round(tBA, 3), "%.3f" % round(tOBP, 3))
    (tSLG, tOPS) = ("%.3f" % round(tSLG, 3), "%.3f" % round(tOPS, 3))
    tAP = ("%.3f" % round(tAP, 3))
    (tBA,tOBP,tSLG,tOPS,tAP) = (tBA[1:5],tOBP[1:5],tSLG[1:5],tOPS[1:5],tAP[1:5])
    totals = [tG, tPA, tAB, tH, tdoub, ttrip, tHR, tRBI, tBB, tSO,
            tBA, tOBP, tSLG, tOPS, tTB, tHBP, tSH, tSF, tIBB, tAO, tAC, tAP]
    for item in xrange(len(totals)): totals[item] = float(totals[item])
    return totals
    
def drawSummaryBattingInfo(canvas): # huge function to display the stats
    (sXOffset, sYOffset) = (canvas.data.sXOffset, canvas.data.sYOffset)
    (fieldWidths,verticalGap)=(canvas.data.fieldWidths,canvas.data.verticalGap)
    sXOffset -= 2
    sYOffset += verticalGap/2
    (font, extra) = (12 if verticalGap == 17 else 13, canvas.data.extra)
    (games, rateStats) = (162, [10,11,12,13,21])
    (index, totals, averages) = (-1, initBattingTotals(), [0]*24)
    for year in sorted(canvas.data.retroPlayer.seasons):
        info = calcSummaryBattingInfo(canvas, year)
        totals = updateBattingTotals(totals, info)
        index += 1 # this loop gets the necessary info for each year
        for position in xrange(len(info)):
            canvas.create_text(sXOffset+sum(fieldWidths[0:position+1])*extra,
                               sYOffset+verticalGap*index, text=info[position],
                               font="Times %d"%font, anchor="e")
    reduction = float(totals[0])/games # normalize to 162-game season
    for item in xrange(len(totals)):
        if item not in rateStats:
            totals[item] = int(totals[item])
            averages[item] = int(round((totals[item]/reduction)))
        else: # this section rounds for regular stats, and formats rate stats
            totals[item] = (str(totals[item])[1:5]+"0")[:4] # with 3 decimals
            averages[item] = ("." + str(totals[item])[1:5]+"0")[:4]
    drawTotals(canvas, info, fieldWidths, extra, index, averages, totals)


def drawTotals(canvas,info,fieldWidths,extra,index,averages,totals):
    (sXOffset, sYOffset) = (canvas.data.sXOffset, canvas.data.sYOffset)
    verticalGap = canvas.data.verticalGap
    sXOffset -= 2
    sYOffset += verticalGap/2
    font = 12 if verticalGap == 17 else 13
    for position in xrange(2,len(info)): # sum of yearly info
        canvas.create_text(sXOffset+sum(fieldWidths[0:position+1])*extra,
                           sYOffset+verticalGap*(index+1),text=totals[
                               position-2],font="Times %d bold"%font,anchor="e")
        canvas.create_text(sXOffset+sum(fieldWidths[0:position+1])*extra,
                           sYOffset+verticalGap*(index+2),text=averages[
                               position-2],font="Times %d bold"%font,anchor="e")
    canvas.create_text(sXOffset+fieldWidths[0]*extra, # totals info
                       sYOffset+verticalGap*len(
                           canvas.data.retroPlayer.seasons),text="TOTALS:",
                       font = "Times %d bold"%font)
    canvas.create_text(sXOffset+fieldWidths[0]*extra, # averages info
                       sYOffset+verticalGap*(len(
                           canvas.data.retroPlayer.seasons)+1),
                       text="AVG PER 162:",font="Times %d bold"%font)


#################


if __name__ == "__main__":
    run()
    


#################

# Test functions...
# What can I test that's non-graphic? If the stuff shows up, I check that it
# was accurate. That's about it.

