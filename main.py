##........................................................
#  Name         : K.A.M.D.Kariyawasam - 19/ENG/049
#                 T.Karthick - 19/ENG/050
#                 K.A.D.G.Kasthuriarachchi - 19/ENG/053
#  Group Number : 05
#  Module       : CO2210 Programming Quest
#  Quest Number : 09
## .......................................................


import PySimpleGUI as sg
import matplotlib.pyplot as plt
import random
import time


class Person:
    __deathCount = 0
    __infectedCount = 0
    __hospitalizedCount = 0
    __recoveredCount = 0

    def __init__(self, age, famID=-1):
        self.__isInfected = False
        self.__isHospitalized = False
        self.__age = age
        self.__famID = famID  # -1 if person don't have a family
        if self.__age < 18:
            self.__lowerRange = 10.0
            self.__upperRange = 20.0
        elif self.__age > 65:
            self.__lowerRange = 35.0
            self.__upperRange = 60.0
        else:
            self.__lowerRange = 15.0
            self.__upperRange = 40.0
        self.__reduceRate = round(random.uniform(5.00, 10.00),
                                  2)  # for ex, inintail children sp rate 10 <-> 20 , if mask of 10 <-> (20 - (5~10))
        self.__daysFromInf = 0

    @staticmethod
    def getDeathCount():
        return Person.__deathCount

    @staticmethod
    def getInfectedCount():
        return Person.__infectedCount

    @staticmethod
    def getHospitalizedCount():
        return Person.__hospitalizedCount

    @staticmethod
    def getRecoveredCount():
        return Person.__recoveredCount

    def setMask(self, enforced):
        self.__upperRange -= self.__reduceRate if enforced else -self.__reduceRate

    def havFam(self):
        return self.__famID != -1

    def isInfected(self):
        if not self.__isInfected:
            Person.__infectedCount += 1
            self.__isInfected = True

    def isHospitalized(self):
        if not self.__isHospitalized:
            Person.__hospitalizedCount += 1
            self.__isHospitalized = True

    def isRecovered(self):
        Person.__recoveredCount += 1
        self.__isInfected = False
        self.__isHospitalized = False

    def incrementInfDay(self):
        self.__daysFromInf += 1

    def getDayCount(self):
        return self.__daysFromInf

    def getFamID(self):
        return self.__famID

    def gotInfected(self):
        guess = round(random.uniform(0.00, 100.00), 2)
        return guess >= self.__lowerRange and guess <= self.__upperRange

    def __del__(self):
        Person.__deathCount += 1


class Family:
    def __init__(self):
        self.__memberID = []

    def addMemberID(self, i):
        self.__memberID.append(i)

    def getMemberID(self):
        return self.__memberID


sg.theme('Default')

# display layout of the window
column1 = [[sg.Text('Simulation Data')],
           [sg.Multiline("Press [Start] to start the simulation.\nApply enforcement conditions at any date needed."
                         "\nPlease do not select other options while simulation is running.",
            disabled=True, size=(60, 30), key="-SIMULATION DATA-")],
           [sg.Text('')]]

column2 = [[sg.Frame(title='Enforcements',
                     size=(200, 115),
                     layout=[[sg.Checkbox('Enforce mask wearing', key="-ENFORCE MASK-")],
                             [sg.Checkbox('Enforce travel restrictions', key="-TRAVEL RESTRICT-")],
                             [sg.Button(size=(22, 1), button_text='Apply')]])],
           [sg.Text('\n')],
           [sg.Frame(title='Graphs',
                     size=(200, 155),
                     layout=[[sg.Button(size=(22, 1), button_text='Daily Infections')],
                             [sg.Button(size=(22, 1), button_text='Daily Hospitalizations')],
                             [sg.Button(size=(22, 1), button_text='Daily Fatalities')],
                             [sg.Button(size=(22, 1), button_text='Daily Recoveries')]])],
           [sg.Text('')],
           [sg.Button(size=(24, 1), button_text='Show Cumulative Data')],
           [sg.Text('\n')],
           [sg.Button(size=(24, 2), button_color='green', button_text='Start')]]

layout = [[sg.Column(column1), sg.Column(column2)]]

window = sg.Window('COVID-19 Simulation', layout, margins=(20, 10))

ttlFamily = 100000
ttlPop = 1000000

ageProb = [0.0, 0.0]

personsDict = {}
famsDict = {}


def initializePop():
    # initalize persons with fam
    for x in range(ttlFamily):
        famMembers = random.randint(2, 7)
        famsDict[x] = Family()

        for y in range(famMembers):
            age = 0
            while True:
                age = random.randint(1, 100);  # assume person's age range is bw 1 - 100
                if ageProb[0] >= 0.2:
                    if age > 65:
                        ageProb[1] += 1e-6
                        break
                    elif age >= 18 and age <= 65:
                        break
                elif ageProb[0] <= 0.2 and age < 18:
                    ageProb[0] += 1e-6
                    break
            famsDict[x].addMemberID(len(personsDict))
            personsDict[len(personsDict)] = Person(age, x)

    oldLen = len(personsDict)

    # persons w/o fam
    for x in range(oldLen, ttlPop):  # assume all children have families
        age = 0
        while True:
            age = random.randint(1, 100);
            if age > 65:
                ageProb[1] += 1e-6
                break
            elif (age >= 18 and age <= 65) and ageProb[1] >= 0.3:
                break

        personsDict[len(personsDict)] = Person(age)

    window['-SIMULATION DATA-'].update("Population Generated.\n")
    window.refresh()

    startSim()

    # list's first part contains families and later part contains
    # families less people -- we didn't randomized it -- as family
    # familyless doesn't matter in this quest


dailyInfCount = [1]  ### COUNT DAILY INF RATE
dailyHospCount = []  ### COUNT DAILY HOSP RATE
dailyFatalCount = []  ### COUNT DAILY FATAL RATE
dailyRecoveryCount = []  ### COUNT DAILY REC RATE

infectedPersonsDict = {}
hospitalizedPersonDict = {}
recoveredPersonDict = {}

travelRestrictEnforced = False
maskEnforced = False


def startSim():
    currDay = 0

    spreadRate = 0.1

    firstPer = random.randint(0, 999999)
    infectedPersonsDict[firstPer] = personsDict.pop(firstPer)

    # MARK INFECTED
    infectedPersonsDict[firstPer].isInfected()

    while currDay < 50:
        dailyFatalCount.append(0)
        dailyHospCount.append(0)
        dailyRecoveryCount.append(0)

        window['-SIMULATION DATA-'].print(f'\nDay : {currDay + 1}')
        window.refresh()
        for person in dict(infectedPersonsDict):
            # ASSUME IF PERSON GOT HOSPITALIZED THEN VIRUS WON"T SPREAD VIA HIM TO FAMILY
            # FIRST CHK : FAMILY
            if infectedPersonsDict[person].havFam():
                # CHECK IF ANYONE INFECTED
                famMembersID = famsDict[infectedPersonsDict[person].getFamID()].getMemberID()

                for x in famMembersID:
                    if (x != person):
                        randomGuess = round(random.uniform(0.00, 100.00), 2)
                        # ASSUME PEOPLE DONT WEAR MASK WHEN WITH FAMILY
                        if randomGuess >= 40.0 and randomGuess <= 80.0:
                            try:
                                infectedPersonsDict[x] = personsDict.pop(x)
                                # MARK INFECTED
                                infectedPersonsDict[x].isInfected()
                                dailyInfCount[currDay] += 1
                            except KeyError:
                                pass

            # HOSPITALIZE IF DAY 5 REACHED -- As VIRUS WON"T SPREAD TO FAMILY VIA INF PERSON WHEN THERE ARE IN HOSPITAL WE CAN NEGLECT THEM FOR FUTURE CALC
            if infectedPersonsDict[person].getDayCount() >= 5:
                infectedPersonsDict[person].isHospitalized()
                hospitalizedPersonDict[person] = infectedPersonsDict.pop(person)
                dailyHospCount[currDay] += 1

            else:
                # INC DAY
                infectedPersonsDict[
                    person].incrementInfDay()  # WE CAN INCREMENT DAY COUNT OF HOSPITALIZED PERSON IN HOSIPITALIZED SECTION

        if not travelRestrictEnforced:
            for person in dict(personsDict):
                personsDict[person].setMask(maskEnforced)
                randomGuess = round(random.uniform(0.00, 100.00), 2)

                if (randomGuess < spreadRate and personsDict[person].gotInfected()):
                    infectedPersonsDict[person] = personsDict.pop(person)
                    # MARK INFECTED
                    infectedPersonsDict[person].isInfected()
                    dailyInfCount[currDay] += 1
            spreadRate += 0.5

        else:
            spreadRate = max(0.1, spreadRate - 2)

        for person in dict(hospitalizedPersonDict):
            if hospitalizedPersonDict[person].getDayCount() >= 10:
                hospitalizedPersonDict[person].isRecovered()
                recoveredPersonDict[person] = hospitalizedPersonDict.pop(
                    person)  # As they have 5 - 6 months of immunitiy power we dont have to check them (coz sim is only for 50 days)
                dailyRecoveryCount[currDay] += 1

            else:
                # CHECK FATAILITY
                randomGuess = round(random.uniform(0.00, 100.00), 2)
                if randomGuess < 0.1:
                    # DIED
                    del hospitalizedPersonDict[person]
                    dailyFatalCount[currDay] += 1
                else:
                    # INC DAY
                    hospitalizedPersonDict[person].incrementInfDay()

        window['-SIMULATION DATA-'].print(
            f'Number of infected patients : {dailyInfCount[currDay]}\
            \nNumber of hospitalized patients : {dailyHospCount[currDay]}'
            f'\nNumber of recovered patients : {dailyRecoveryCount[currDay]}\
            \nNumber of patients died : {dailyFatalCount[currDay]}')
        window.refresh()
        time.sleep(2)

        currDay += 1
        dailyInfCount.append(0)

    window['-SIMULATION DATA-'].print("\nSimulation Completed.")
    window.refresh()

    dailyInfCount.pop()


while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    if event == 'Start':
        # start simulation
        window['-SIMULATION DATA-'].update("Generating Population. Please wait...")
        window.perform_long_operation(initializePop, '-THREAD OP-')

    if values["-ENFORCE MASK-"]:
        maskEnforced = True
    elif not values["-ENFORCE MASK-"]:
        maskEnforced = False
    if values["-TRAVEL RESTRICT-"]:
        travelRestrictEnforced = True
    elif not values["-TRAVEL RESTRICT-"]:
        travelRestrictEnforced = False
    if event == 'Apply':
        pass

    if event == 'Daily Infections':
        plt.figure("Daily infections")
        plt.plot(list(range(1, 51)), dailyInfCount, marker='o', markersize=2)
        plt.title("Infections per day")
        plt.xlabel("Day")
        plt.ylabel("Number of people")
        plt.show()
    if event == 'Daily Hospitalizations':
        plt.figure("Daily hospitalizations")
        plt.plot(list(range(1, 51)), dailyHospCount, marker='o', markersize=2)
        plt.title("Hospitalizations per day")
        plt.xlabel("Day")
        plt.ylabel("Number of people")
        plt.show()
    if event == 'Daily Fatalities':
        plt.figure("Daily fatalities")
        plt.plot(list(range(1, 51)), dailyFatalCount, marker='o', markersize=2)
        plt.title("Fatalities per day")
        plt.xlabel("Day")
        plt.ylabel("Number of people")
        plt.show()
    if event == 'Daily Recoveries':
        plt.figure("Daily recoveries")
        plt.plot(list(range(1, 51)), dailyRecoveryCount, marker='o', markersize=2)
        plt.title("Recoveries per day")
        plt.xlabel("Day")
        plt.ylabel("Number of people")
        plt.show()

    if event == 'Show Cumulative Data':
        sg.popup_scrolled(f'Total Infected : {Person.getInfectedCount()}\nTotal Recovered : {Person.getRecoveredCount()}\
            \nTotal Deaths : {Person.getDeathCount()}\nTotal Uninfected : {len(personsDict)}', title="Simulation data")

window.close()
