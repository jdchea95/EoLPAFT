import PySimpleGUI as sg
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np

from tkinter import *
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import pandas as pd

import PIL.Image as Image
from PIL import Image, ImageTk

import xlsxwriter

from datetime import datetime

from plotly.offline import plot
import plotly.graph_objs as go

from html2image import Html2Image

from tktooltip import ToolTip
import io

EoLPlasticgui = tk.Tk()
EoLPlasticgui.title("Generic Scenario of End-of-Life Plastics - Chemical Additives")

my_program= ttk.Notebook(EoLPlasticgui)
my_program.pack(fill="both",expand=1)

w = 1200 # width for the Tk root
h = 400 # height for the Tk root
#get screen width and height
ws = EoLPlasticgui.winfo_screenwidth() # width of the screen
hs = EoLPlasticgui.winfo_screenheight() # height of the screen
#calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
#set the dimensions of the screen  and where it is placed
EoLPlasticgui.geometry('%dx%d+%d+%d' % (w, h, x, y-25))

    
#Create frames for GUI
my_frame1 = Frame(my_program, width=300, height=300, bg="white") #Home frame
userSpecificationsFrame = Frame(my_program, width = 300, height = 300, bg = 'white') #User specs frame
userSpecificationsCanvas = Canvas(userSpecificationsFrame, bg = 'white') #Canvas within user specs frame to allow for scrollbar
my_frame2 = Frame(userSpecificationsCanvas, width=300, height=300, bg="white") #Frame to put widgets on for user specs frame
my_frame3 = Frame(my_program, width=300, height=300, bg="white") #Material Data tab
my_frame4 = Frame(my_program, width=300, height=300, bg="white") #Will be for assumptions tab, but for now has been removed until assumptions tab is ready
my_frame5 = Frame(my_program, width=300, height = 300, bg = 'white') #For LCI Tab
dataAnalysisFrame = Frame(my_program, width = 300, height = 300, bg ='white') #Added to program for canvas on next line
streamFrame = Frame(my_program, width = 300, height = 300, bg = 'white') #Will be for pop-up
sensAnalFrame = Frame(my_program, width = 30, height = 300, bg = 'white') #for sensitivity analysis
mat_loopTab = Frame(my_program, width = 30, height = 300, bg = 'white') #for material loop scenario
epr_analysis = Frame(my_program, width = 30, height = 300, bg = 'white') #for EPR tabe

#Adds tabs to top
my_program.add(my_frame1, text="Home")
my_program.add(userSpecificationsFrame, text="User Specifications")
my_program.add(streamFrame, text = 'Material Flow Results')
my_program.add(dataAnalysisFrame, text = 'Scenario Visualization')
my_program.add(my_frame5, text = 'Life Cycle Inventory')
my_program.add(sensAnalFrame, text = 'Scenario Analysis')
my_program.add(epr_analysis, text = 'EPR')
my_program.add(mat_loopTab, text = 'Material Loops and Accumulation')

##########################################################################################################
##########################################################################################################
#Sensitivity Analysis Sheet


#Create dictionaries of constant values that are from assumptions and will be used in calculations
assumedValues={"Plastic waste lost to littering":0.02, "Plastic waste leak after landfill":0.1, "Plastic content in compost":0.01, 
               "Total compost stream mass multiplier":1.01, "Total mass of plastic in compost stream(Tons):":426_000, 
               "Additive migration Fraction":0.02, "Incineration Efficiency Fraction":0.9999}

#Creates dictionary of low additive Fractions. key = type of additive F6:F21; value = low value for bulk mass proportion G6:G21
lowAdditiveFractions = {"Plasticizer":0.1, "Flame Retardant":0.007, "UV Stabilizer": 0.005, "Heat Stabilizer":0.005, "Antioxidant":0.005, "Slip Agent":0.001, "Lubricant":0.001, 
                        "Antistatic":0.001, "Curing Agent":0.001, "Blowing Agent":0.005, "Biocide":0.00001, "Colorant": 0.0025, "Organic Pigment":0.00001, 
                        "Clarifier/Toner": 0.00015, "Inorganic Pigment": 0.0001, "Filler": 0.00001, "Reinforcement": 0.15}

#Create lists of categories to be paired with data for each year
conditionsCategories = ["Total MSW (Tons):", "Total Plastic waste (Tons):", "Plastic Recycled (Total, domestic and export)", 
                        "Plastic Domestically Recycled Fraction", "Efficiency of Domestic Recycling", "Plastic Export Fraction", 
                        "Plastic Re-Export Fraction", "Plastic Incinerated Fraction", "Plastic Landfilled Fraction", "Waste Facility Emissions"]

typesOfWastes = ["Misc. Inorganic Waste", "Other", "Yard Trimmings", "Food", "Rubber, Leather and Textiles", "Wood", "Metals", "Glass", 
                 "Paper and Paperboard", "Plastics"]

typesOfWastesForCalculations = ["Misc. Inorganic Waste", "Other", "Yard Trimmings", "Food", "Rubber, Leather and Textiles", "Wood", "Metals", "Glass", 
                 "Paper and Paperboard"] #Note: This is the same as the one above without a plastics string

#Creates list of strings of types of plastics in domestic calculations
typesOfPlasticDomestic = ["PET", "HDPE", "PVC", "LDPE", "PLA", "PP", "PS", "Other Resin"]

#Creates list of strings of types of plastics recycled in domestic calculations
recycledTypesOfPlasticDomestic = ["Recycled "+ i for i in typesOfPlasticDomestic]

#Creates list of strings of types of plastics in international calculations
typesOfPlasticsInternational = ["Ethylene", "Vinyl Chloride", "Styrene", "Other"]

#Categories for life cycle inventory (formerly known as material flow analysis)
matFlowAnalSumCategories = ["PET", "HDPE", "PVC", "LDPE", "PLA", "PP", "PS", "Other Resin", "Chemical Additives"]

#Dictionary of densities of plastics for later calculations
polymerWasteDensity = {"PET":1.365, "HDPE":952.5, "PVC":1.455, "LDPE":0.925, "PLA":1.26, "PP":905, "PS":1.055, "Other Resin":1.29}

#Creates list for material information that will be used for energy footprint sensitivity analysis. Note: First and second values will be 
#recalculated for each sensitivity analysis

petMaterialValues = [0.799, 0.67, 85, 39, 3.9, 2.4, 80.1, 4.25, 4.59*10**5, 3.67*10**10, 1.95*10**6]
hdpeMaterialValues = [0.708, 0.67, 80, 40, 3.26, 2.28, 78.5, 3.87, 3*10**5, 2.36*10**10, 1.16*10**6]
pvcMaterialValues = [0.885, 0.67, 59, 36, 2.5, 2.2, 57.9, 3.28, 36647, 2.12*10**9, 1.2*10**5]
ldpeMaterialValues = [0.731, 0.67, 67.5, 50, 2.8, 2.9, 82.6, 4.23, 214150, 1.77*10**10, 9.06*10**5]
plaMaterialValues = [0, 0.67, 51.5, 36.5, 3.6, 2.2, 77.2, 5.4, 0, 0, 0]
ppMaterialValues = [.655, 0.67, 79, 50, 3.1, 2.1, 90, 3.64, 22642, 2.04*10**9, 8.24*10**4]
psMaterialValues = [.882, .67, 97, 47.5, 3.8, 2.9, 80, 4.44, 28898, 2.31*10**9, 1.28*10**5]
otherMaterialValues = [0.906, 0.67, 87, 29.6, 3.7, 1.3, 50.8, 2.16, 1281464, 6.51*10**10, 2.77*10**6]


#Creates empty lists that will be filled by user input before calculations are made
plasticRecycled = 0

conditions = []

mswCompProp = []

mswRecyc = []

mswIncin = []

mswLand = []

mswCompost =[]

repRecPlastics = []

repPlasticImport = []

repPlasticsExport = []

repPlasticsReExport = []

plasticLandFractionsList = []

plasticRecycledFractionsList = []

global plasticIncinFractionsList
plasticIncinFractionsList = []

sensitivityPoints = [] #willbe used to generate sensitivity analysis plot

ghgEmitSA = [] #will be used to generate sensitivity analysis plot

energyFootprintPoints = []

litterAnal = []

waterAnal = []

chemRecycData = []

sensitivityPoints_epr = [] #willbe used to generate sensitivity analysis plot

ghgEmitSA = [] #will be used to generate sensitivity analysis plot

energyFootprintPoints = []

litterAnal_epr = []

waterAnal_epr = []

chemRecyc_addies = []

#Create 2018 data which will be added to the lists above as input by user:


conditions2018 = [292_360_000.0, 8.4, (0.084-0.0456706)*100, 0.6670*100, 0.0456706*100, 0.0002*100, 0.172271*(1-0.084)*100, 100*(1-0.084-0.172271*(1-0.084)), 109_000_000, 630_000_000] #B2:B10

mswCompProp2018 = [1.39, 1.56, 12.1, 21.59, 8.96, 6.19, 8.76, 4.19, 23.05, 12.2] #B21:B30

mswRecyc2018 = [69_000_000.0, 0, 1.4, 0, 0, 6.06, 4.49, 12.63, 4.43, 66.6, 4.38] #B32:B42

mswIncin2018 = [34_560_000.0, 2.3, 1.9, 7.4, 21.8, 16.6, 8.2, 8.5, 4.7, 12.2, 16.3] #B44:B54

mswLand2018 = [146_180_000.0, 2.2, 2, 7.2, 24.1, 11.1, 8.3, 9.5, 5.2, 11.8, 18.5] #B56:B66

mswCompost2018 =[42_600_000.0, 0, 0, 52.3, 47.7, 0, 0, 0, 0, 0, 0] #B68:B78

repRecPlastics2018 = [910000.0, 560000.0, 0, 370000.0, 0, 50000.0, 20000.0, 1110000.0] #F9:F16

repPlasticImport2018 = [139791.0, 36647.0, 19841.0, 778806.0] #E22:#25

repPlasticsExport2018 = [920477.0, 137493.0, 28071.0, 543487.0] #F22:F25

repPlasticsReExport2018 = [7246.0, 34.0, 27.0, 1038.0] #G22:G25

plasticLandFractionsList2018 = [13.410900183711, 17.5750153092468, 2.57195345988977, 25.1684017146356, 0.275566442131047, 24.8009797917942, 6.85854255970606, 9.33864053888549]

plasticRecycledFractionsList2018 = [14.8179271708683, 17.6470588235294, 2.35294117647059, 24.0616246498599, 0.252100840336134, 22.8291316526611, 6.33053221288515, 11.6526610644258]

plasticIncinFractionsList2018 = [13.410900183711, 17.5750153092468, 2.57195345988977, 25.1684017146356, 0.275566442131047, 24.8009797917942, 6.85854255970606, 9.33864053888549]
 
chemRecyc2018 = [0 for i in range(3)]

#Creates list of each kind of additive added to each type of plastic based on stream 6 additive categories
PETadditiveTypes = ["UV Stabilizer", "Flame Retardant", "Antistatic", "Clarifier/Toner", "Organic Pigment"]

HDPEadditiveTypes = ["Antioxidant", "UV Stabilizer", "Colorant", "Flame Retardant", "Heat Stabilizer", "Organic Pigment"]

PVCadditiveTypes = ["Plasticizer", "Antioxidant", "Slip Agent", "Heat Stabilizer", "Lubricant", "Colorant", "Organic Pigment"]

PPadditiveTypes = ["Antioxidant", "Slip Agent", "UV Stabilizer", "Flame Retardant", "Clarifier/Toner", "Organic Pigment"]

PSadditiveTypes = ["Antioxidant", "Slip Agent", "UV Stabilizer", "Antistatic", "Colorant", "Organic Pigment"]

LDPEadditiveTypes = ["Antioxidant", "Slip Agent", "UV Stabilizer", "Flame Retardant", "Heat Stabilizer", "Colorant", "Organic Pigment"]

PLAadditiveTypes = ["Plasticizer", "Heat Stabilizer", "Filler", "Reinforcement", "Biocide", "Antioxidant", "Colorant"]

otherResinAdditives = ["Plasticizer", "Antioxidant", "UV Stabilizer", "Colorant", "Flame Retardant", "Curing Agent", "Blowing Agent", "Biocide", "Clarifier/Toner", 
                       "Inorganic Pigment", "Heat Stabilizer", "Organic Pigment", "Filler", "Reinforcement", "Lubricant", "Slip Agent", "Antistatic"]

#Creates list of recycled additives
recycledAdditivesList = ["Recycled "+ i for i in otherResinAdditives]

#Creates list of 8 preceding lists
additivesListList = [PETadditiveTypes, HDPEadditiveTypes, PVCadditiveTypes, PPadditiveTypes, PSadditiveTypes, LDPEadditiveTypes, PLAadditiveTypes, otherResinAdditives]

#Will calculate amount of each kind of additive in each kind of plastic based on low additive Fractions and bulk mass; key = types of additives, value = amount of each additive
def additiveMassCalculator(additiveList, plasticType, massDict): #Takes argument of LIST of types of additives going into type of plastic, STRING of type of plastic, then DICT of bulk masses
    newDict = dict(zip(additiveList, [massDict[plasticType]*lowAdditiveFractions[i] for i in additiveList])) #takes bulk mass and multiplies by low additive Fraction for each kind of additive
    return newDict

#Sums mass of additive type in specified stream
def totalOfAdditiveType(typeOfAdditive, listOfAdditiveLists): #Takes argument for STRING of type of additive, and LIST of dicts of additives
    additiveAmount = 0
    for i in listOfAdditiveLists:
        if typeOfAdditive in i: #Checks whether additive is in each list of additives, then adds to total of that additive
            additiveAmount += i[typeOfAdditive]
    return additiveAmount

#Calculates total mass of plastic resin in specific stream
def totalResinCalculator(plasticType, plasticMassDict, additiveMassList): #Takes argument for STRING of plastic type; DICT of bulk masses; DICT of additive masses for specific plastic
    resinMass = plasticMassDict[plasticType]-sum(additiveMassList.values()) #sums additives in plastic's bulk mass, then subtracts to find resin mass
    return resinMass

#Calculates bulk plastic masses in reverse of total resin calculator, based on resin masses
def backwardsLumpPlasticCalculator(resinMassList, typeOfResin, additiveList):
    additiveFraction = sum([lowAdditiveFractions[i] for i in additiveList]) #Finds total Fraction of bulk mass that is resin
    lumpSum = resinMassList[typeOfResin]/(1-additiveFraction) #Divides to find bulk mass
    return lumpSum
        

def trvwListMaker(listOfDicts): #Creates lists that will be eventually added to LCI TRVW tables. Takes argument of list of dictionaries that are to be examined
    newList = []
    for i in matFlowAnalSumCategories: #iterates over list of categories in LCI tables
        subList = []
        q=0
        subList.append(i)
        for d in listOfDicts:
            q = d[i] #Takes value from dict
            try:
                q= float(q) #if value is a number, will and round to three decimal places and add to the TRVW list
                subList.append(round(q,3))
            except ValueError:
                subList.append(d[i]) #if value is not a number (if it is 'Unavaible'), it will be added 
        for b in range(len(subList)):
            if subList[b] == 0:
                subList[b] = "Negligible" #Changes 0's to negligible
        newList.append(subList)
    return newList

def streamSummaryTRVWLister(listOfDicts, category): #creates lists that will be added to stream summary TRVW tables. Takes argument of list of dictionaries that are to be examined, along with string for category that will make up the row of the table
    trvwList = []
    trvwList.append(category) #adds category/row name
    for i in listOfDicts:
        if category in i:
            trvwList.append(i[category]) #adds values corresponding to category from dictionary to this list if there is one, otherwise adds 0
        else: 
            trvwList.append(0)
    return trvwList
#Will accomplish recycling scaling calculations (Sensitivty Facts G9:G16)
def recycleScaler(reportedList, plasticTotal, recycledFraction): #takes input of types of plastics, total plastic mass, and Fraction of plastic that is recycled 
    newScaledDict = dict(zip(typesOfPlasticDomestic,[plasticTotal*recycledFraction/sum(reportedList)*i for i in reportedList])) #creates dictionary from above list
    return newScaledDict

def trvwRounder(num): #rounds numbers in stream summary trvw based on its magnitude
    value = 0
    if isinstance(num, str):
        value = num
    elif abs(num)<1:
        if abs(num)<0.5:
            if abs(num)<0.1:
                if abs(num) == 0:
                    value = 0
                else:
                    value = '<0.1'
            else:
                value = '<0.5'
        else: 
            value = '<1'
    else:
        value = '{:,}'.format(round(num))
    return value

def checkEntry(check): #will be used to make sure all data has an input
    if check == []:
        return True

def makeCalculations(sensitivity, chemRecyc):    
    #Add total plastic waste to conditions list, rather than creating redundancy by having user input it themselves
    if len(conditions) != 11:
        conditions.insert(1, mswCompProp[9]*conditions[0])
    
    #creates list of lists of input data
    listOfDataLists = [conditions, mswCompProp, mswRecyc, mswIncin, mswLand, mswCompost, repRecPlastics, repPlasticImport, repPlasticsExport,
                   repPlasticsReExport, plasticLandFractionsList, plasticRecycledFractionsList, plasticIncinFractionsList, chemRecycData] 
    #Checks entry data lists to make sure they have data in there and returns error if necesssary
    for i in listOfDataLists:
        if checkEntry(i):
            gapLabel1.config(text = 'Not all data has been input.')
            return
    #clears LCI tables if they already had data inside
    matFlowManufactureTRVW.delete(*matFlowManufactureTRVW.get_children())
    matFlowUseTRVW.delete(*matFlowUseTRVW.get_children())
    matFlowCSPTRVW.delete(*matFlowCSPTRVW.get_children())
    matFlowMechRecycTRVW.delete(*matFlowMechRecycTRVW.get_children())
    matFlowIncinTRVW.delete(*matFlowIncinTRVW.get_children())
    matFlowLandTRVW.delete(*matFlowLandTRVW.get_children())
    
    
    
    #Creates dict of Fractions of total plastic landfilled are associated with each type of plastic
    plasticLandFractions = dict(zip(typesOfPlasticDomestic, plasticLandFractionsList))

    
    #Creates dictionary of proportion of each type of plastic that has been recycled. key = type of plastic A5:A12; value = proportion of each type of plastic in MSW stream B5:B12
    plasticFractionsRecycled = dict(zip(typesOfPlasticDomestic, plasticRecycledFractionsList))
    
    #Creates dict of incineration Fractions for each kind of plastic. Key = type of plastic, value = proportion of incineration make up
    plasticIncinFractionsDict = dict(zip(typesOfPlasticDomestic, plasticIncinFractionsList))
    
    #Creates dictionary of international recycling values
    repPlasticImportDict = dict(zip(typesOfPlasticsInternational, repPlasticImport))
    
    repPlasticsExportDict = dict(zip(typesOfPlasticsInternational, repPlasticsExport))
    
    repPlasticsReExportDict = dict(zip(typesOfPlasticsInternational, repPlasticsReExport))
    
    #Creates dictionary of scaled recycled masses (key = type of plastic, value = bulk mass of plastic and additives)
    scaledRec = recycleScaler(repRecPlastics, conditions[1], conditions[2]) #G9:G1
    #Find fraction of each type of plastic bulk mass in the scaled recycling dictionary
    scaledRecFractions = dict(zip(typesOfPlasticDomestic, [scaledRec[i]/sum(scaledRec.values()) for i in typesOfPlasticDomestic]))
    reRecyclingRate = 0.1
    
    ##########################################################################################################
    ##########################################################################################################
    #Stream 6 Calculations
    #Sheet = Stream 6 - PWaste Generated
    #Creates dictionary with total mass of each total type of plastic generated (total mass of plastics generated * Fraction of each kind of plastic). key = type of plastic A5:A12; value = bulk mass including additives C5:C12
    plasticsMassDict = dict(zip(typesOfPlasticDomestic, [plasticFractionsRecycled[i] * conditions[1] for i in typesOfPlasticDomestic]))
    
    
    
    #Creates dicts of additive masses in each kind of plastic in 
    PETAdditiveMasses = additiveMassCalculator(PETadditiveTypes, "PET", plasticsMassDict)
    HDPEAdditiveMasses = additiveMassCalculator(HDPEadditiveTypes, "HDPE", plasticsMassDict)
    PVCAdditiveMasses = additiveMassCalculator(PVCadditiveTypes, "PVC", plasticsMassDict)
    PPAdditiveMasses = additiveMassCalculator(PPadditiveTypes, "PP", plasticsMassDict)
    PSAdditiveMasses = additiveMassCalculator(PSadditiveTypes, "PS", plasticsMassDict)
    LDPEAdditiveMasses = additiveMassCalculator(LDPEadditiveTypes, "LDPE", plasticsMassDict)
    PLAAdditiveMasses = additiveMassCalculator(PLAadditiveTypes, "PLA", plasticsMassDict)
    otherResinAdditivesMasses = additiveMassCalculator(otherResinAdditives, "Other Resin", plasticsMassDict)
    
    #Creates list of preceding 8 dicts
    listOfStream6Additives_ = [PETAdditiveMasses, HDPEAdditiveMasses, PVCAdditiveMasses, LDPEAdditiveMasses,   PLAAdditiveMasses,
                                   PPAdditiveMasses, PSAdditiveMasses, otherResinAdditivesMasses]
    
    
    averageDensityCalculation = sum([polymerWasteDensity[i]*plasticFractionsRecycled[i] for i in typesOfPlasticDomestic])* 0.00000110231
    ##########################################################################################################################
    #Stream 16 Calculations
    #Sheet = Stream 16 - MechRecyc
    
    #Creates dictionary of bulk masses by multiplying scaled recycling values by the ratio of domestic recycled plastic to total recycled plastic
    stream16PlasticCalcMasses = dict(zip(typesOfPlasticDomestic, [conditions[3]/conditions[2]*scaledRec[i] for i in typesOfPlasticDomestic]))
    
    #Creates dictionary of masses of each kind of additive in each kind of plastic
    stream16PET = additiveMassCalculator(PETadditiveTypes, "PET", stream16PlasticCalcMasses)
    stream16HDPE = additiveMassCalculator(HDPEadditiveTypes, "HDPE", stream16PlasticCalcMasses)
    stream16PVC = additiveMassCalculator(PVCadditiveTypes, "PVC", stream16PlasticCalcMasses)
    stream16PP = additiveMassCalculator(PPadditiveTypes, "PP", stream16PlasticCalcMasses)
    stream16PS = additiveMassCalculator(PSadditiveTypes, "PS", stream16PlasticCalcMasses)   
    stream16LDPE = additiveMassCalculator(LDPEadditiveTypes, "LDPE", stream16PlasticCalcMasses)
    stream16PLA = additiveMassCalculator(PLAadditiveTypes, "PLA", stream16PlasticCalcMasses)
    stream16Other = additiveMassCalculator(otherResinAdditives, "Other Resin", stream16PlasticCalcMasses)
    
    #Creates dict of emissions factors per M24:M31. Key = type of additive, value = emission factor
    emissionFactors = {"PET":-1.13, "HDPE":-.88, "PVC":0, "LDPE":0, "PLA": 0, "PP":0, "PS":0, "Other Resin":-1.03}
    
    #Creates list of additive dicts in stream 16 
    listOfstream16Additives = [stream16PET, stream16HDPE, stream16PVC, stream16LDPE, stream16PLA, stream16PP, stream16PS,  stream16Other]
    
    #Calculates total amount of each kind of additive in stream 16; key = type of additive, value = total mass of additive
    totalAdditivesStream16_ = dict(zip(otherResinAdditives, [totalOfAdditiveType(i, listOfstream16Additives) for i in otherResinAdditives])) #Dict of additive in stream 16
    
    #Calculates Fraction of each additive of total mass of additives in stream 16; key = type of additive, value = Fraction of total 
    additiveFractionsStream16_ = dict(zip(otherResinAdditives, [totalAdditivesStream16_[i]/sum(totalAdditivesStream16_.values()) for i in otherResinAdditives]))
    
    #Calculates total amount of each resin in stream 16; key = type of plastic, value = mass of resin
    stream16ResinMasses_ = dict(zip(typesOfPlasticDomestic, [totalResinCalculator(typesOfPlasticDomestic[i], stream16PlasticCalcMasses, listOfstream16Additives[i]) for i in range(8)]))
    
    
    ############################################################################################
    #Stream 17
    
    #Creates dict by calculating emissions from stream 16 per emissions factors and converts to Tons of CO2. 
    #Multiplies bulk mass of each plastic by emission factor and then converts to Tons. Key = type of plastic, value = emissions in Tons of CO2
    emissionStream16 = dict(zip(typesOfPlasticDomestic, [emissionFactors[i]*stream16PlasticCalcMasses[i]*1.10231 for i in typesOfPlasticDomestic]))
    
    
    #############################################################################################
    #Stream 19
    #Sheet = Stream 19 - Contamination
    #Creates dict of additive contaminations. Key = type of additive; value = contamination 
    additiveContaminationConstant = 0.0415 #C11
    
    #Multiplies Fraction of each kind of additive by the total of plastic bulk masses in stream 16 and by the contamination constant
    stream19AdditivesTotals = dict(zip(otherResinAdditives, [additiveFractionsStream16_[i]*sum(stream16PlasticCalcMasses.values())*(additiveContaminationConstant) for i in otherResinAdditives]))
    
    
    #Calculates additives and degradation products in stream 19
    stream19Contaminants = sum(stream16PlasticCalcMasses.values())*0.0065
    stream19DegradationProducts = sum(stream16PlasticCalcMasses.values())*0.0515
   
    #################################################################################################
    #Stream 4 Calculations
    #Sheet = US Mat Flow Analysis 
    #Creates dict of total resin in stream 4, based on stream 6 and bulk plastic manufacturing for . Key = type of plastic, value = mass of resin
    stream4ResinMasses_ = dict(zip(typesOfPlasticDomestic, [totalResinCalculator(typesOfPlasticDomestic[i], plasticsMassDict, listOfStream6Additives_[i]) for i in range(8)]))
    
    #Creates dict of total additives in stream 4, based on stream 6 and bulk plastic manufacturing for . Key = type of additive, value = mass of additive
    stream4AdditiveMasses_ = dict(zip(otherResinAdditives, [totalOfAdditiveType(i, listOfStream6Additives_) for i in otherResinAdditives]))
    
    
    ##############################################################################################
    #Stream 18 Calculations
    #Sheet = US Mat Flow Analysis 
    #Creates dict of additive migration occuring in stream 18 by multiplying the mass of each kind of additive in stream 16 by the additive migration constant (0.02)
    stream18AdditiveMigration = dict(zip(otherResinAdditives, [0.02*totalAdditivesStream16_[i] for i in otherResinAdditives]))
    
    
    ###################################################################################################
    #Stream 21 Calculations
    #Sheet = Stream 21 - Import
    
    #Creates dict with key = type of plastic and value = amount of type of plastic imported based on reported Imported plastics in 
    stream21PlasticMasses = {"PET":repPlasticImportDict["Other"]*0.4, "HDPE": repPlasticImportDict["Ethylene"]/2, "PVC":repPlasticImportDict["Vinyl Chloride"], 
                             "LDPE":repPlasticImportDict["Ethylene"]/2, "PLA":0, "PP":0, "PS":repPlasticImportDict["Styrene"], "Other Resin": repPlasticImportDict["Other"]*0.6} #includes resin and additives lumped together
    
    
    #Creates dict of each kind of additive in each kind of plastic. Key = additive, value = mass of that additive
    stream21PET = additiveMassCalculator(PETadditiveTypes, "PET", stream21PlasticMasses)
    stream21HDPE = additiveMassCalculator(HDPEadditiveTypes, "HDPE", stream21PlasticMasses)
    stream21PVC = additiveMassCalculator(PVCadditiveTypes, "PVC", stream21PlasticMasses)
    stream21PP = additiveMassCalculator(PPadditiveTypes, "PP", stream21PlasticMasses)
    stream21PS = additiveMassCalculator(PSadditiveTypes, "PS", stream21PlasticMasses)   
    stream21LDPE = additiveMassCalculator(LDPEadditiveTypes, "LDPE", stream21PlasticMasses)
    stream21PLA = additiveMassCalculator(PLAadditiveTypes, "PLA", stream21PlasticMasses)
    stream21Other = additiveMassCalculator(otherResinAdditives, "Other Resin", stream21PlasticMasses)
    
    #Creates list of preceding dicts
    listOfStream21Additives_ = [stream21PET, stream21HDPE, stream21PVC, stream21LDPE, stream21PLA, stream21PP, 
                                    stream21PS,  stream21Other]
    
    #Totals each kind of additive in stream 21. Key = type of additive, value = amount of additive
    stream21AdditivesTotals = dict(zip(otherResinAdditives, [totalOfAdditiveType(i, listOfStream21Additives_) for i in otherResinAdditives]))
    
    #Calculates total amount of each kind of resin in stream 21. Key = type of plastic, value = amount of resin
    stream21ResinMasses_ = dict(zip(typesOfPlasticDomestic, [totalResinCalculator(typesOfPlasticDomestic[i], stream21PlasticMasses, listOfStream21Additives_[i]) for i in range(8)]))
    
    #Calculates emissions in this stream by multiplying bulk mass by 0.04 (the emissions factor) then converting into Tons of CO2
    stream21Emissions = dict(zip(typesOfPlasticDomestic, [0.04 * 1.10231* stream21PlasticMasses[i] for i in typesOfPlasticDomestic]))
    
    
    ################################################################################
    #Stream 22 Calculations
    #Sheet = Stream 22- Re-Export
    
    #Creates dict with key = type of plastic and value = amount of type of plastic reexported based on reported reexported plastics in 
    
    stream22PlasticMasses = {"PET":repPlasticsReExportDict["Other"]*0.4, "HDPE": repPlasticsReExportDict["Ethylene"]/2, "PVC":repPlasticsReExportDict["Vinyl Chloride"], 
                             "LDPE":repPlasticsReExportDict["Ethylene"]/2, "PLA":0, "PP":0, "PS":repPlasticsReExportDict["Styrene"], "Other Resin": repPlasticsReExportDict["Other"]*0.6}
    
    
    #Calculates amount of each additive in each type of plastic in stream 22. Key = type of additive, value = mass of that additive in stream 22
    stream22PET = additiveMassCalculator(PETadditiveTypes, "PET", stream22PlasticMasses)
    stream22HDPE = additiveMassCalculator(HDPEadditiveTypes, "HDPE", stream22PlasticMasses)
    stream22PVC = additiveMassCalculator(PVCadditiveTypes, "PVC", stream22PlasticMasses)
    stream22PP = additiveMassCalculator(PPadditiveTypes, "PP", stream22PlasticMasses)
    stream22PS = additiveMassCalculator(PSadditiveTypes, "PS", stream22PlasticMasses)   
    stream22LDPE = additiveMassCalculator(LDPEadditiveTypes, "LDPE", stream22PlasticMasses)
    stream22PLA = additiveMassCalculator(PLAadditiveTypes, "PLA", stream22PlasticMasses)
    stream22Other = additiveMassCalculator(otherResinAdditives, "Other Resin", stream22PlasticMasses)
    
    #Creates list of above dictionaries
    listOfStream22Additives_ = [stream22PET, stream22HDPE, stream22PVC, stream22LDPE, stream22PLA, stream22PP, 
                                    stream22PS,  stream22Other]
    
    
    #Dict: Calculates total mass of each kind of resin in stream 22. Key = type of plastic, value = mass of resin
    stream22ResinMasses_ = dict(zip(typesOfPlasticDomestic, [totalResinCalculator(typesOfPlasticDomestic[i], stream22PlasticMasses, listOfStream22Additives_[i]) for i in range(8)]))
    
    #Dict: Calculates total of each kind of additive in stream 22. Key = type of additive, value = mass of additive
    stream22AdditivesTotals = dict(zip(otherResinAdditives, [totalOfAdditiveType(i, listOfStream22Additives_) for i in otherResinAdditives]))
    
    #Dict: Calculates emissions in stream 22. Emission factor 0.04*bulk mass of plastic in stream 22 and then converted into Tons of CO2
    stream22Emissions = dict(zip(typesOfPlasticDomestic, [0.04 * 1.10231* stream22PlasticMasses[i] for i in typesOfPlasticDomestic]))
    
    
    ###############################################################################################################
    #Stream 23 Calculations
    #Sheet = Stream 23MechRec-Incin
    
    #Dictionary of resin masses in stream 23, based on efficiency of domestic recycling (1-conditions208[4])/2, then multiplied by resin mass. key = type of plastic resin, value = mass of resin
    stream23ResinMasses_ = dict(zip(typesOfPlasticDomestic, [(1-conditions[4])/2*stream16ResinMasses_[i] for i in typesOfPlasticDomestic])) #Resin alone
    
    #Dictionary of additive masses in stream 23, based on efficiency of domestic recycling (1-conditions208[4])/2, then multiplied by additive mass. key = type of plastic additive, value = mass of additive
    stream23AdditiveMasses_ = dict(zip(otherResinAdditives, [totalAdditivesStream16_[i]*(1-conditions[4])/2 for i in otherResinAdditives]))
    stream23PlasticMasses = dict(zip(typesOfPlasticDomestic, [stream23ResinMasses_[i] for i in typesOfPlasticDomestic]))
    stream23PlasticMasses["Other Resin"] = stream23PlasticMasses["Other Resin"] + sum(list(stream23AdditiveMasses_.values()))
   
    #stream 23 Emissions calculations dictionary. Bulk plastic weight in stream * 0.04 * conversion factor to make units Tons of CO2. Key = type of plastic, value = emissions associated with that type
    stream23Emissions = dict(zip(typesOfPlasticDomestic, [0.04*1.10231*stream23PlasticMasses[i] for i in typesOfPlasticDomestic]))
    
    ###########################################################################################################
    
    #Stream28 Calculations unnecessary because they are the same as stream 23- as per sheet US Mat Flow Analysis 
    
    #################################################################################################
    #Stream 31 - to chemical recycling
    stream31ResinMasses = dict(zip(typesOfPlasticDomestic, [chemRecycData[0]*(stream16ResinMasses_[i]+stream21ResinMasses_[i]-stream22ResinMasses_[i]-2*stream23ResinMasses_[i]) for i in typesOfPlasticDomestic]))
    stream31AdditiveMasses = dict(zip(otherResinAdditives, [(totalAdditivesStream16_[i]+stream19AdditivesTotals[i]+stream21AdditivesTotals[i]-stream22AdditivesTotals[i]-stream18AdditiveMigration[i]-2*stream23AdditiveMasses_[i])*chemRecycData[0] for i in otherResinAdditives]))
    stream31Total = sum(stream31ResinMasses.values())+sum(stream31AdditiveMasses.values())

    #Stream 32 - to landfill from chemical recycling
    stream32ResinMasses = dict(zip(typesOfPlasticDomestic, [stream31ResinMasses[i]*chemRecycData[1] for i in typesOfPlasticDomestic]))
    stream32AdditiveMasses = dict(zip(otherResinAdditives, [stream31AdditiveMasses[i]*chemRecycData[1] for i in otherResinAdditives]))
    stream32Total = sum(stream32ResinMasses.values())+sum(stream32AdditiveMasses.values())

    #Stream 33 - to incineration from chemical recycling
    stream33Resinmasses = dict(zip(typesOfPlasticDomestic, [stream31ResinMasses[i]*chemRecycData[2] for i in typesOfPlasticDomestic]))
    stream33AdditiveMasses = dict(zip(otherResinAdditives, [stream31AdditiveMasses[i]*chemRecycData[2] for i in otherResinAdditives]))
    stream33Total = sum(stream33Resinmasses.values())+sum(stream33AdditiveMasses.values())

    #Stream 34 - yield from chemical recycling
    chemRecyc_yield = 1-chemRecycData[1]-chemRecycData[2]
    stream34ResinMasses = dict(zip(typesOfPlasticDomestic, [chemRecyc_yield*stream31ResinMasses[i] for i in typesOfPlasticDomestic])) #products from chemical recycling
    stream34AdditiveMasses = dict(zip(otherResinAdditives, [chemRecyc_yield*stream31AdditiveMasses[i] for i in otherResinAdditives])) #all additives from chemical recycling
    
    
    
    
    
    
    ##########################################################################################################
    #Stream 20 Calculations
    #Sheet = Stream 20 Domestic Recyc
    
    
    #Creates dictionary of stream 20 resin masses. Key = type of plastic resin, value = mass of resin: stream16+stream21-stream22-stream23-stream28 (but stream28=stream23, so stream23 is subtracted twice)
    stream20ResinMasses = dict(zip(typesOfPlasticDomestic, [stream16ResinMasses_[i]+stream21ResinMasses_[i]-stream22ResinMasses_[i]-2*stream23ResinMasses_[i]-stream31ResinMasses[i] for i in typesOfPlasticDomestic]))
    
    #Creates dictionary of stream 20 additive masses. Key = type of additive, value = mass of additive: stream16-stream18+stream19+stream21-stream22-stream23-stream28 (stream28=stream23, so stream23 is substracted twice)
    stream20TotalAdditives = dict(zip(otherResinAdditives, [totalAdditivesStream16_[i]-stream18AdditiveMigration[i]+stream19AdditivesTotals[i]+stream21AdditivesTotals[i]-stream22AdditivesTotals[i]-2*stream23AdditiveMasses_[i] -stream31AdditiveMasses[i] for i in otherResinAdditives]))
    
    #Not given bulk masses, so bulk masses calculated here. Key = type of plastic, value = bulk mass of each type of plastic
    stream20PlasticCalcMasses = dict(zip(typesOfPlasticDomestic, [stream20ResinMasses[i] for i in typesOfPlasticDomestic]))
    stream20PlasticCalcMasses["Other Resin"] = stream20PlasticCalcMasses["Other Resin"]+sum(list(stream20TotalAdditives.values()))
    
    stream20EmissionsFactors = {"PET":-1.13, "HDPE":-0.88, "PVC":0, "LDPE":0, "PLA":0, "PP":0, "PS":0, "Other Resin":-1.03}
    
    stream20Emissions = dict(zip(typesOfPlasticDomestic, [stream20PlasticCalcMasses[i] * stream20EmissionsFactors[i] for i in typesOfPlasticDomestic]))    
    ###################################################################################################################################
    #Stream 1 Calculations
    #Sheet =US Mat Flow Analysis 
    #Dictionary of stream1 resin masses. Key = type of resin, value = mass of resin: stream4- stream 20
    stream1PlasticMasses = dict(zip(typesOfPlasticDomestic, [stream4ResinMasses_[i]- stream20ResinMasses[i] for i in typesOfPlasticDomestic]))
    
    
    ###########################################################################################################
    #Stream 2 Calculations
    #Sheet= US Mat Flow Analysis 
    #Dictionary of additive masses. Key = type of additive, value = mass of additive
    stream2AdditiveMasses = dict(zip(otherResinAdditives, [stream4AdditiveMasses_[i] - stream20TotalAdditives[i] for i in otherResinAdditives]))
    
    
    ##################################################################################
    #Stream 3 Calculations
    #Sheet = Stream 3 - Emissions
    
    #Sum to create mass basis for stream 3
    stream1_stream2_total = sum(stream1PlasticMasses.values())+sum(stream2AdditiveMasses.values())
    
    
    #Creats dict of Fraction of each kind of plastic in stream 3 based on total resin. Key = type of plastic, value = Fraction of total 
    stream3PlasticFractions = dict(zip(typesOfPlasticDomestic, [stream1PlasticMasses[i]/sum(stream1PlasticMasses.values()) for i in typesOfPlasticDomestic]))
    
    #Creates dict of bulk plastic masses of each kind of plastic based on Fraction determined above and mass basis. Key = type of plastic, value = bulk mass
    stream3PlasticMasses = dict(zip(typesOfPlasticDomestic, [stream3PlasticFractions[i]*stream1_stream2_total for i in typesOfPlasticDomestic])) #Lump sum
    
    #Creates dictionary of additives for each type for each kind of plastic based on bulk mass
    stream3PETAdditives = additiveMassCalculator(PETadditiveTypes, "PET", stream3PlasticMasses)
    stream3HDPEAdditives = additiveMassCalculator(HDPEadditiveTypes, "HDPE", stream3PlasticMasses)
    stream3PVCAdditives = additiveMassCalculator(PVCadditiveTypes, "PVC", stream3PlasticMasses)
    stream3LDPEAdditives = additiveMassCalculator(LDPEadditiveTypes, "LDPE", stream3PlasticMasses)
    stream3PLAAdditives = additiveMassCalculator(PLAadditiveTypes, "PLA", stream3PlasticMasses)
    stream3PPAdditives = additiveMassCalculator(PPadditiveTypes, "PP", stream3PlasticMasses)
    stream3PSAdditives = additiveMassCalculator(PSadditiveTypes, "PS", stream3PlasticMasses)
    stream3OtherAdditives = additiveMassCalculator(otherResinAdditives, "Other Resin", stream3PlasticMasses)
    
    #Creates dictionary of emisions factors for each kind of plastic. Key = type of plastic, value = emission factor
    stream3EmissionFactor = {"PET":2.2, "HDPE":1.53, "PVC":1.9, "LDPE":1.76, "PLA":2.09, "PP":1.51, "PS":2.46, "Other Resin":1.92}
    
    #Creates dictionary of emissions for stream 3. Key = type of plastic, value = emissions for that (bulk mass*emission factor*conversion factor)
    stream3Emissions = dict(zip(typesOfPlasticDomestic, [stream3EmissionFactor[i] * stream3PlasticMasses[i]*1.10231 for i in typesOfPlasticDomestic]))
    
    
    #################################################################################################################
    #Stream 5 Calculations
    #Sheet = US Mat Flow Analysis 
    polymerMigrationConstant = 4.71538E-06
    additiveMigrationConstant = 0.019945732
    
    #Creates dict of resin masses in stream 5 by multiplying by polymer migration constant defined above. Key = type of resin, value = mass of migration
    stream5ResinMasses = dict(zip(typesOfPlasticDomestic, [polymerMigrationConstant*stream4ResinMasses_[i] for i in typesOfPlasticDomestic]))
    
    #Creates dict of additive masses in stream 5 by multiplying by additive migration constant defined above. Key = type of resin, value = mass of migration
    stream5AdditiveMasses = dict(zip(otherResinAdditives, [additiveMigrationConstant*stream4AdditiveMasses_[i] for i in otherResinAdditives]))
    
    #####################################################################################################################
    #Stream 27 Calculations
    #Sheet = Stream 27 - Export
    
    #Dictionary defining mass of each kind of plastic for this stream based on Export definitions in US  Sensitivity facts. Key = type of plastic, value = bulk mass of that plastic
    stream27PlasticMasses = {"PET":repPlasticsExportDict["Other"]*0.4, "HDPE":repPlasticsExportDict["Ethylene"]/2, 
                                 "PVC":repPlasticsExportDict["Vinyl Chloride"], "LDPE":repPlasticsExportDict["Ethylene"]/2,
                                 "PLA":0, "PP": 0, "PS":repPlasticsExportDict["Styrene"], "Other Resin":repPlasticsExportDict["Other"]*0.6}
    
    #Dictionary defining mass of each kind of additive in each kind of plastic. Key = type of additive, value = mass of that additive
    stream27PETAdditives = additiveMassCalculator(PETadditiveTypes, "PET", stream27PlasticMasses)
    stream27HDPEAdditives = additiveMassCalculator(HDPEadditiveTypes, "HDPE", stream27PlasticMasses)
    stream27PVCAdditives = additiveMassCalculator(PVCadditiveTypes, "PVC", stream27PlasticMasses)
    stream27LDPEAdditives = additiveMassCalculator(LDPEadditiveTypes, "LDPE", stream27PlasticMasses)
    stream27PLAAdditives = additiveMassCalculator(PLAadditiveTypes, "PLA", stream27PlasticMasses)
    stream27PPAdditives = additiveMassCalculator(PPadditiveTypes, "PP", stream27PlasticMasses)
    stream27PSAdditives = additiveMassCalculator(PETadditiveTypes, "PS", stream27PlasticMasses)
    stream27OtherAdditives = additiveMassCalculator(otherResinAdditives, "Other Resin", stream27PlasticMasses)
    
    #List of above dictionaries
    listOfstream27Additives = [stream27PETAdditives, stream27HDPEAdditives, stream27PVCAdditives, stream27LDPEAdditives, stream27PLAAdditives,
                               stream27PPAdditives, stream27PSAdditives, stream27OtherAdditives]
    
    #Dictionary of resin masses in this stream. Key = type of resin, value = mass of resin
    stream27ResinMasses = dict(zip(typesOfPlasticDomestic, [totalResinCalculator(typesOfPlasticDomestic[i], stream27PlasticMasses, listOfstream27Additives[i]) for i in range(8)]))
    
    
    #Dictionary of additive masses in this stream. Key = type of additive, value = mass of additive
    stream27TotalAdditivesMasses = dict(zip(otherResinAdditives, [totalOfAdditiveType(i, listOfstream27Additives) for i in otherResinAdditives]))
    
    #Dictionary of emissions in this stream, key = type of plastic, value = emissions associated with that plastic (bulk mass *0.04 * conversion factor to make units Tons CO2))
    stream27Emissions = dict(zip(typesOfPlasticDomestic, [0.04*1.10231*stream27PlasticMasses[i] for i in typesOfPlasticDomestic]))
    
    ######################################################################################
    #Stream 8 Calculations
    #Note: stream8 plastic resins and additives are the same as stream 27 as per US Mat FLow Analysis 
    #Creates dictionary of types of MSW waste (without plastic), takes total MSW and multiplies that by their respective proportions. Key = type of MSW, value = mass of that MSW
    stream8MSWMasses_ = dict(zip(typesOfWastesForCalculations, [mswCompProp[i]*conditions[0] for i in range(len(typesOfWastesForCalculations))]))
    
    
    ####################################################################################################
    #Stream 9 Calculations
    #Sheet = Stream 9 - Litter
    #Determines total mass of stream 4, then multiplies it by littering constant to determine mass of littered plastic
    stream4TotalMass_ = sum(stream4AdditiveMasses_.values())+sum(stream4ResinMasses_.values())
    stream9TotalMass_ = assumedValues["Plastic waste lost to littering"]*stream4TotalMass_
    
    #Creates dictionary of bulk plastic masses based on proportions of plastic generated and mass basis for stream. Key = type of plastic, value = bulk mass littered 
    stream9PlasticMasses_ = dict(zip(typesOfPlasticDomestic, [stream9TotalMass_*plasticFractionsRecycled[i] for i in typesOfPlasticDomestic]))
    
    
    #Creates dictionary of additives in littered plastic based on bulk masses determined above. Key = type of additive, value = mass of additive
    stream9PETAdditives = additiveMassCalculator(PETadditiveTypes, "PET", stream9PlasticMasses_)
    stream9HDPEAdditives = additiveMassCalculator(HDPEadditiveTypes, "HDPE", stream9PlasticMasses_)
    stream9PVCAdditives = additiveMassCalculator(PVCadditiveTypes, "PVC", stream9PlasticMasses_)
    stream9LDPEAdditives = additiveMassCalculator(LDPEadditiveTypes, "LDPE", stream9PlasticMasses_)
    stream9PLAAdditives = additiveMassCalculator(PLAadditiveTypes, "PLA", stream9PlasticMasses_)
    stream9PPAdditives = additiveMassCalculator(PPadditiveTypes, "PP", stream9PlasticMasses_)
    stream9PSAdditives = additiveMassCalculator(PSadditiveTypes, "PS", stream9PlasticMasses_)
    stream9OtherAdditives = additiveMassCalculator(otherResinAdditives, "Other Resin", stream9PlasticMasses_)
    
    #Creates list of above dicts
    listOfstream9Additives = [stream9PETAdditives, stream9HDPEAdditives, stream9PVCAdditives, stream9LDPEAdditives, stream9PLAAdditives,
                               stream9PPAdditives, stream9PSAdditives, stream9OtherAdditives]
    
    #Creates dictionary of total of each kind of additive in this stream. Key = type of additive, value = total mass of additive in this stream
    stream9TotalAdditives = dict(zip(otherResinAdditives, [totalOfAdditiveType(i, listOfstream9Additives) for i in otherResinAdditives]))
    
    #Creates dict of total resin in this stream. Key= type of resin, value = mass of resin in this stream
    stream9ResinTotals = dict(zip(typesOfPlasticDomestic, [totalResinCalculator(typesOfPlasticDomestic[i], stream9PlasticMasses_, listOfstream9Additives[i]) for i in range(8)]))
    
    ###############################################################################################################
    #Stream 6 Pt. 2
    
    #Dict of resin values in this stream
    stream6ResinTotals = dict(zip(typesOfPlasticDomestic, [stream4ResinMasses_[i] - stream5ResinMasses[i] for i in typesOfPlasticDomestic]))
    
    #Dict of additive values in this stream
    stream6AdditiveTotals = dict(zip(otherResinAdditives, [stream4AdditiveMasses_[i] - stream5AdditiveMasses[i] for i in otherResinAdditives]))
    
    ########################################################################################
    #Stream 10 Calculations
    #Sheet = US Mat Flow Analysis 
    
    #Creates dict of resin totals in this stream. Key = type of resin, value = mass of resin (stream6-stream9+stream27)
    stream10ResinTotals = dict(zip(typesOfPlasticDomestic, [stream6ResinTotals[i] - stream9ResinTotals[i] + stream27ResinMasses[i] for i in typesOfPlasticDomestic]))
    
    
    #Creates dict of additive totals in this stream. Key = type of additive, value = mass of additive (stream6-stream9+stream27)
    stream10AdditiveTotals = dict(zip(otherResinAdditives, [stream6AdditiveTotals[i] - stream9TotalAdditives[i]+stream27TotalAdditivesMasses[i] for i in otherResinAdditives]))
    #Note: stream 10 MSW data (rows 27:35) is the same as stream 8 so will be omitted for concision purposes
    totalStream10Waste = sum(stream10AdditiveTotals.values())+sum(stream10ResinTotals.values())+sum(stream8MSWMasses_.values()) #Cell K39
    
    
    ############################################################################################################
    #Stream 7 Calculations
    #Sheet = US Mat Flow Analysis 
    stream7EmissionFactor = 230
    
    #Calculates stream 7 emissions based on total stream 10 mass, emission factor, and conversion factor to Tons of CO2
    stream7TotalEmissions = totalStream10Waste*stream7EmissionFactor*0.00110231
    
    
    ############################################################################
    #Stream 11 Calculations
    #Sheet = US Mat Flow Analysis 
    
    #Creates dictionary of key = types of MSW (except plastic); value = mass of MSW incinerated (total mass incinerated*proportion incinerated)
    stream11MSWValues = dict(zip(typesOfWastesForCalculations, [mswIncin[0]*mswIncin[i] for i in range(1,len(typesOfWastesForCalculations)+1)]))
    
    
    ##############################################################################
    #Stream 12 Calculations
    #Sheet = US Mat FLow Analysis 
    
    #Creates dict of key = types of MSW (except plastic); value = mass of MSW landfilled (total mass landfilled*proportion landfilled)
    stream12MSWValues = dict(zip(typesOfWastesForCalculations, [mswLand[0]*mswLand[i] for i in range(1, len(typesOfWastesForCalculations)+1)]))
    
    
    ############################################################################
    #Stream 13 Calculations
    #Sheet = Stream 13-Plastic Compost
    
    #Creates dict of key = type of plastic, value = mass*0.01Fraction*Fraction of each kind of plastic. 
    stream13PlasticMasses = dict(zip(typesOfPlasticDomestic, [mswCompost[0]*100*0.0001*plasticFractionsRecycled[i] for i in typesOfPlasticDomestic]))
    
    #Creates dict of key = type of additive, value = mass of additive in this stream
    stream13PETAdditives = additiveMassCalculator(PETadditiveTypes, "PET", stream13PlasticMasses)
    stream13HDPEAdditives = additiveMassCalculator(HDPEadditiveTypes, "HDPE", stream13PlasticMasses)
    stream13PVCAdditives = additiveMassCalculator(PVCadditiveTypes, "PVC", stream13PlasticMasses)
    stream13LDPEAdditives = additiveMassCalculator(LDPEadditiveTypes, "LDPE", stream13PlasticMasses)
    stream13PLAAdditives = additiveMassCalculator(PLAadditiveTypes, "PLA", stream13PlasticMasses)
    stream13PPAdditives = additiveMassCalculator(PPadditiveTypes, "PP", stream13PlasticMasses)
    stream13PSAdditives = additiveMassCalculator(PSadditiveTypes, "PS", stream13PlasticMasses)
    stream13OtherAdditives = additiveMassCalculator(otherResinAdditives, "Other Resin", stream13PlasticMasses)
    
    #List of above dicts
    listOfStream13Additives = [stream13PETAdditives, stream13HDPEAdditives, stream13PVCAdditives, stream13LDPEAdditives, stream13PLAAdditives,
                                   stream13PPAdditives, stream13PSAdditives, stream13OtherAdditives]
    
    #Totals additives and resins for this stream
    stream13AdditiveTotals = dict(zip(otherResinAdditives, [totalOfAdditiveType(i, listOfStream13Additives) for i in otherResinAdditives]))
    stream13ResinMasses = dict(zip(typesOfPlasticDomestic, [totalResinCalculator(typesOfPlasticDomestic[i], stream13PlasticMasses, listOfStream13Additives[i]) for i in range(8)]))
    
    #MSW for this stream
    stream13MSW = dict(zip(typesOfWastesForCalculations, [mswCompost[i+1]*mswCompost[0] for i in range(10)]))
    #######################################################################################################################
    #Stream 14 Calculations
    #Sheet = US Mat Flow Analysis 
    #Creates dict of key = types of MSW except plastic, value = mass recycled(total mass recycled*proportion of each kind of plastic recycled)
    stream14MSWValues = dict(zip(typesOfWastesForCalculations, [mswRecyc[0]*mswRecyc[i] for i in range(1, len(typesOfWastesForCalculations)+1)]))
    
    ######################################################################
    #Stream 15 Input
    #Sheet = US Mat Flow Analysis 
    
    wasteFacilityEmissions = conditions[9]*1.10231 #CellP43
    
    
    #########################################################################
    #Stream 24 Calculations
    #Sheet = Stream 24 - Incineration
    
    
    
    
    #Calculates mass basis, total plastic*Fraction incinerated
    stream24MassBasis = conditions[1]*conditions[7]
    
    #Creates dict of bulk masses of each kind of plastic based on mass basis and proportions of each plastic incinerated. Key = type of plastic, value = bulk mass
    stream24PlasticMasses = dict(zip(typesOfPlasticDomestic, [stream24MassBasis*plasticIncinFractionsDict[i] for i in typesOfPlasticDomestic]))
    
    #Creates dict of additives based on bulk masses. Key= type of additive, value = mass of additive
    stream24PETAdditives = additiveMassCalculator(PETadditiveTypes, "PET", stream24PlasticMasses)
    stream24HDPEAdditives = additiveMassCalculator(HDPEadditiveTypes, "HDPE", stream24PlasticMasses)
    stream24PVCAdditives = additiveMassCalculator(PVCadditiveTypes, "PVC", stream24PlasticMasses)
    stream24LDPEAdditives = additiveMassCalculator(LDPEadditiveTypes, "LDPE", stream24PlasticMasses)
    stream24PLAAdditives = additiveMassCalculator(PLAadditiveTypes, "PLA", stream24PlasticMasses)
    stream24PPAdditives = additiveMassCalculator(PPadditiveTypes, "PP", stream24PlasticMasses)
    stream24PSAdditives = additiveMassCalculator(PSadditiveTypes, "PS", stream24PlasticMasses)
    stream24OtherAdditives = additiveMassCalculator(otherResinAdditives, "Other Resin", stream24PlasticMasses)
    
    #List of above dicts
    listOfStream24Additives = [stream24PETAdditives, stream24HDPEAdditives, stream24PVCAdditives, stream24LDPEAdditives, stream24PLAAdditives,
                                   stream24PPAdditives, stream24PSAdditives, stream24OtherAdditives]
    
    #Creates dict of total additives and resins in the straem
    stream24AdditiveTotals = dict(zip(otherResinAdditives, [totalOfAdditiveType(i, listOfStream24Additives) for i in otherResinAdditives]))
    stream24ResinMasses = dict(zip(typesOfPlasticDomestic, [totalResinCalculator(typesOfPlasticDomestic[i], stream24PlasticMasses, listOfStream24Additives[i]) for i in range(8)]))
    
    
    #Creates dict of emissions factors, then creates dict of emissions associated with each type of plastic's bulk masses
    stream24EmissionsFactors = {"PET": 1.24, "HDPE":1.27, "PVC":0.67, "LDPE": 1.27, "PLA":1.25, "PP":1.27, "PS":1.64, "Other Resin":2.33}
    stream24Emissions = dict(zip(typesOfPlasticDomestic, [stream24EmissionsFactors[i]*stream24PlasticMasses[i] *1.10231 for i in typesOfPlasticDomestic]))
    
    ##########################################################################################
    #Stream 25 Calculations
    #Sheet = US Mat Flow Analysis 
    #Creates dict of amount of resin, additive, and non-plastic MSW not incincerated (value = type of resin/additive/MSW, value = mass not incinerated)
    stream25ResinMasses = dict(zip(typesOfPlasticDomestic, [(stream24ResinMasses[i]+stream23ResinMasses_[i])*(1-assumedValues["Incineration Efficiency Fraction"]) for i in typesOfPlasticDomestic]))
    stream25AdditiveMasses = dict(zip(otherResinAdditives, [(stream24AdditiveTotals[i]+stream23AdditiveMasses_[i])*(1-assumedValues["Incineration Efficiency Fraction"]) for i in otherResinAdditives]))
    
    stream25MSWValues = dict(zip(typesOfWastesForCalculations, [(stream11MSWValues[i])*(1-assumedValues["Incineration Efficiency Fraction"]) for i in typesOfWastesForCalculations]))
    
    stream25AshMass = (sum(stream24AdditiveTotals.values())+sum(stream24ResinMasses.values()))/averageDensityCalculation * 0.01 * 2.05*0.0000011023
    #############################################################################################
    #Stream 26 Calculations
    #Sheet = Stream 26 Landfilled Plastic
    
    
    #Creates dict of total plastic landfilled
    stream26MassBasis = conditions[1]*conditions[8]
    
    #Creates dict of key = type of plastic, value = bulk mass of type of plastic (mass basis for stream *proportion for each kind of plastic)
    stream26PlasticMasses = dict(zip(typesOfPlasticDomestic, [stream26MassBasis*plasticLandFractions[i] for i in typesOfPlasticDomestic]))
    
    
    #Creates dict of additives for each kind of plastic. Key = type of additive, value = mass
    stream26PETAdditives = additiveMassCalculator(PETadditiveTypes, "PET", stream26PlasticMasses)
    stream26HDPEAdditives = additiveMassCalculator(HDPEadditiveTypes, "HDPE", stream26PlasticMasses)
    stream26PVCAdditives = additiveMassCalculator(PVCadditiveTypes, "PVC", stream26PlasticMasses)
    stream26LDPEAdditives = additiveMassCalculator(LDPEadditiveTypes, "LDPE", stream26PlasticMasses)
    stream26PLAAdditives = additiveMassCalculator(PLAadditiveTypes, "PLA", stream26PlasticMasses)
    stream26PPAdditives = additiveMassCalculator(PPadditiveTypes, "PP", stream26PlasticMasses)
    stream26PSAdditives = additiveMassCalculator(PSadditiveTypes, "PS", stream26PlasticMasses)
    stream26OtherAdditives = additiveMassCalculator(otherResinAdditives, "Other Resin", stream26PlasticMasses)
    
    #List of above created dicts
    listOfStream26Additives = [stream26PETAdditives, stream26HDPEAdditives, stream26PVCAdditives, stream26LDPEAdditives, stream26PLAAdditives,
                                   stream26PPAdditives, stream26PSAdditives, stream26OtherAdditives]
    
    #Creates dict of Sums of additives and resins in this stream
    stream26AdditiveTotals = dict(zip(otherResinAdditives, [totalOfAdditiveType(i, listOfStream26Additives)+stream32AdditiveMasses[i] for i in otherResinAdditives]))
    stream26ResinMasses = dict(zip(typesOfPlasticDomestic, [totalResinCalculator(typesOfPlasticDomestic[i], stream26PlasticMasses, listOfStream26Additives[i]) + stream32ResinMasses[typesOfPlasticDomestic[i]] for i in range(8)]))
    
    #Creates dict of emissions in this stream based on bulk masses in this stream
    stream26Emissions = dict(zip(typesOfPlasticDomestic, [0.04*stream26PlasticMasses[i] *1.10231 for i in typesOfPlasticDomestic]))
    
    
    #########################################################################
    #Stream 29 Calculations
    #Sheet = Stream 29 - Plastic Release
    #Creates dict of resins and additives in this stream based on leak constant. key = type of resin or additive, value = mass
    stream29ResinMasses = dict(zip(typesOfPlasticDomestic, [stream4ResinMasses_[i] * assumedValues["Plastic waste leak after landfill"] for i in typesOfPlasticDomestic]))
    stream29AdditiveMasses = dict(zip(otherResinAdditives, [stream4AdditiveMasses_[i]*assumedValues["Plastic waste leak after landfill"]+(stream26AdditiveTotals[i]+stream23AdditiveMasses_[i])*0.00001 for i in otherResinAdditives]))
    
    #Creates dict of key = type of plastic, value = emissions associated with release (mass*0.04 for emission factor *conversion factor)
    stream29Emissions = dict(zip(typesOfPlasticDomestic, [stream29ResinMasses[i]*0.04*1.10231 for i in typesOfPlasticDomestic]))
    
    ##########################################################################
    #Stream 30 Calculations
    #Sheet = US Mat Flow Analysis 
    #Sums emissions in stream 26
    stream26totalEmissions = sum(stream26Emissions.values())
    
    #Inputs landfill emissions in 
    FractionOfMSWEmissionLandfill = 0.15
    combinedLandfillEmissions = conditions[10]*FractionOfMSWEmissionLandfill
    
    #Sums stream 30 emissions
    stream30Emissions = stream26totalEmissions+combinedLandfillEmissions
    
    ###########################################################################
    #Total Incineration Calculations
    #Sheet = US Mat Flow Analysis 
    
    #Creates dict of total incineration for each kind of plastic and additive (stream 23 +stream 24).
    totalIncinerationPlasticResin = dict(zip(typesOfPlasticDomestic, [stream23ResinMasses_[i] + stream24ResinMasses[i] + stream33Resinmasses[i]  for i in typesOfPlasticDomestic]))
    totalIncinerationAdditives = dict(zip(otherResinAdditives, [stream23AdditiveMasses_[i]+ stream24AdditiveTotals[i] + stream33AdditiveMasses[i] for i in otherResinAdditives]))
    
    #Creates dict of total incineration for each kind of MSW (stream 11).
    totalIncinerationMSW = stream11MSWValues
    
    #Total Landfill Calculations: sums stream 9, 23, 26 and subtracts stream 29 resins, additive, MSW masses
    totalLandfillPlasticResin = dict(zip(typesOfPlasticDomestic, [stream9ResinTotals[i]+stream23ResinMasses_[i]+stream26ResinMasses[i]-stream29ResinMasses[i] +stream32ResinMasses[i] for i in typesOfPlasticDomestic]))
    totalLandfillAdditives = dict(zip(otherResinAdditives, [stream9TotalAdditives[i]+stream23AdditiveMasses_[i]+stream26AdditiveTotals[i]-stream29AdditiveMasses[i] +stream32AdditiveMasses[i] for i in otherResinAdditives]))
    totalLandfilledOtherMSW = stream12MSWValues
    

    #Begin accumulation calculations
    #Note: all lists will be denoted the same as above, but will include a marker in front to indicate the material loop. mL1= material loop 1, mL2, mL3, mL4
    #Note: all non-plastic MSW values are the same throughout
    
    
    additive_contam_loops = []
    #Material Loop 1 
    
    #Streams 1 and 2
    mL1stream1NonRecycPlasticMasses = dict(zip(typesOfPlasticDomestic, [stream1PlasticMasses[i]-stream20ResinMasses[i]for i in typesOfPlasticDomestic]))
    mL1stream2NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [stream2AdditiveMasses[i]-stream20TotalAdditives[i] for i in otherResinAdditives]))

    mL1stream1RecycPlasticMasses = dict(zip(recycledTypesOfPlasticDomestic, stream20ResinMasses.values()))
    mL1stream1RecycAdditiveMasses = dict(zip(recycledAdditivesList, stream20TotalAdditives.values()))
    
   #Stream 4 (note: no stream 3)
    mL1stream4NonRecycPlasticMasses = mL1stream1NonRecycPlasticMasses
    mL1stream4NonRecycAdditiveMasses = mL1stream2NonRecycAdditiveMasses
    mL1stream4RecycPlasticMasses = mL1stream1RecycPlasticMasses
    mL1stream4RecycAdditiveMasses = mL1stream1RecycAdditiveMasses
    
    #Stream 5
    mL1stream5NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [polymerMigrationConstant*mL1stream4NonRecycPlasticMasses[i] for i in typesOfPlasticDomestic]))
    mL1stream5NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [additiveMigrationConstant*mL1stream4NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL1stream5RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [polymerMigrationConstant*mL1stream4RecycPlasticMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL1stream5RecycAdditiveMasses = dict(zip(recycledAdditivesList, [additiveMigrationConstant*mL1stream4RecycAdditiveMasses[i] for i in recycledAdditivesList]))


    #Stream 6
    mL1stream6NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [mL1stream4NonRecycPlasticMasses[i] - mL1stream5NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL1stream6NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL1stream4NonRecycAdditiveMasses[i] -mL1stream5NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL1stream6RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL1stream4RecycPlasticMasses[i] -mL1stream5RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL1stream6RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL1stream4RecycAdditiveMasses[i] - mL1stream5RecycAdditiveMasses[i] for i in recycledAdditivesList]))

    #Stream 8 (note: no stream 7 and stream 8 is the same in all loops)
    mL1stream8MSW = stream8MSWMasses_
    mL1stream8ResinMasses = stream27ResinMasses 
    mL1stream8AdditiveMasses = stream27TotalAdditivesMasses

    #Stream 9
    mL1stream9NonRecycPlasticMasses = dict(zip(typesOfPlasticDomestic, [assumedValues["Plastic waste lost to littering"]*mL1stream4NonRecycPlasticMasses[i] for i in typesOfPlasticDomestic]))
    mL1stream9NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [assumedValues["Plastic waste lost to littering"]*mL1stream4NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL1stream9RecycPlasticMasses = dict(zip(recycledTypesOfPlasticDomestic, [assumedValues["Plastic waste lost to littering"]*mL1stream4RecycPlasticMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL1stream9RecycAdditiveMasses = dict(zip(recycledAdditivesList, [assumedValues["Plastic waste lost to littering"]*mL1stream4RecycAdditiveMasses[i] for i in recycledAdditivesList]))

    #Stream 10
    
    mL1stream10NonRecycPlasticMasses = dict(zip(typesOfPlasticDomestic, [mL1stream8ResinMasses[i] + mL1stream6NonRecycResinMasses[i]-mL1stream9NonRecycPlasticMasses[i] for i in typesOfPlasticDomestic]))
    mL1stream10NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL1stream8AdditiveMasses[i]+mL1stream6NonRecycAdditiveMasses[i]-mL1stream9NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL1stream10RecycPlasticMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL1stream6RecycResinMasses[i]-mL1stream9RecycPlasticMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL1stream10RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL1stream6RecycAdditiveMasses[i]-mL1stream9RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    mL1stream10MSWMasses = stream8MSWMasses_
    
    #Streams 11, 12, 13, 14, and 15 Note: Streams 11, 12, 13, and 14 are the same in every loop. Stream 15 is empty
    mL1stream11 = stream11MSWValues
    mL1stream12 = stream12MSWValues
    mL1stream13ResinMasses = stream13ResinMasses
    mL1stream13Additivemasses = stream13AdditiveTotals
    mL1stream13MSW = stream13MSW
    mL1stream14 = stream14MSWValues
    
    
    #Stream 16
    mL1stream16RecycPlasticMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL1stream10RecycPlasticMasses[i]*reRecyclingRate for i in recycledTypesOfPlasticDomestic]))
    mL1stream16RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL1stream10RecycAdditiveMasses[i]*reRecyclingRate for i in recycledAdditivesList]))
    
    mL1stream16NonRecycMassBasis = (sum(mL1stream10NonRecycPlasticMasses.values())+sum(mL1stream10NonRecycAdditiveMasses.values())+sum(mL1stream10RecycAdditiveMasses.values())+sum(mL1stream10RecycPlasticMasses.values()))*conditions[3]-sum(mL1stream16RecycAdditiveMasses.values())-sum(mL1stream16RecycPlasticMasses.values())

    mL1stream16NonRecycPlasticBulkMasses = dict(zip(typesOfPlasticDomestic, [mL1stream16NonRecycMassBasis*scaledRecFractions[i] for i in typesOfPlasticDomestic]))

    
    mL1stream16PETNonRecyc = additiveMassCalculator(PETadditiveTypes, "PET", mL1stream16NonRecycPlasticBulkMasses)
    mL1stream16HDPENonRecyc = additiveMassCalculator(HDPEadditiveTypes, "HDPE", mL1stream16NonRecycPlasticBulkMasses)
    mL1stream16PVCNonRecyc = additiveMassCalculator(PVCadditiveTypes, "PVC", mL1stream16NonRecycPlasticBulkMasses)
    mL1stream16PPNonRecyc = additiveMassCalculator(PPadditiveTypes, "PP", mL1stream16NonRecycPlasticBulkMasses)
    mL1stream16PSNonRecyc = additiveMassCalculator(PSadditiveTypes, "PS", mL1stream16NonRecycPlasticBulkMasses)   
    mL1stream16LDPENonRecyc = additiveMassCalculator(LDPEadditiveTypes, "LDPE", mL1stream16NonRecycPlasticBulkMasses)
    mL1stream16PLANonRecyc = additiveMassCalculator(PLAadditiveTypes, "PLA", mL1stream16NonRecycPlasticBulkMasses)
    mL1stream16OtherNonRecyc = additiveMassCalculator(otherResinAdditives, "Other Resin", mL1stream16NonRecycPlasticBulkMasses)

    
    #Creates list of additive dicts in stream 16 
    mL1listOfstream16NonRecycAdditives = [mL1stream16PETNonRecyc, mL1stream16HDPENonRecyc, mL1stream16PVCNonRecyc, mL1stream16LDPENonRecyc, mL1stream16PLANonRecyc, 
                                       mL1stream16PPNonRecyc, mL1stream16PSNonRecyc,  mL1stream16OtherNonRecyc]
    
    
    #Calculates total amount of each kind of additive in stream 16; key = type of additive, value = total mass of additive
    mL1Stream16totalNonRecycAdditives = dict(zip(otherResinAdditives, [totalOfAdditiveType(i, mL1listOfstream16NonRecycAdditives) for i in otherResinAdditives])) #Dict of additive in stream 16
    
    #Calculates total amount of each resin in stream 16; key = type of plastic, value = mass of resin
    mL1stream16NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [totalResinCalculator(typesOfPlasticDomestic[i], mL1stream16NonRecycPlasticBulkMasses, mL1listOfstream16NonRecycAdditives[i]) for i in range(8)]))
    
    #stream 18
    mL1stream18NonRecycAdditives = dict(zip(otherResinAdditives, [mL1Stream16totalNonRecycAdditives[i]*assumedValues["Additive migration Fraction"] for i in otherResinAdditives]))
    mL1stream18RecycAdditives = dict(zip(recycledAdditivesList, [mL1stream16RecycAdditiveMasses[i]*assumedValues["Additive migration Fraction"] for i in recycledAdditivesList]))
    
    #stream 19 stays the same throughout the loops
    mL1stream19NonRecycAdditives = stream19AdditivesTotals
    
    #stream 21 stays the same throughout the loops
    mL1stream21NonRecycResinMasses = stream21ResinMasses_
    mL1stream21NonRecycAdditiveMasses = stream21AdditivesTotals
    
    #stream 22 stays the same throughout the loops
    mL1stream22NonRecycResinMasses = stream22ResinMasses_
    mL1stream22NonRecycAdditiveMasses = stream22AdditivesTotals
    
    #stream 23
    mL1stream23NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [(1-conditions[4])/2*mL1stream16NonRecycResinMasses[i] for i in typesOfPlasticDomestic])) 
    mL1stream23NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [(1-conditions[4])/2*mL1Stream16totalNonRecycAdditives[i] for i in otherResinAdditives])) 
    mL1stream23RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [(1-conditions[4])/2*mL1stream16RecycPlasticMasses[i] for i in recycledTypesOfPlasticDomestic])) 
    mL1stream23RecycAdditiveMasses = dict(zip(recycledAdditivesList, [(1-conditions[4])/2*mL1stream16RecycAdditiveMasses[i] for i in recycledAdditivesList])) 

    #stream 28 is the same as stream 23
    mL1stream28NonRecycResinMasses = mL1stream23NonRecycResinMasses
    mL1stream28NonRecycAdditiveMasses = mL1stream23NonRecycAdditiveMasses
    mL1stream28RecycResinMasses = mL1stream23RecycResinMasses
    mL1stream28RecycAdditiveMasses = mL1stream23RecycAdditiveMasses
    
    #stream 20
    mL1stream20NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [mL1stream16NonRecycResinMasses[i]+mL1stream21NonRecycResinMasses[i]-mL1stream22NonRecycResinMasses[i] - mL1stream23NonRecycResinMasses[i]-mL1stream28NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL1stream20NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL1Stream16totalNonRecycAdditives[i] - mL1stream18NonRecycAdditives[i]+mL1stream19NonRecycAdditives[i]+mL1stream21NonRecycAdditiveMasses[i] - mL1stream22NonRecycAdditiveMasses[i] -mL1stream23NonRecycAdditiveMasses[i]-mL1stream28NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL1stream20RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL1stream16RecycPlasticMasses[i]-mL1stream23RecycResinMasses[i]-mL1stream28RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL1stream20RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL1stream16RecycAdditiveMasses[i]-mL1stream18RecycAdditives[i]-mL1stream23RecycAdditiveMasses[i]-mL1stream28RecycAdditiveMasses[i] for i in recycledAdditivesList]))


    #stream 24
    mL1stream24NonRecyResinMasses = stream24ResinMasses
    mL1stream24NonRecycAdditiveMasses = stream24AdditiveTotals
    
    mL1stream24RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [(mL1stream10RecycPlasticMasses[i]-mL1stream16RecycPlasticMasses[i])*(conditions[7]/conditions[8]) for i in recycledTypesOfPlasticDomestic]))
    mL1stream24RecycAdditiveMasses = dict(zip(recycledAdditivesList, [(mL1stream10RecycAdditiveMasses[i]-mL1stream16RecycAdditiveMasses[i])*((conditions[7]/conditions[8])) for i in recycledAdditivesList]))
    
    #stream 25
    mL1stream25NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL1stream23NonRecycResinMasses[i]+mL1stream24NonRecyResinMasses[i]) for i in typesOfPlasticDomestic]))
    mL1stream25NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL1stream23NonRecycAdditiveMasses[i]+mL1stream24NonRecycAdditiveMasses[i]) for i in otherResinAdditives]))
    
    mL1stream25RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL1stream23RecycResinMasses[i]+mL1stream24RecycResinMasses[i]) for i in recycledTypesOfPlasticDomestic]))
    mL1stream25RecycAdditiveMasses = dict(zip(recycledAdditivesList, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL1stream23RecycAdditiveMasses[i]+mL1stream24RecycAdditiveMasses[i]) for i in recycledAdditivesList]))
    
    #stream 26
    mL1stream26NonRecycResinMasses = stream26ResinMasses
    mL1stream26NonRecycAdditiveMasses = stream26AdditiveTotals
    
    mL1stream26RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL1stream10RecycPlasticMasses[i]-mL1stream16RecycPlasticMasses[i]-mL1stream24RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL1stream26RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL1stream10RecycAdditiveMasses[i]-mL1stream16RecycAdditiveMasses[i]-mL1stream24RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    #stream 27 
    mL1stream27NonRecycResinMasses = stream27ResinMasses
    mL1stream27NonRecycAdditiveMasses = stream27TotalAdditivesMasses
    
    #stream 29
    mL1stream29NonRecycResinmasses = dict(zip(typesOfPlasticDomestic, [mL1stream4NonRecycPlasticMasses[i]*assumedValues["Plastic waste leak after landfill"] for i in typesOfPlasticDomestic]))
    mL1stream29NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL1stream4NonRecycAdditiveMasses[i]*assumedValues["Plastic waste leak after landfill"]+(mL1stream26NonRecycAdditiveMasses[i]+mL1stream28NonRecycAdditiveMasses[i])*0.00001 for i in otherResinAdditives]))
    mL1stream29RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL1stream4RecycPlasticMasses[i]*assumedValues["Plastic waste leak after landfill"] + (mL1stream26RecycResinMasses[i]+mL1stream28RecycResinMasses[i])*0.00001 for i in recycledTypesOfPlasticDomestic]))
    mL1stream29RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL1stream4RecycAdditiveMasses[i]*assumedValues["Plastic waste leak after landfill"]+(mL1stream26RecycAdditiveMasses[i]+mL1stream28RecycAdditiveMasses[i])*0.00001 for i in recycledAdditivesList]))
    
    #stream 30 is all 0's
    
    #Creates dict of total incineration for each kind of plastic and additive (stream 23 +stream 24).
    mL1totalIncinerationNonRecycResin = dict(zip(typesOfPlasticDomestic, [mL1stream23NonRecycResinMasses[i] + mL1stream24NonRecyResinMasses[i] for i in typesOfPlasticDomestic]))
    mL1totalIncinerationNonRecycAdditives = dict(zip(otherResinAdditives, [mL1stream24NonRecycAdditiveMasses[i] + mL1stream23NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL1totalIncinerationRecycResin = dict(zip(recycledTypesOfPlasticDomestic, [mL1stream23RecycResinMasses[i]+mL1stream24RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL1totalIncinerationRecycAdditives = dict(zip(recycledAdditivesList, [mL1stream23RecycAdditiveMasses[i] + mL1stream24RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    #Total Landfill Calculations: sums stream 9, 23, 26 and subtracts stream 29 resins, additive, MSW masses
    mL1totalLandfillNonRecycPlasticResin = dict(zip(typesOfPlasticDomestic, [mL1stream9NonRecycPlasticMasses[i] + mL1stream23NonRecycResinMasses[i] + mL1stream26NonRecycResinMasses[i] - mL1stream29NonRecycResinmasses[i] for i in typesOfPlasticDomestic]))
    mL1totalLandfillNonRecycAdditives = dict(zip(otherResinAdditives, [mL1stream9NonRecycAdditiveMasses[i] + mL1stream23NonRecycAdditiveMasses[i] + mL1stream26NonRecycAdditiveMasses[i] - mL1stream29NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL1totalLandfillRecycResin = dict(zip(recycledTypesOfPlasticDomestic, [mL1stream9RecycPlasticMasses[i] + mL1stream23RecycResinMasses[i] + mL1stream26RecycResinMasses[i] - mL1stream29RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL1totalLandfillRecycAdditives = dict(zip(recycledAdditivesList, [mL1stream9RecycAdditiveMasses[i] + mL1stream23RecycAdditiveMasses[i] + mL1stream26RecycAdditiveMasses[i] - mL1stream29RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    totalLandfilledOtherMSW = stream12MSWValues
    
    #now for material loop trvw summaries. Note: this list mimics trvw maker below for "material loop 0"
    #creates  list to be iterated over for filling ML1 summary trvw
    dummyDictionary = {}
    
    listOfStreamsForNonRecycResinTRVWML1 = [mL1stream1NonRecycPlasticMasses, dummyDictionary, dummyDictionary, mL1stream4NonRecycPlasticMasses, mL1stream5NonRecycResinMasses,
                                            mL1stream6NonRecycResinMasses, dummyDictionary, mL1stream8ResinMasses, mL1stream9NonRecycPlasticMasses, mL1stream10NonRecycPlasticMasses,
                                            dummyDictionary, dummyDictionary, mL1stream13ResinMasses, dummyDictionary, dummyDictionary, mL1stream16NonRecycResinMasses, dummyDictionary,
                                            dummyDictionary, dummyDictionary, mL1stream20NonRecycResinMasses, mL1stream21NonRecycResinMasses, mL1stream22NonRecycResinMasses, mL1stream23NonRecycResinMasses,
                                            mL1stream24NonRecyResinMasses, mL1stream25NonRecycResinMasses, mL1stream26NonRecycResinMasses, mL1stream27NonRecycResinMasses, mL1stream28NonRecycResinMasses,
                                            mL1stream29NonRecycResinmasses, dummyDictionary, mL1totalIncinerationNonRecycResin, mL1totalLandfillNonRecycPlasticResin]
    
    listOfStreamforNonRecycAdditivesTRVWML1 = [dummyDictionary, mL1stream2NonRecycAdditiveMasses, dummyDictionary, mL1stream4NonRecycAdditiveMasses, mL1stream5NonRecycAdditiveMasses,
                                               mL1stream6NonRecycAdditiveMasses, dummyDictionary, mL1stream8AdditiveMasses, mL1stream9NonRecycAdditiveMasses, 
                                               mL1stream10NonRecycAdditiveMasses, dummyDictionary, dummyDictionary, mL1stream13Additivemasses, dummyDictionary,
                                               dummyDictionary, mL1Stream16totalNonRecycAdditives, dummyDictionary, mL1stream18NonRecycAdditives, mL1stream19NonRecycAdditives,
                                               mL1stream20NonRecycAdditiveMasses, mL1stream21NonRecycAdditiveMasses, mL1stream22NonRecycAdditiveMasses, mL1stream23NonRecycAdditiveMasses,
                                               mL1stream24NonRecycAdditiveMasses, mL1stream25NonRecycAdditiveMasses, mL1stream26NonRecycAdditiveMasses, 
                                               mL1stream27NonRecycAdditiveMasses, mL1stream23NonRecycAdditiveMasses, mL1stream29NonRecycAdditiveMasses, dummyDictionary,
                                               mL1totalIncinerationNonRecycAdditives, mL1totalLandfillNonRecycAdditives]
    
    listOfStreamforRecycResinTRVWML1 = [mL1stream1RecycPlasticMasses, dummyDictionary, dummyDictionary, mL1stream4RecycPlasticMasses, mL1stream5RecycResinMasses,
                                        mL1stream6RecycResinMasses, dummyDictionary, dummyDictionary, mL1stream9RecycPlasticMasses, mL1stream10RecycPlasticMasses,
                                        dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, mL1stream16RecycPlasticMasses,
                                        dummyDictionary, dummyDictionary, dummyDictionary, mL1stream20RecycResinMasses, dummyDictionary, dummyDictionary, 
                                        mL1stream23RecycResinMasses, mL1stream24RecycResinMasses, mL1stream25RecycResinMasses, mL1stream26RecycResinMasses, dummyDictionary,
                                        mL1stream23RecycResinMasses, mL1stream29RecycResinMasses, dummyDictionary, mL1totalIncinerationRecycResin, mL1totalLandfillRecycResin]
    
    listOfstreamforRecycAdditivesTRVWML1 = [mL1stream1RecycAdditiveMasses, dummyDictionary, dummyDictionary, mL1stream4RecycAdditiveMasses, mL1stream5RecycAdditiveMasses,
                                            mL1stream6RecycAdditiveMasses, dummyDictionary, dummyDictionary, mL1stream9RecycAdditiveMasses, mL1stream10RecycAdditiveMasses, 
                                            dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, mL1stream16RecycAdditiveMasses,
                                            dummyDictionary, mL1stream18RecycAdditives, dummyDictionary, mL1stream20RecycAdditiveMasses, dummyDictionary, dummyDictionary,
                                            mL1stream23RecycAdditiveMasses, mL1stream24RecycAdditiveMasses, mL1stream25RecycAdditiveMasses, mL1stream26RecycAdditiveMasses,
                                            dummyDictionary, mL1stream28RecycAdditiveMasses, mL1stream29RecycAdditiveMasses, dummyDictionary, mL1totalIncinerationRecycAdditives, 
                                            mL1totalLandfillRecycAdditives]
    
    listOfStreamMSWTRVW = [dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, 
                           stream8MSWMasses_, dummyDictionary, stream8MSWMasses_, stream11MSWValues, stream12MSWValues, stream13MSW, stream14MSWValues,
                           dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary,
                           dummyDictionary, dummyDictionary, stream25MSWValues, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary,
                          totalIncinerationMSW, totalLandfilledOtherMSW]
    matLoopRecycAdditives = []
    matLoopRecycAdditives.append(sum(list(mL1stream1RecycAdditiveMasses.values())))
    global mL1TRVWLists
    mL1TRVWLists = []
    mL1TRVWLists.clear() #clears to make sure that when new data is input, old data is erased
    
    #list comprehension that will create list of lists for addition to stream summary table. streamSummaryTRVWLister defined above
    mL1TRVWLists = [streamSummaryTRVWLister(listOfStreamsForNonRecycResinTRVWML1, i) for i in typesOfPlasticDomestic]+[streamSummaryTRVWLister(listOfStreamforNonRecycAdditivesTRVWML1, i) for i in otherResinAdditives] + [streamSummaryTRVWLister(listOfStreamforRecycResinTRVWML1, i) for i in recycledTypesOfPlasticDomestic] + [streamSummaryTRVWLister(listOfstreamforRecycAdditivesTRVWML1, i) for i in recycledAdditivesList] +[streamSummaryTRVWLister(listOfStreamMSWTRVW, i) for i in typesOfWastesForCalculations]
   
    #following list will be used to make other calculations easier later on by removing row title, which can then be added later on
    mL1listsWithoutTitles = [streamSummaryTRVWLister(listOfStreamsForNonRecycResinTRVWML1, i) for i in typesOfPlasticDomestic]+[streamSummaryTRVWLister(listOfStreamforNonRecycAdditivesTRVWML1, i) for i in otherResinAdditives] + [streamSummaryTRVWLister(listOfStreamforRecycResinTRVWML1, i) for i in recycledTypesOfPlasticDomestic] + [streamSummaryTRVWLister(listOfstreamforRecycAdditivesTRVWML1, i) for i in recycledAdditivesList] +[streamSummaryTRVWLister(listOfStreamMSWTRVW, i) for i in typesOfWastesForCalculations]
    for i in mL1listsWithoutTitles:
        del i[0]
    
    #Creates ash row list for addition to TRVW
    mL1ashTRVWList = ['Ash', 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,stream25AshMass, 0,0,0,0,0,0,0,]
    
    #Creates list for column sums at bottom of table, then Creates list of data lists that will be tacked on to the end of the stream summary TRVW
    mL1totalStreamMassesList = ['Total Mass excluding emissions']+[sum([i[b] for i in mL1listsWithoutTitles]) for b in range(32)]
    
    mL1listsToAdd =[mL1ashTRVWList, mL1totalStreamMassesList]
    
    mL1totalPlasticsStreamSummaryList = ['Total Plastics'] + [sum(i.values()) for i in listOfStreamsForNonRecycResinTRVWML1]
    
    for i in range(len(mL1totalPlasticsStreamSummaryList)):
        if mL1totalPlasticsStreamSummaryList[i] is int:
            mL1totalPlasticsStreamSummaryList[i] += sum(listOfStreamforRecycResinTRVWML1[i].values())            
    
    mL1listsToAdd.append(mL1totalPlasticsStreamSummaryList)
    
    mL1totalAdditivesStreamSummaryList = ['Total Additives'] + [sum(i.values()) for i in listOfStreamforNonRecycAdditivesTRVWML1]
    
    for i in range(len(mL1totalAdditivesStreamSummaryList)):
        if mL1totalAdditivesStreamSummaryList[i] is int:
            mL1totalAdditivesStreamSummaryList[i] += sum(listOfstreamforRecycAdditivesTRVWML1[i].values())
    
    mL1listsToAdd.append(mL1totalAdditivesStreamSummaryList)
    
    mL1actualMassEmissionTotalTRVWList = ['Actual mass of emission (Tons):'] + [0, 0, '-', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, stream25AshMass, 0, 0, 0, 0, 0, 0, 0]
    mL1listsToAdd.append(mL1actualMassEmissionTotalTRVWList)
    
    mL1totalEmissionsTRVWList = ['Total Emissions', 0,0, (sum(stream4AdditiveMasses_.values())+sum(stream4ResinMasses_.values()))*0.0025+sum(stream3Emissions.values()), 0,0,0, totalStream10Waste*230*0.00110231, 0,0,0,0,0,0,0, conditions[9]*1.10231131, 0, sum(emissionStream16.values()), 0, 0, sum(stream20Emissions.values()), 0, 0, sum(stream23Emissions.values()), 0, sum(stream24Emissions.values())+1.05*sum(stream11MSWValues.values()), sum(stream27Emissions.values()), sum(stream23Emissions.values()), sum(stream29Emissions.values()), stream30Emissions, 0, 0]
    mL1listsToAdd.append(mL1totalEmissionsTRVWList)
    
    
    
    mL1emissionsFromPlasticList = ['Emissions from plastic', 0,0, (sum(stream4AdditiveMasses_.values())+sum(stream4ResinMasses_.values()))*0.0025+sum(stream3Emissions.values()), 0,0,0, totalStream10Waste*230*0.00110231, 0,0,0,0,0,0,0, conditions[9]*1.10231131, 0, sum(emissionStream16.values()), 0, 0, sum(stream20Emissions.values()), 0, 0, sum(stream23Emissions.values()), 0, sum(stream24Emissions.values()),0, sum(stream27Emissions.values()), sum(stream23Emissions.values()), sum(stream29Emissions.values()), sum(stream26Emissions.values()), 0, 0]
    mL1listsToAdd.append(mL1emissionsFromPlasticList)
    
    
    mL1TRVWLists = mL1TRVWLists+mL1listsToAdd
    
    
    #MATERIAL LOOP 2
    mL1stream20NonRecycResinConversion = dict(zip(recycledTypesOfPlasticDomestic, [mL1stream20NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL1stream20NonRecycAdditiveConversion = dict(zip(recycledAdditivesList, [mL1stream20NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    
    #Streams 1-4
    mL2stream1RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL1stream20NonRecycResinConversion[i]+mL1stream20RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL2stream1RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL1stream20NonRecycAdditiveConversion[i]+mL1stream20RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    
    #from ORIGINAL, necessary to make following calculations that combine dicts with different sets of keys
    stream4ResinMassesConversion = dict(zip(recycledTypesOfPlasticDomestic, [stream4ResinMasses_[i] for i in typesOfPlasticDomestic]))
    stream4AdditiveMassConversion = dict(zip(recycledAdditivesList, [stream4AdditiveMasses_[i] for i in otherResinAdditives]))
    
    #continuing on with this material loop:
    mL2stream4NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [stream4ResinMassesConversion[i]-mL2stream1RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL2stream4NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [stream4AdditiveMassConversion[i]-mL2stream1RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    mL2stream4RecycAdditiveMasses = mL2stream1RecycAdditiveMasses
    mL2stream4RecycResinMasses = mL2stream1RecycResinMasses
    
    
    #finishing up stream 1
    mL2stream1NonRecycResinMasses = mL2stream4NonRecycResinMasses
    
    
    #stream 2
    mL2stream2NonRecycAdditiveMasses = mL2stream4NonRecycAdditiveMasses
    
    #Stream 5
    mL2stream5NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [polymerMigrationConstant*mL2stream4NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL2stream5NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [additiveMigrationConstant*mL2stream4NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL2stream5RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [polymerMigrationConstant*mL2stream4RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL2stream5RecycAdditiveMasses = dict(zip(recycledAdditivesList, [additiveMigrationConstant*mL2stream4RecycAdditiveMasses[i] for i in recycledAdditivesList]))


    #Stream 6
    mL2stream6NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [mL2stream4NonRecycResinMasses[i] - mL2stream5NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL2stream6NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL2stream4NonRecycAdditiveMasses[i] -mL2stream5NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL2stream6RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL2stream4RecycResinMasses[i] -mL2stream5RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL2stream6RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL2stream4RecycAdditiveMasses[i] - mL2stream5RecycAdditiveMasses[i] for i in recycledAdditivesList]))

    #Stream 8 (note: no stream 7 and stream 8 is the same in all loops)
    mL2stream8MSW = stream8MSWMasses_
    mL2stream8ResinMasses = stream27ResinMasses 
    mL2stream8AdditiveMasses = stream27TotalAdditivesMasses

    #Stream 9
    mL2stream9NonRecycPlasticMasses = dict(zip(typesOfPlasticDomestic, [assumedValues["Plastic waste lost to littering"]*mL2stream4NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL2stream9NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [assumedValues["Plastic waste lost to littering"]*mL2stream4NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL2stream9RecycPlasticMasses = dict(zip(recycledTypesOfPlasticDomestic, [assumedValues["Plastic waste lost to littering"]*mL2stream4RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL2stream9RecycAdditiveMasses = dict(zip(recycledAdditivesList, [assumedValues["Plastic waste lost to littering"]*mL2stream4RecycAdditiveMasses[i] for i in recycledAdditivesList]))

    #Stream 10
    
    mL2stream10NonRecycPlasticMasses = dict(zip(typesOfPlasticDomestic, [mL2stream8ResinMasses[i] + mL2stream6NonRecycResinMasses[i]-mL2stream9NonRecycPlasticMasses[i] for i in typesOfPlasticDomestic]))
    mL2stream10NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL2stream8AdditiveMasses[i]+mL2stream6NonRecycAdditiveMasses[i]-mL2stream9NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL2stream10RecycPlasticMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL2stream6RecycResinMasses[i]-mL2stream9RecycPlasticMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL2stream10RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL2stream6RecycAdditiveMasses[i]-mL2stream9RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    mL2stream10MSWMasses = stream8MSWMasses_
    
    #Streams 11, 12, 13, 14, and 15 Note: Streams 11, 12, 13, and 14 are the same in every loop. Stream 15 is empty
    mL2stream11 = stream11MSWValues
    mL2stream12 = stream12MSWValues
    mL2stream13ResinMasses = stream13ResinMasses
    mL2stream13Additivemasses = stream13AdditiveTotals
    mL2stream13MSW = stream13MSW
    mL2stream14 = stream14MSWValues
    
    
    #Stream 16
    mL2stream16RecycPlasticMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL2stream10RecycPlasticMasses[i]*reRecyclingRate for i in recycledTypesOfPlasticDomestic]))
    mL2stream16RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL2stream10RecycAdditiveMasses[i]*reRecyclingRate for i in recycledAdditivesList]))
    
    mL2stream16NonRecycResinMasses = mL1stream16NonRecycResinMasses
    mL2stream16NonRecycAdditiveMasses = mL1Stream16totalNonRecycAdditives
    
    #stream 18
    mL2stream18NonRecycAdditives = dict(zip(otherResinAdditives, [mL2stream16NonRecycAdditiveMasses[i]*assumedValues["Additive migration Fraction"] for i in otherResinAdditives]))
    mL2stream18RecycAdditives = dict(zip(recycledAdditivesList, [mL2stream16RecycAdditiveMasses[i]*assumedValues["Additive migration Fraction"] for i in recycledAdditivesList]))
    
    #stream 19 stays the same throughout the loops
    mL2stream19NonRecycAdditives = stream19AdditivesTotals
    
    #stream 21 stays the same throughout the loops
    mL2stream21NonRecycResinMasses = stream21ResinMasses_
    mL2stream21NonRecycAdditiveMasses = stream21AdditivesTotals
    
    #stream 22 stays the same throughout the loops
    mL2stream22NonRecycResinMasses = stream22ResinMasses_
    mL2stream22NonRecycAdditiveMasses = stream22AdditivesTotals
    
    #stream 23
    mL2stream23NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [(1-conditions[4])/2*mL2stream16NonRecycResinMasses[i] for i in typesOfPlasticDomestic])) 
    mL2stream23NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [(1-conditions[4])/2*mL2stream16NonRecycAdditiveMasses[i] for i in otherResinAdditives])) 
    mL2stream23RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [(1-conditions[4])/2*mL2stream16RecycPlasticMasses[i] for i in recycledTypesOfPlasticDomestic])) 
    mL2stream23RecycAdditiveMasses = dict(zip(recycledAdditivesList, [(1-conditions[4])/2*mL2stream16RecycAdditiveMasses[i] for i in recycledAdditivesList])) 

    #stream 28 is the same as stream 23
    mL2stream28NonRecycResinMasses = mL2stream23NonRecycResinMasses
    mL2stream28NonRecycAdditiveMasses = mL2stream23NonRecycAdditiveMasses
    mL2stream28RecycResinMasses = mL2stream23RecycResinMasses
    mL2stream28RecycAdditiveMasses = mL2stream23RecycAdditiveMasses
    
    #stream 20
    mL2stream20NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [mL2stream16NonRecycResinMasses[i]+mL2stream21NonRecycResinMasses[i]-mL2stream22NonRecycResinMasses[i] - mL2stream23NonRecycResinMasses[i]-mL2stream28NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL2stream20NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL2stream16NonRecycAdditiveMasses[i] - mL2stream18NonRecycAdditives[i]+mL2stream19NonRecycAdditives[i]+mL2stream21NonRecycAdditiveMasses[i]-mL2stream22NonRecycAdditiveMasses[i]-mL2stream23NonRecycAdditiveMasses[i]-mL2stream28NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL2stream20RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL2stream16RecycPlasticMasses[i]-mL2stream23RecycResinMasses[i]-mL2stream28RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL2stream20RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL2stream16RecycAdditiveMasses[i]-mL2stream18RecycAdditives[i]-mL2stream23RecycAdditiveMasses[i]-mL2stream28RecycAdditiveMasses[i] for i in recycledAdditivesList]))


    #stream 24
    mL2stream24NonRecyResinMasses = stream24ResinMasses
    mL2stream24NonRecycAdditiveMasses = stream24AdditiveTotals
    
    mL2stream24RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [(mL2stream10RecycPlasticMasses[i]-mL2stream16RecycPlasticMasses[i])*(conditions[7]/conditions[8]) for i in recycledTypesOfPlasticDomestic]))
    mL2stream24RecycAdditiveMasses = dict(zip(recycledAdditivesList, [(mL2stream10RecycAdditiveMasses[i]-mL2stream16RecycAdditiveMasses[i])*((conditions[7]/conditions[8])) for i in recycledAdditivesList]))
    
    #stream 25
    mL2stream25NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL2stream23NonRecycResinMasses[i]+mL2stream24NonRecyResinMasses[i]) for i in typesOfPlasticDomestic]))
    mL2stream25NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL2stream23NonRecycAdditiveMasses[i]+mL2stream24NonRecycAdditiveMasses[i]) for i in otherResinAdditives]))
    
    mL2stream25RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL2stream23RecycResinMasses[i]+mL2stream24RecycResinMasses[i]) for i in recycledTypesOfPlasticDomestic]))
    mL2stream25RecycAdditiveMasses = dict(zip(recycledAdditivesList, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL2stream23RecycAdditiveMasses[i]+mL2stream24RecycAdditiveMasses[i]) for i in recycledAdditivesList]))
    
    #stream 26
    mL2stream26NonRecycResinMasses = stream26ResinMasses
    mL2stream26NonRecycAdditiveMasses = stream26AdditiveTotals
    
    mL2stream26RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL2stream10RecycPlasticMasses[i]-mL2stream16RecycPlasticMasses[i]-mL2stream24RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL2stream26RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL2stream10RecycAdditiveMasses[i]-mL2stream16RecycAdditiveMasses[i]-mL2stream24RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    #stream 27 
    mL2stream27NonRecycResinMasses = stream27ResinMasses
    mL2stream27NonRecycAdditiveMasses = stream27TotalAdditivesMasses
    
    #stream 29
    mL2stream29NonRecycResinmasses = dict(zip(typesOfPlasticDomestic, [mL2stream4NonRecycResinMasses[i]*assumedValues["Plastic waste leak after landfill"] for i in typesOfPlasticDomestic]))
    mL2stream29NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL2stream4NonRecycAdditiveMasses[i]*assumedValues["Plastic waste leak after landfill"]+(mL2stream26NonRecycAdditiveMasses[i]+mL2stream28NonRecycAdditiveMasses[i])*0.00001 for i in otherResinAdditives]))
    mL2stream29RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL2stream4RecycResinMasses[i]*assumedValues["Plastic waste leak after landfill"] + (mL2stream26RecycResinMasses[i]+mL2stream28RecycResinMasses[i])*0.00001 for i in recycledTypesOfPlasticDomestic]))
    mL2stream29RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL2stream4RecycAdditiveMasses[i]*assumedValues["Plastic waste leak after landfill"]+(mL2stream26RecycAdditiveMasses[i]+mL2stream28RecycAdditiveMasses[i])*0.00001 for i in recycledAdditivesList]))
    
    #stream 30 is all 0's
    
    #Creates dict of total incineration for each kind of plastic and additive (stream 23 +stream 24).
    mL2totalIncinerationNonRecycResin = dict(zip(typesOfPlasticDomestic, [mL2stream23NonRecycResinMasses[i] + mL2stream24NonRecyResinMasses[i] for i in typesOfPlasticDomestic]))
    mL2totalIncinerationNonRecycAdditives = dict(zip(otherResinAdditives, [mL2stream24NonRecycAdditiveMasses[i] + mL2stream23NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL2totalIncinerationRecycResin = dict(zip(recycledTypesOfPlasticDomestic, [mL2stream23RecycResinMasses[i]+mL2stream24RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL2totalIncinerationRecycAdditives = dict(zip(recycledAdditivesList, [mL2stream23RecycAdditiveMasses[i] + mL2stream24RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    #Total Landfill Calculations: sums stream 9, 23, 26 and subtracts stream 29 resins, additive, MSW masses
    mL2totalLandfillNonRecycPlasticResin = dict(zip(typesOfPlasticDomestic, [mL2stream9NonRecycPlasticMasses[i] + mL2stream23NonRecycResinMasses[i] + mL2stream26NonRecycResinMasses[i] - mL2stream29NonRecycResinmasses[i] for i in typesOfPlasticDomestic]))
    mL2totalLandfillNonRecycAdditives = dict(zip(otherResinAdditives, [mL2stream9NonRecycAdditiveMasses[i] + mL2stream23NonRecycAdditiveMasses[i] + mL2stream26NonRecycAdditiveMasses[i] - mL2stream29NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL2totalLandfillRecycResin = dict(zip(recycledTypesOfPlasticDomestic, [mL2stream9RecycPlasticMasses[i] + mL2stream23RecycResinMasses[i] + mL2stream26RecycResinMasses[i] - mL2stream29RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL2totalLandfillRecycAdditives = dict(zip(recycledAdditivesList, [mL2stream9RecycAdditiveMasses[i] + mL2stream23RecycAdditiveMasses[i] + mL2stream26RecycAdditiveMasses[i] - mL2stream29RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    totalLandfilledOtherMSW = stream12MSWValues
    
    #now for material loop trvw summaries. Note: this list mimics trvw maker below for "material loop 0"
    #creates  list to be iterated over for filling ML1 summary trvw
    
    
    listOfStreamsForNonRecycResinTRVWmL2 = [mL2stream1NonRecycResinMasses, dummyDictionary, dummyDictionary, mL2stream4NonRecycResinMasses, mL2stream5NonRecycResinMasses,
                                            mL2stream6NonRecycResinMasses, dummyDictionary, mL2stream8ResinMasses, mL2stream9NonRecycPlasticMasses, mL2stream10NonRecycPlasticMasses,
                                            dummyDictionary, dummyDictionary, mL2stream13ResinMasses, dummyDictionary, dummyDictionary, mL2stream16NonRecycResinMasses, dummyDictionary,
                                            dummyDictionary, dummyDictionary, mL2stream20NonRecycResinMasses, mL2stream21NonRecycResinMasses, mL2stream22NonRecycResinMasses, mL2stream23NonRecycResinMasses,
                                            mL2stream24NonRecyResinMasses, mL2stream25NonRecycResinMasses, mL2stream26NonRecycResinMasses, mL2stream27NonRecycResinMasses, mL2stream28NonRecycResinMasses,
                                            mL2stream29NonRecycResinmasses, dummyDictionary, mL2totalIncinerationNonRecycResin, mL2totalLandfillNonRecycPlasticResin]
    
    
    
    listOfStreamforNonRecycAdditivesTRVWmL2 = [dummyDictionary, mL2stream2NonRecycAdditiveMasses, dummyDictionary, mL2stream4NonRecycAdditiveMasses, mL2stream5NonRecycAdditiveMasses,
                                               mL2stream6NonRecycAdditiveMasses, dummyDictionary, mL2stream8AdditiveMasses, mL2stream9NonRecycAdditiveMasses, 
                                               mL2stream10NonRecycAdditiveMasses, dummyDictionary, dummyDictionary, mL2stream13Additivemasses, dummyDictionary,
                                               dummyDictionary, mL2stream16NonRecycAdditiveMasses, dummyDictionary, mL2stream18NonRecycAdditives, mL2stream19NonRecycAdditives,
                                               mL2stream20NonRecycAdditiveMasses, mL2stream21NonRecycAdditiveMasses, mL2stream22NonRecycAdditiveMasses, mL2stream23NonRecycAdditiveMasses,
                                               mL2stream24NonRecycAdditiveMasses, mL2stream25NonRecycAdditiveMasses, mL2stream26NonRecycAdditiveMasses, 
                                               mL2stream27NonRecycAdditiveMasses, mL2stream23NonRecycAdditiveMasses, mL2stream29NonRecycAdditiveMasses, dummyDictionary,
                                               mL2totalIncinerationNonRecycAdditives, mL2totalLandfillNonRecycAdditives]
    
    listOfStreamforRecycResinTRVWmL2 = [mL2stream1RecycResinMasses, dummyDictionary, dummyDictionary, mL2stream4RecycResinMasses, mL2stream5RecycResinMasses,
                                        mL2stream6RecycResinMasses, dummyDictionary, dummyDictionary, mL2stream9RecycPlasticMasses, mL2stream10RecycPlasticMasses,
                                        dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, mL2stream16RecycPlasticMasses,
                                        dummyDictionary, dummyDictionary, dummyDictionary, mL2stream20RecycResinMasses, dummyDictionary, dummyDictionary, 
                                        mL2stream23RecycResinMasses, mL2stream24RecycResinMasses, mL2stream25RecycResinMasses, mL2stream26RecycResinMasses, dummyDictionary,
                                        mL2stream23RecycResinMasses, mL2stream29RecycResinMasses, dummyDictionary, mL2totalIncinerationRecycResin, mL2totalLandfillRecycResin]
    
    listOfstreamforRecycAdditivesTRVWmL2 = [mL2stream1RecycAdditiveMasses, dummyDictionary, dummyDictionary, mL2stream4RecycAdditiveMasses, mL2stream5RecycAdditiveMasses,
                                            mL2stream6RecycAdditiveMasses, dummyDictionary, dummyDictionary, mL2stream9RecycAdditiveMasses, mL2stream10RecycAdditiveMasses, 
                                            dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, mL2stream16RecycAdditiveMasses,
                                            dummyDictionary, mL2stream18RecycAdditives, dummyDictionary, mL2stream20RecycAdditiveMasses, dummyDictionary, dummyDictionary,
                                            mL2stream23RecycAdditiveMasses, mL2stream24RecycAdditiveMasses, mL2stream25RecycAdditiveMasses, mL2stream26RecycAdditiveMasses,
                                            dummyDictionary, mL2stream28RecycAdditiveMasses, mL2stream29RecycAdditiveMasses, dummyDictionary, mL2totalIncinerationRecycAdditives, 
                                            mL2totalLandfillRecycAdditives]
    
    listOfStreamMSWTRVW = [dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, 
                           stream8MSWMasses_, dummyDictionary, stream8MSWMasses_, stream11MSWValues, stream12MSWValues, stream13MSW, stream14MSWValues,
                           dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary,
                           dummyDictionary, dummyDictionary, stream25MSWValues, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary,
                          totalIncinerationMSW, totalLandfilledOtherMSW]
    
    matLoopRecycAdditives.append(sum(list(mL2stream1RecycAdditiveMasses.values())))

    
    global mL2TRVWLists
    mL2TRVWLists = []
    mL2TRVWLists.clear() #clears to make sure that when new data is input, old data is erased
    
    #list comprehension that will create list of lists for addition to stream summary table. streamSummaryTRVWLister defined above
    mL2TRVWLists = [streamSummaryTRVWLister(listOfStreamsForNonRecycResinTRVWmL2, i) for i in typesOfPlasticDomestic]+[streamSummaryTRVWLister(listOfStreamforNonRecycAdditivesTRVWmL2, i) for i in otherResinAdditives] + [streamSummaryTRVWLister(listOfStreamforRecycResinTRVWmL2, i) for i in recycledTypesOfPlasticDomestic] + [streamSummaryTRVWLister(listOfstreamforRecycAdditivesTRVWmL2, i) for i in recycledAdditivesList] +[streamSummaryTRVWLister(listOfStreamMSWTRVW, i) for i in typesOfWastesForCalculations]
   
    #following list will be used to make other calculations easier later on by removing row title, which can then be added later on
    mL2listsWithoutTitles = [streamSummaryTRVWLister(listOfStreamsForNonRecycResinTRVWmL2, i) for i in typesOfPlasticDomestic]+[streamSummaryTRVWLister(listOfStreamforNonRecycAdditivesTRVWmL2, i) for i in otherResinAdditives] + [streamSummaryTRVWLister(listOfStreamforRecycResinTRVWmL2, i) for i in recycledTypesOfPlasticDomestic] + [streamSummaryTRVWLister(listOfstreamforRecycAdditivesTRVWmL2, i) for i in recycledAdditivesList] +[streamSummaryTRVWLister(listOfStreamMSWTRVW, i) for i in typesOfWastesForCalculations]
    for i in mL2listsWithoutTitles:
        del i[0]
    
    #Creates ash row list for addition to TRVW
    mL2ashTRVWList = ['Ash', 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,stream25AshMass, 0,0,0,0,0,0,0,]
    
    #Creates list for column sums at bottom of table, then Creates list of data lists that will be tacked on to the end of the stream summary TRVW
    mL2totalStreamMassesList = ['Total Mass excluding emissions']+[sum([i[b] for i in mL2listsWithoutTitles]) for b in range(32)]
    
    mL2listsToAdd =[mL2ashTRVWList, mL2totalStreamMassesList]
    
    mL2totalPlasticsStreamSummaryList = ['Total Plastics'] + [sum(i.values()) for i in listOfStreamsForNonRecycResinTRVWmL2]
    
    for i in range(len(mL2totalPlasticsStreamSummaryList)):
        if mL2totalPlasticsStreamSummaryList[i] is int:
            mL2totalPlasticsStreamSummaryList[i] += sum(listOfStreamforRecycResinTRVWmL2[i].values())            
    
    mL2listsToAdd.append(mL2totalPlasticsStreamSummaryList)
    
    mL2totalAdditivesStreamSummaryList = ['Total Additives'] + [sum(i.values()) for i in listOfStreamforNonRecycAdditivesTRVWmL2]
    
    for i in range(len(mL2totalAdditivesStreamSummaryList)):
        if mL2totalAdditivesStreamSummaryList[i] is int:
            mL2totalAdditivesStreamSummaryList[i] += sum(listOfstreamforRecycAdditivesTRVWmL2[i].values())
    
    mL2listsToAdd.append(mL2totalAdditivesStreamSummaryList)
    
    mL2actualMassEmissionTotalTRVWList = ['Actual mass of emission (Tons):'] + [0, 0, '-', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, stream25AshMass, 0, 0, 0, 0, 0, 0, 0]
    mL2listsToAdd.append(mL2actualMassEmissionTotalTRVWList)
    
    mL2totalEmissionsTRVWList = ['Total Emissions', 0,0, (sum(stream4AdditiveMasses_.values())+sum(stream4ResinMasses_.values()))*0.0025+sum(stream3Emissions.values()), 0,0,0, totalStream10Waste*230*0.00110231, 0,0,0,0,0,0,0, conditions[9]*1.10231131, 0, sum(emissionStream16.values()), 0, 0, sum(stream20Emissions.values()), 0, 0, sum(stream23Emissions.values()), 0, sum(stream24Emissions.values())+1.05*sum(stream11MSWValues.values()), sum(stream27Emissions.values()), sum(stream23Emissions.values()), sum(stream29Emissions.values()), stream30Emissions, 0, 0]
    mL2listsToAdd.append(mL2totalEmissionsTRVWList)
    
    
    
    mL2emissionsFromPlasticList = ['Emissions from plastic', 0,0, (sum(stream4AdditiveMasses_.values())+sum(stream4ResinMasses_.values()))*0.0025+sum(stream3Emissions.values()), 0,0,0, totalStream10Waste*230*0.00110231, 0,0,0,0,0,0,0, conditions[9]*1.10231131, 0, sum(emissionStream16.values()), 0, 0, sum(stream20Emissions.values()), 0, 0, sum(stream23Emissions.values()), 0, sum(stream24Emissions.values()),0, sum(stream27Emissions.values()), sum(stream23Emissions.values()), sum(stream29Emissions.values()), sum(stream26Emissions.values()), 0, 0]
    mL2listsToAdd.append(mL2emissionsFromPlasticList)
    
    
    mL2TRVWLists = mL2TRVWLists+mL2listsToAdd
    
    
    
    
    #MATERIAL LOOP 3
    mL2stream20NonRecycResinConversion = dict(zip(recycledTypesOfPlasticDomestic, [mL2stream20NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL2stream20NonRecycAdditiveConversion = dict(zip(recycledAdditivesList, [mL2stream20NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    
    #Streams 1-4
    mL3stream1RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL2stream20NonRecycResinConversion[i]+mL2stream20RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL3stream1RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL2stream20NonRecycAdditiveConversion[i]+mL2stream20RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    
    #continuing on with this material loop:
    mL3stream4NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [stream4ResinMassesConversion[i]-mL3stream1RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL3stream4NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [stream4AdditiveMassConversion[i]-mL3stream1RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    mL3stream4RecycAdditiveMasses = mL3stream1RecycAdditiveMasses
    mL3stream4RecycResinMasses = mL3stream1RecycResinMasses
    
    
    #finishing up stream 1
    mL3stream1NonRecycResinMasses = mL3stream4NonRecycResinMasses
    
    
    #stream 2
    mL3stream2NonRecycAdditiveMasses = mL3stream4NonRecycAdditiveMasses
    
    #Stream 5
    mL3stream5NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [polymerMigrationConstant*mL3stream4NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL3stream5NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [additiveMigrationConstant*mL3stream4NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL3stream5RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [polymerMigrationConstant*mL3stream4RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL3stream5RecycAdditiveMasses = dict(zip(recycledAdditivesList, [additiveMigrationConstant*mL3stream4RecycAdditiveMasses[i] for i in recycledAdditivesList]))


    #Stream 6
    mL3stream6NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [mL3stream4NonRecycResinMasses[i] - mL3stream5NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL3stream6NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL3stream4NonRecycAdditiveMasses[i] -mL3stream5NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL3stream6RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL3stream4RecycResinMasses[i] -mL3stream5RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL3stream6RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL3stream4RecycAdditiveMasses[i] - mL3stream5RecycAdditiveMasses[i] for i in recycledAdditivesList]))

    #Stream 8 (note: no stream 7 and stream 8 is the same in all loops)
    mL3stream8MSW = stream8MSWMasses_
    mL3stream8ResinMasses = stream27ResinMasses 
    mL3stream8AdditiveMasses = stream27TotalAdditivesMasses

    #Stream 9
    mL3stream9NonRecycPlasticMasses = dict(zip(typesOfPlasticDomestic, [assumedValues["Plastic waste lost to littering"]*mL3stream4NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL3stream9NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [assumedValues["Plastic waste lost to littering"]*mL3stream4NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL3stream9RecycPlasticMasses = dict(zip(recycledTypesOfPlasticDomestic, [assumedValues["Plastic waste lost to littering"]*mL3stream4RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL3stream9RecycAdditiveMasses = dict(zip(recycledAdditivesList, [assumedValues["Plastic waste lost to littering"]*mL3stream4RecycAdditiveMasses[i] for i in recycledAdditivesList]))

    #Stream 10
    
    mL3stream10NonRecycPlasticMasses = dict(zip(typesOfPlasticDomestic, [mL3stream8ResinMasses[i] + mL3stream6NonRecycResinMasses[i]-mL3stream9NonRecycPlasticMasses[i] for i in typesOfPlasticDomestic]))
    mL3stream10NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL3stream8AdditiveMasses[i]+mL3stream6NonRecycAdditiveMasses[i]-mL3stream9NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL3stream10RecycPlasticMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL3stream6RecycResinMasses[i]-mL3stream9RecycPlasticMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL3stream10RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL3stream6RecycAdditiveMasses[i]-mL3stream9RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    mL3stream10MSWMasses = stream8MSWMasses_
    
    #Streams 11, 12, 13, 14, and 15 Note: Streams 11, 12, 13, and 14 are the same in every loop. Stream 15 is empty
    mL3stream11 = stream11MSWValues
    mL3stream12 = stream12MSWValues
    mL3stream13ResinMasses = stream13ResinMasses
    mL3stream13Additivemasses = stream13AdditiveTotals
    mL3stream13MSW = stream13MSW
    mL3stream14 = stream14MSWValues
    
    
    #Stream 16
    mL3stream16RecycPlasticMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL3stream10RecycPlasticMasses[i]*reRecyclingRate for i in recycledTypesOfPlasticDomestic]))
    mL3stream16RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL3stream10RecycAdditiveMasses[i]*reRecyclingRate for i in recycledAdditivesList]))
    
    mL3stream16NonRecycResinMasses = mL1stream16NonRecycResinMasses
    mL3stream16NonRecycAdditiveMasses = mL1Stream16totalNonRecycAdditives
    
    #stream 18
    mL3stream18NonRecycAdditives = dict(zip(otherResinAdditives, [mL3stream16NonRecycAdditiveMasses[i]*assumedValues["Additive migration Fraction"] for i in otherResinAdditives]))
    mL3stream18RecycAdditives = dict(zip(recycledAdditivesList, [mL3stream16RecycAdditiveMasses[i]*assumedValues["Additive migration Fraction"] for i in recycledAdditivesList]))
    
    #stream 19 stays the same throughout the loops
    mL3stream19NonRecycAdditives = stream19AdditivesTotals
    
    #stream 21 stays the same throughout the loops
    mL3stream21NonRecycResinMasses = stream21ResinMasses_
    mL3stream21NonRecycAdditiveMasses = stream21AdditivesTotals
    
    #stream 22 stays the same throughout the loops
    mL3stream22NonRecycResinMasses = stream22ResinMasses_
    mL3stream22NonRecycAdditiveMasses = stream22AdditivesTotals
    
    #stream 23
    mL3stream23NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [(1-conditions[4])/2*mL3stream16NonRecycResinMasses[i] for i in typesOfPlasticDomestic])) 
    mL3stream23NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [(1-conditions[4])/2*mL3stream16NonRecycAdditiveMasses[i] for i in otherResinAdditives])) 
    mL3stream23RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [(1-conditions[4])/2*mL3stream16RecycPlasticMasses[i] for i in recycledTypesOfPlasticDomestic])) 
    mL3stream23RecycAdditiveMasses = dict(zip(recycledAdditivesList, [(1-conditions[4])/2*mL3stream16RecycAdditiveMasses[i] for i in recycledAdditivesList])) 

    #stream 28 is the same as stream 23
    mL3stream28NonRecycResinMasses = mL3stream23NonRecycResinMasses
    mL3stream28NonRecycAdditiveMasses = mL3stream23NonRecycAdditiveMasses
    mL3stream28RecycResinMasses = mL3stream23RecycResinMasses
    mL3stream28RecycAdditiveMasses = mL3stream23RecycAdditiveMasses
    
    #stream 20
    mL3stream20NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [mL3stream16NonRecycResinMasses[i]+mL3stream21NonRecycResinMasses[i]-mL3stream22NonRecycResinMasses[i] - mL3stream23NonRecycResinMasses[i]-mL3stream28NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL3stream20NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL3stream16NonRecycAdditiveMasses[i] - mL3stream18NonRecycAdditives[i]+mL3stream19NonRecycAdditives[i]+mL3stream21NonRecycAdditiveMasses[i] -mL3stream22NonRecycAdditiveMasses[i] -mL3stream23NonRecycAdditiveMasses[i]-mL3stream28NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL3stream20RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL3stream16RecycPlasticMasses[i]-mL3stream23RecycResinMasses[i]-mL3stream28RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL3stream20RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL3stream16RecycAdditiveMasses[i]-mL3stream18RecycAdditives[i]-mL3stream23RecycAdditiveMasses[i]-mL3stream28RecycAdditiveMasses[i] for i in recycledAdditivesList]))


    #stream 24
    mL3stream24NonRecyResinMasses = stream24ResinMasses
    mL3stream24NonRecycAdditiveMasses = stream24AdditiveTotals
    
    mL3stream24RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [(mL3stream10RecycPlasticMasses[i]-mL3stream16RecycPlasticMasses[i])*(conditions[7]/conditions[8]) for i in recycledTypesOfPlasticDomestic]))
    mL3stream24RecycAdditiveMasses = dict(zip(recycledAdditivesList, [(mL3stream10RecycAdditiveMasses[i]-mL3stream16RecycAdditiveMasses[i])*((conditions[7]/conditions[8])) for i in recycledAdditivesList]))
    
    #stream 25
    mL3stream25NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL3stream23NonRecycResinMasses[i]+mL3stream24NonRecyResinMasses[i]) for i in typesOfPlasticDomestic]))
    mL3stream25NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL3stream23NonRecycAdditiveMasses[i]+mL3stream24NonRecycAdditiveMasses[i]) for i in otherResinAdditives]))
    
    mL3stream25RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL3stream23RecycResinMasses[i]+mL3stream24RecycResinMasses[i]) for i in recycledTypesOfPlasticDomestic]))
    mL3stream25RecycAdditiveMasses = dict(zip(recycledAdditivesList, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL3stream23RecycAdditiveMasses[i]+mL3stream24RecycAdditiveMasses[i]) for i in recycledAdditivesList]))
    
    #stream 26
    mL3stream26NonRecycResinMasses = stream26ResinMasses
    mL3stream26NonRecycAdditiveMasses = stream26AdditiveTotals
    
    mL3stream26RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL3stream10RecycPlasticMasses[i]-mL3stream16RecycPlasticMasses[i]-mL3stream24RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL3stream26RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL3stream10RecycAdditiveMasses[i]-mL3stream16RecycAdditiveMasses[i]-mL3stream24RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    #stream 27 
    mL3stream27NonRecycResinMasses = stream27ResinMasses
    mL3stream27NonRecycAdditiveMasses = stream27TotalAdditivesMasses
    
    #stream 29
    mL3stream29NonRecycResinmasses = dict(zip(typesOfPlasticDomestic, [mL3stream4NonRecycResinMasses[i]*assumedValues["Plastic waste leak after landfill"] for i in typesOfPlasticDomestic]))
    mL3stream29NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL3stream4NonRecycAdditiveMasses[i]*assumedValues["Plastic waste leak after landfill"]+(mL3stream26NonRecycAdditiveMasses[i]+mL3stream28NonRecycAdditiveMasses[i])*0.00001 for i in otherResinAdditives]))
    mL3stream29RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL3stream4RecycResinMasses[i]*assumedValues["Plastic waste leak after landfill"] + (mL3stream26RecycResinMasses[i]+mL3stream28RecycResinMasses[i])*0.00001 for i in recycledTypesOfPlasticDomestic]))
    mL3stream29RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL3stream4RecycAdditiveMasses[i]*assumedValues["Plastic waste leak after landfill"]+(mL3stream26RecycAdditiveMasses[i]+mL3stream28RecycAdditiveMasses[i])*0.00001 for i in recycledAdditivesList]))
    
    #stream 30 is all 0's
    
    #Creates dict of total incineration for each kind of plastic and additive (stream 23 +stream 24).
    mL3totalIncinerationNonRecycResin = dict(zip(typesOfPlasticDomestic, [mL3stream23NonRecycResinMasses[i] + mL3stream24NonRecyResinMasses[i] for i in typesOfPlasticDomestic]))
    mL3totalIncinerationNonRecycAdditives = dict(zip(otherResinAdditives, [mL3stream24NonRecycAdditiveMasses[i] + mL3stream23NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL3totalIncinerationRecycResin = dict(zip(recycledTypesOfPlasticDomestic, [mL3stream23RecycResinMasses[i]+mL3stream24RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL3totalIncinerationRecycAdditives = dict(zip(recycledAdditivesList, [mL3stream23RecycAdditiveMasses[i] + mL3stream24RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    #Total Landfill Calculations: sums stream 9, 23, 26 and subtracts stream 29 resins, additive, MSW masses
    mL3totalLandfillNonRecycPlasticResin = dict(zip(typesOfPlasticDomestic, [mL3stream9NonRecycPlasticMasses[i] + mL3stream23NonRecycResinMasses[i] + mL3stream26NonRecycResinMasses[i] - mL3stream29NonRecycResinmasses[i] for i in typesOfPlasticDomestic]))
    mL3totalLandfillNonRecycAdditives = dict(zip(otherResinAdditives, [mL3stream9NonRecycAdditiveMasses[i] + mL3stream23NonRecycAdditiveMasses[i] + mL3stream26NonRecycAdditiveMasses[i] - mL3stream29NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL3totalLandfillRecycResin = dict(zip(recycledTypesOfPlasticDomestic, [mL3stream9RecycPlasticMasses[i] + mL3stream23RecycResinMasses[i] + mL3stream26RecycResinMasses[i] - mL3stream29RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL3totalLandfillRecycAdditives = dict(zip(recycledAdditivesList, [mL3stream9RecycAdditiveMasses[i] + mL3stream23RecycAdditiveMasses[i] + mL3stream26RecycAdditiveMasses[i] - mL3stream29RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    totalLandfilledOtherMSW = stream12MSWValues
    
    #now for material loop trvw summaries. Note: this list mimics trvw maker below for "material loop 0"
    #creates  list to be iterated over for filling ML1 summary trvw
    
    
    listOfStreamsForNonRecycResinTRVWmL3 = [mL3stream1NonRecycResinMasses, dummyDictionary, dummyDictionary, mL3stream4NonRecycResinMasses, mL3stream5NonRecycResinMasses,
                                            mL3stream6NonRecycResinMasses, dummyDictionary, mL3stream8ResinMasses, mL3stream9NonRecycPlasticMasses, mL3stream10NonRecycPlasticMasses,
                                            dummyDictionary, dummyDictionary, mL3stream13ResinMasses, dummyDictionary, dummyDictionary, mL3stream16NonRecycResinMasses, dummyDictionary,
                                            dummyDictionary, dummyDictionary, mL3stream20NonRecycResinMasses, mL3stream21NonRecycResinMasses, mL3stream22NonRecycResinMasses, mL3stream23NonRecycResinMasses,
                                            mL3stream24NonRecyResinMasses, mL3stream25NonRecycResinMasses, mL3stream26NonRecycResinMasses, mL3stream27NonRecycResinMasses, mL3stream28NonRecycResinMasses,
                                            mL3stream29NonRecycResinmasses, dummyDictionary, mL3totalIncinerationNonRecycResin, mL3totalLandfillNonRecycPlasticResin]
    
    
    
    listOfStreamforNonRecycAdditivesTRVWmL3 = [dummyDictionary, mL3stream2NonRecycAdditiveMasses, dummyDictionary, mL3stream4NonRecycAdditiveMasses, mL3stream5NonRecycAdditiveMasses,
                                               mL3stream6NonRecycAdditiveMasses, dummyDictionary, mL3stream8AdditiveMasses, mL3stream9NonRecycAdditiveMasses, 
                                               mL3stream10NonRecycAdditiveMasses, dummyDictionary, dummyDictionary, mL3stream13Additivemasses, dummyDictionary,
                                               dummyDictionary, mL3stream16NonRecycAdditiveMasses, dummyDictionary, mL3stream18NonRecycAdditives, mL3stream19NonRecycAdditives,
                                               mL3stream20NonRecycAdditiveMasses, mL3stream21NonRecycAdditiveMasses, mL3stream22NonRecycAdditiveMasses, mL3stream23NonRecycAdditiveMasses,
                                               mL3stream24NonRecycAdditiveMasses, mL3stream25NonRecycAdditiveMasses, mL3stream26NonRecycAdditiveMasses, 
                                               mL3stream27NonRecycAdditiveMasses, mL3stream23NonRecycAdditiveMasses, mL3stream29NonRecycAdditiveMasses, dummyDictionary,
                                               mL3totalIncinerationNonRecycAdditives, mL3totalLandfillNonRecycAdditives]
    
    listOfStreamforRecycResinTRVWmL3 = [mL3stream1RecycResinMasses, dummyDictionary, dummyDictionary, mL3stream4RecycResinMasses, mL3stream5RecycResinMasses,
                                        mL3stream6RecycResinMasses, dummyDictionary, dummyDictionary, mL3stream9RecycPlasticMasses, mL3stream10RecycPlasticMasses,
                                        dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, mL3stream16RecycPlasticMasses,
                                        dummyDictionary, dummyDictionary, dummyDictionary, mL3stream20RecycResinMasses, dummyDictionary, dummyDictionary, 
                                        mL3stream23RecycResinMasses, mL3stream24RecycResinMasses, mL3stream25RecycResinMasses, mL3stream26RecycResinMasses, dummyDictionary,
                                        mL3stream23RecycResinMasses, mL3stream29RecycResinMasses, dummyDictionary, mL3totalIncinerationRecycResin, mL3totalLandfillRecycResin]
    
    listOfstreamforRecycAdditivesTRVWmL3 = [mL3stream1RecycAdditiveMasses, dummyDictionary, dummyDictionary, mL3stream4RecycAdditiveMasses, mL3stream5RecycAdditiveMasses,
                                            mL3stream6RecycAdditiveMasses, dummyDictionary, dummyDictionary, mL3stream9RecycAdditiveMasses, mL3stream10RecycAdditiveMasses, 
                                            dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, mL3stream16RecycAdditiveMasses,
                                            dummyDictionary, mL3stream18RecycAdditives, dummyDictionary, mL3stream20RecycAdditiveMasses, dummyDictionary, dummyDictionary,
                                            mL3stream23RecycAdditiveMasses, mL3stream24RecycAdditiveMasses, mL3stream25RecycAdditiveMasses, mL3stream26RecycAdditiveMasses,
                                            dummyDictionary, mL3stream28RecycAdditiveMasses, mL3stream29RecycAdditiveMasses, dummyDictionary, mL3totalIncinerationRecycAdditives, 
                                            mL3totalLandfillRecycAdditives]
    
    listOfStreamMSWTRVW = [dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, 
                           stream8MSWMasses_, dummyDictionary, stream8MSWMasses_, stream11MSWValues, stream12MSWValues, stream13MSW, stream14MSWValues,
                           dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary,
                           dummyDictionary, dummyDictionary, stream25MSWValues, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary,
                          totalIncinerationMSW, totalLandfilledOtherMSW]
    
    matLoopRecycAdditives.append(sum(list(mL3stream1RecycAdditiveMasses.values())))

    global mL3TRVWLists
    mL3TRVWLists = []
    mL3TRVWLists.clear() #clears to make sure that when new data is input, old data is erased
    
    #list comprehension that will create list of lists for addition to stream summary table. streamSummaryTRVWLister defined above
    mL3TRVWLists = [streamSummaryTRVWLister(listOfStreamsForNonRecycResinTRVWmL3, i) for i in typesOfPlasticDomestic]+[streamSummaryTRVWLister(listOfStreamforNonRecycAdditivesTRVWmL3, i) for i in otherResinAdditives] + [streamSummaryTRVWLister(listOfStreamforRecycResinTRVWmL3, i) for i in recycledTypesOfPlasticDomestic] + [streamSummaryTRVWLister(listOfstreamforRecycAdditivesTRVWmL3, i) for i in recycledAdditivesList] +[streamSummaryTRVWLister(listOfStreamMSWTRVW, i) for i in typesOfWastesForCalculations]
   
    #following list will be used to make other calculations easier later on by removing row title, which can then be added later on
    mL3listsWithoutTitles = [streamSummaryTRVWLister(listOfStreamsForNonRecycResinTRVWmL3, i) for i in typesOfPlasticDomestic]+[streamSummaryTRVWLister(listOfStreamforNonRecycAdditivesTRVWmL3, i) for i in otherResinAdditives] + [streamSummaryTRVWLister(listOfStreamforRecycResinTRVWmL3, i) for i in recycledTypesOfPlasticDomestic] + [streamSummaryTRVWLister(listOfstreamforRecycAdditivesTRVWmL3, i) for i in recycledAdditivesList] +[streamSummaryTRVWLister(listOfStreamMSWTRVW, i) for i in typesOfWastesForCalculations]
    for i in mL3listsWithoutTitles:
        del i[0]
    
    #Creates ash row list for addition to TRVW
    mL3ashTRVWList = ['Ash', 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,stream25AshMass, 0,0,0,0,0,0,0,]
    
    #Creates list for column sums at bottom of table, then Creates list of data lists that will be tacked on to the end of the stream summary TRVW
    mL3totalStreamMassesList = ['Total Mass excluding emissions']+[sum([i[b] for i in mL3listsWithoutTitles]) for b in range(32)]
    
    mL3listsToAdd =[mL3ashTRVWList, mL3totalStreamMassesList]
    
    mL3totalPlasticsStreamSummaryList = ['Total Plastics'] + [sum(i.values()) for i in listOfStreamsForNonRecycResinTRVWmL3]
    
    for i in range(len(mL3totalPlasticsStreamSummaryList)):
        if mL3totalPlasticsStreamSummaryList[i] is int:
            mL3totalPlasticsStreamSummaryList[i] += sum(listOfStreamforRecycResinTRVWmL3[i].values())            
    
    mL3listsToAdd.append(mL3totalPlasticsStreamSummaryList)
    
    mL3totalAdditivesStreamSummaryList = ['Total Additives'] + [sum(i.values()) for i in listOfStreamforNonRecycAdditivesTRVWmL3]
    
    for i in range(len(mL3totalAdditivesStreamSummaryList)):
        if mL3totalAdditivesStreamSummaryList[i] is int:
            mL3totalAdditivesStreamSummaryList[i] += sum(listOfstreamforRecycAdditivesTRVWmL3[i].values())
    
    mL3listsToAdd.append(mL3totalAdditivesStreamSummaryList)
    
    mL3actualMassEmissionTotalTRVWList = ['Actual mass of emission (Tons):'] + [0, 0, '-', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, stream25AshMass, 0, 0, 0, 0, 0, 0, 0]
    mL3listsToAdd.append(mL3actualMassEmissionTotalTRVWList)
    
    mL3totalEmissionsTRVWList = ['Total Emissions', 0,0, (sum(stream4AdditiveMasses_.values())+sum(stream4ResinMasses_.values()))*0.0025+sum(stream3Emissions.values()), 0,0,0, totalStream10Waste*230*0.00110231, 0,0,0,0,0,0,0, conditions[9]*1.10231131, 0, sum(emissionStream16.values()), 0, 0, sum(stream20Emissions.values()), 0, 0, sum(stream23Emissions.values()), 0, sum(stream24Emissions.values())+1.05*sum(stream11MSWValues.values()), sum(stream27Emissions.values()), sum(stream23Emissions.values()), sum(stream29Emissions.values()), stream30Emissions, 0, 0]
    mL3listsToAdd.append(mL3totalEmissionsTRVWList)
    
    
    
    mL3emissionsFromPlasticList = ['Emissions from plastic', 0,0, (sum(stream4AdditiveMasses_.values())+sum(stream4ResinMasses_.values()))*0.0025+sum(stream3Emissions.values()), 0,0,0, totalStream10Waste*230*0.00110231, 0,0,0,0,0,0,0, conditions[9]*1.10231131, 0, sum(emissionStream16.values()), 0, 0, sum(stream20Emissions.values()), 0, 0, sum(stream23Emissions.values()), 0, sum(stream24Emissions.values()),0, sum(stream27Emissions.values()), sum(stream23Emissions.values()), sum(stream29Emissions.values()), sum(stream26Emissions.values()), 0, 0]
    mL3listsToAdd.append(mL3emissionsFromPlasticList)
    
    
    mL3TRVWLists = mL3TRVWLists+mL3listsToAdd
    
    #MATERIAL LOOP 4
    mL3stream20NonRecycResinConversion = dict(zip(recycledTypesOfPlasticDomestic, [mL3stream20NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL3stream20NonRecycAdditiveConversion = dict(zip(recycledAdditivesList, [mL3stream20NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    
    #Streams 1-4
    mL4stream1RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL3stream20NonRecycResinConversion[i]+mL2stream20RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL4stream1RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL3stream20NonRecycAdditiveConversion[i]+mL2stream20RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    
    #continuing on with this material loop:
    mL4stream4NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [stream4ResinMassesConversion[i]-mL4stream1RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL4stream4NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [stream4AdditiveMassConversion[i]-mL4stream1RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    mL4stream4RecycAdditiveMasses = mL4stream1RecycAdditiveMasses
    mL4stream4RecycResinMasses = mL4stream1RecycResinMasses
    
    
    #finishing up stream 1
    mL4stream1NonRecycResinMasses = mL4stream4NonRecycResinMasses
    
    
    #stream 2
    mL4stream2NonRecycAdditiveMasses = mL4stream4NonRecycAdditiveMasses
    
    #Stream 5
    mL4stream5NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [polymerMigrationConstant*mL4stream4NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL4stream5NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [additiveMigrationConstant*mL4stream4NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL4stream5RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [polymerMigrationConstant*mL4stream4RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL4stream5RecycAdditiveMasses = dict(zip(recycledAdditivesList, [additiveMigrationConstant*mL4stream4RecycAdditiveMasses[i] for i in recycledAdditivesList]))


    #Stream 6
    mL4stream6NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [mL4stream4NonRecycResinMasses[i] - mL4stream5NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL4stream6NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL4stream4NonRecycAdditiveMasses[i] -mL4stream5NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL4stream6RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL4stream4RecycResinMasses[i] -mL4stream5RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL4stream6RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL4stream4RecycAdditiveMasses[i] - mL4stream5RecycAdditiveMasses[i] for i in recycledAdditivesList]))

    #Stream 8 (note: no stream 7 and stream 8 is the same in all loops)
    mL4stream8MSW = stream8MSWMasses_
    mL4stream8ResinMasses = stream27ResinMasses 
    mL4stream8AdditiveMasses = stream27TotalAdditivesMasses

    #Stream 9
    mL4stream9NonRecycPlasticMasses = dict(zip(typesOfPlasticDomestic, [assumedValues["Plastic waste lost to littering"]*mL4stream4NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL4stream9NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [assumedValues["Plastic waste lost to littering"]*mL4stream4NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL4stream9RecycPlasticMasses = dict(zip(recycledTypesOfPlasticDomestic, [assumedValues["Plastic waste lost to littering"]*mL4stream4RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL4stream9RecycAdditiveMasses = dict(zip(recycledAdditivesList, [assumedValues["Plastic waste lost to littering"]*mL4stream4RecycAdditiveMasses[i] for i in recycledAdditivesList]))

    #Stream 10
    
    mL4stream10NonRecycPlasticMasses = dict(zip(typesOfPlasticDomestic, [mL4stream8ResinMasses[i] + mL4stream6NonRecycResinMasses[i]-mL4stream9NonRecycPlasticMasses[i] for i in typesOfPlasticDomestic]))
    mL4stream10NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL4stream8AdditiveMasses[i]+mL4stream6NonRecycAdditiveMasses[i]-mL4stream9NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL4stream10RecycPlasticMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL4stream6RecycResinMasses[i]-mL4stream9RecycPlasticMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL4stream10RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL4stream6RecycAdditiveMasses[i]-mL4stream9RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    mL4stream10MSWMasses = stream8MSWMasses_
    
    #Streams 11, 12, 13, 14, and 15 Note: Streams 11, 12, 13, and 14 are the same in every loop. Stream 15 is empty
    mL4stream11 = stream11MSWValues
    mL4stream12 = stream12MSWValues
    mL4stream13ResinMasses = stream13ResinMasses
    mL4stream13Additivemasses = stream13AdditiveTotals
    mL4stream13MSW = stream13MSW
    mL4stream14 = stream14MSWValues
    
    
    #Stream 16
    mL4stream16RecycPlasticMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL4stream10RecycPlasticMasses[i]*reRecyclingRate for i in recycledTypesOfPlasticDomestic]))
    mL4stream16RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL4stream10RecycAdditiveMasses[i]*reRecyclingRate for i in recycledAdditivesList]))
    
    mL4stream16NonRecycResinMasses = mL1stream16NonRecycResinMasses
    mL4stream16NonRecycAdditiveMasses = mL1Stream16totalNonRecycAdditives
    
    #stream 18
    mL4stream18NonRecycAdditives = dict(zip(otherResinAdditives, [mL4stream16NonRecycAdditiveMasses[i]*assumedValues["Additive migration Fraction"] for i in otherResinAdditives]))
    mL4stream18RecycAdditives = dict(zip(recycledAdditivesList, [mL4stream16RecycAdditiveMasses[i]*assumedValues["Additive migration Fraction"] for i in recycledAdditivesList]))
    
    #stream 19 stays the same throughout the loops
    mL4stream19NonRecycAdditives = stream19AdditivesTotals
    
    #stream 21 stays the same throughout the loops
    mL4stream21NonRecycResinMasses = stream21ResinMasses_
    mL4stream21NonRecycAdditiveMasses = stream21AdditivesTotals
    
    #stream 22 stays the same throughout the loops
    mL4stream22NonRecycResinMasses = stream22ResinMasses_
    mL4stream22NonRecycAdditiveMasses = stream22AdditivesTotals
    
    #stream 23
    mL4stream23NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [(1-conditions[4])/2*mL4stream16NonRecycResinMasses[i] for i in typesOfPlasticDomestic])) 
    mL4stream23NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [(1-conditions[4])/2*mL4stream16NonRecycAdditiveMasses[i] for i in otherResinAdditives])) 
    mL4stream23RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [(1-conditions[4])/2*mL4stream16RecycPlasticMasses[i] for i in recycledTypesOfPlasticDomestic])) 
    mL4stream23RecycAdditiveMasses = dict(zip(recycledAdditivesList, [(1-conditions[4])/2*mL4stream16RecycAdditiveMasses[i] for i in recycledAdditivesList])) 

    #stream 28 is the same as stream 23
    mL4stream28NonRecycResinMasses = mL4stream23NonRecycResinMasses
    mL4stream28NonRecycAdditiveMasses = mL4stream23NonRecycAdditiveMasses
    mL4stream28RecycResinMasses = mL4stream23RecycResinMasses
    mL4stream28RecycAdditiveMasses = mL4stream23RecycAdditiveMasses
    
    #stream 20
    mL4stream20NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [mL4stream16NonRecycResinMasses[i]+mL4stream21NonRecycResinMasses[i]-mL4stream22NonRecycResinMasses[i] - mL4stream23NonRecycResinMasses[i]-mL4stream28NonRecycResinMasses[i] for i in typesOfPlasticDomestic]))
    mL4stream20NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL4stream16NonRecycAdditiveMasses[i] - mL4stream18NonRecycAdditives[i]+mL4stream19NonRecycAdditives[i]+mL4stream21NonRecycAdditiveMasses[i] -mL4stream22NonRecycAdditiveMasses[i] -mL4stream23NonRecycAdditiveMasses[i]-mL4stream28NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL4stream20RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL4stream16RecycPlasticMasses[i]-mL4stream23RecycResinMasses[i]-mL4stream28RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL4stream20RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL4stream16RecycAdditiveMasses[i]-mL4stream18RecycAdditives[i]-mL4stream23RecycAdditiveMasses[i]-mL4stream28RecycAdditiveMasses[i] for i in recycledAdditivesList]))


    #stream 24
    mL4stream24NonRecyResinMasses = stream24ResinMasses
    mL4stream24NonRecycAdditiveMasses = stream24AdditiveTotals
    
    mL4stream24RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [(mL4stream10RecycPlasticMasses[i]-mL4stream16RecycPlasticMasses[i])*(conditions[7]/conditions[8]) for i in recycledTypesOfPlasticDomestic]))
    mL4stream24RecycAdditiveMasses = dict(zip(recycledAdditivesList, [(mL4stream10RecycAdditiveMasses[i]-mL4stream16RecycAdditiveMasses[i])*((conditions[7]/conditions[8])) for i in recycledAdditivesList]))
    
    #stream 25
    mL4stream25NonRecycResinMasses = dict(zip(typesOfPlasticDomestic, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL4stream23NonRecycResinMasses[i]+mL4stream24NonRecyResinMasses[i]) for i in typesOfPlasticDomestic]))
    mL4stream25NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL4stream23NonRecycAdditiveMasses[i]+mL4stream24NonRecycAdditiveMasses[i]) for i in otherResinAdditives]))
    
    mL4stream25RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL4stream23RecycResinMasses[i]+mL4stream24RecycResinMasses[i]) for i in recycledTypesOfPlasticDomestic]))
    mL4stream25RecycAdditiveMasses = dict(zip(recycledAdditivesList, [(1-assumedValues["Incineration Efficiency Fraction"])*(mL4stream23RecycAdditiveMasses[i]+mL4stream24RecycAdditiveMasses[i]) for i in recycledAdditivesList]))
    
    #stream 26
    mL4stream26NonRecycResinMasses = stream26ResinMasses
    mL4stream26NonRecycAdditiveMasses = stream26AdditiveTotals
    
    mL4stream26RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL4stream10RecycPlasticMasses[i]-mL4stream16RecycPlasticMasses[i]-mL4stream24RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL4stream26RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL4stream10RecycAdditiveMasses[i]-mL4stream16RecycAdditiveMasses[i]-mL4stream24RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    #stream 27 
    mL4stream27NonRecycResinMasses = stream27ResinMasses
    mL4stream27NonRecycAdditiveMasses = stream27TotalAdditivesMasses
    
    #stream 29
    mL4stream29NonRecycResinmasses = dict(zip(typesOfPlasticDomestic, [mL4stream4NonRecycResinMasses[i]*assumedValues["Plastic waste leak after landfill"] for i in typesOfPlasticDomestic]))
    mL4stream29NonRecycAdditiveMasses = dict(zip(otherResinAdditives, [mL4stream4NonRecycAdditiveMasses[i]*assumedValues["Plastic waste leak after landfill"]+(mL4stream26NonRecycAdditiveMasses[i]+mL4stream28NonRecycAdditiveMasses[i])*0.00001 for i in otherResinAdditives]))
    mL4stream29RecycResinMasses = dict(zip(recycledTypesOfPlasticDomestic, [mL4stream4RecycResinMasses[i]*assumedValues["Plastic waste leak after landfill"] + (mL4stream26RecycResinMasses[i]+mL4stream28RecycResinMasses[i])*0.00001 for i in recycledTypesOfPlasticDomestic]))
    mL4stream29RecycAdditiveMasses = dict(zip(recycledAdditivesList, [mL4stream4RecycAdditiveMasses[i]*assumedValues["Plastic waste leak after landfill"]+(mL4stream26RecycAdditiveMasses[i]+mL4stream28RecycAdditiveMasses[i])*0.00001 for i in recycledAdditivesList]))
    
    #stream 30 is all 0's
    
    
    #Creates dict of total incineration for each kind of plastic and additive (stream 23 +stream 24).
    mL4totalIncinerationNonRecycResin = dict(zip(typesOfPlasticDomestic, [mL4stream23NonRecycResinMasses[i] + mL4stream24NonRecyResinMasses[i] for i in typesOfPlasticDomestic]))
    mL4totalIncinerationNonRecycAdditives = dict(zip(otherResinAdditives, [mL4stream24NonRecycAdditiveMasses[i] + mL4stream23NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL4totalIncinerationRecycResin = dict(zip(recycledTypesOfPlasticDomestic, [mL4stream23RecycResinMasses[i]+mL4stream24RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL4totalIncinerationRecycAdditives = dict(zip(recycledAdditivesList, [mL4stream23RecycAdditiveMasses[i] + mL4stream24RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    #Total Landfill Calculations: sums stream 9, 23, 26 and subtracts stream 29 resins, additive, MSW masses
    mL4totalLandfillNonRecycPlasticResin = dict(zip(typesOfPlasticDomestic, [mL4stream9NonRecycPlasticMasses[i] + mL4stream23NonRecycResinMasses[i] + mL4stream26NonRecycResinMasses[i] - mL4stream29NonRecycResinmasses[i] for i in typesOfPlasticDomestic]))
    mL4totalLandfillNonRecycAdditives = dict(zip(otherResinAdditives, [mL4stream9NonRecycAdditiveMasses[i] + mL4stream23NonRecycAdditiveMasses[i] + mL4stream26NonRecycAdditiveMasses[i] - mL4stream29NonRecycAdditiveMasses[i] for i in otherResinAdditives]))
    mL4totalLandfillRecycResin = dict(zip(recycledTypesOfPlasticDomestic, [mL4stream9RecycPlasticMasses[i] + mL4stream23RecycResinMasses[i] + mL4stream26RecycResinMasses[i] - mL4stream29RecycResinMasses[i] for i in recycledTypesOfPlasticDomestic]))
    mL4totalLandfillRecycAdditives = dict(zip(recycledAdditivesList, [mL4stream9RecycAdditiveMasses[i] + mL4stream23RecycAdditiveMasses[i] + mL4stream26RecycAdditiveMasses[i] - mL4stream29RecycAdditiveMasses[i] for i in recycledAdditivesList]))
    
    totalLandfilledOtherMSW = stream12MSWValues
    
    #now for material loop trvw summaries. Note: this list mimics trvw maker below for "material loop 0"
    #creates  list to be iterated over for filling ML1 summary trvw
    
    
    listOfStreamsForNonRecycResinTRVWmL4 = [mL4stream1NonRecycResinMasses, dummyDictionary, dummyDictionary, mL4stream4NonRecycResinMasses, mL4stream5NonRecycResinMasses,
                                            mL4stream6NonRecycResinMasses, dummyDictionary, mL4stream8ResinMasses, mL4stream9NonRecycPlasticMasses, mL4stream10NonRecycPlasticMasses,
                                            dummyDictionary, dummyDictionary, mL4stream13ResinMasses, dummyDictionary, dummyDictionary, mL4stream16NonRecycResinMasses, dummyDictionary,
                                            dummyDictionary, dummyDictionary, mL4stream20NonRecycResinMasses, mL4stream21NonRecycResinMasses, mL4stream22NonRecycResinMasses, mL4stream23NonRecycResinMasses,
                                            mL4stream24NonRecyResinMasses, mL4stream25NonRecycResinMasses, mL4stream26NonRecycResinMasses, mL4stream27NonRecycResinMasses, mL4stream28NonRecycResinMasses,
                                            mL4stream29NonRecycResinmasses, dummyDictionary, mL4totalIncinerationNonRecycResin, mL4totalLandfillNonRecycPlasticResin]
    
    
    
    listOfStreamforNonRecycAdditivesTRVWmL4 = [dummyDictionary, mL4stream2NonRecycAdditiveMasses, dummyDictionary, mL4stream4NonRecycAdditiveMasses, mL4stream5NonRecycAdditiveMasses,
                                               mL4stream6NonRecycAdditiveMasses, dummyDictionary, mL4stream8AdditiveMasses, mL4stream9NonRecycAdditiveMasses, 
                                               mL4stream10NonRecycAdditiveMasses, dummyDictionary, dummyDictionary, mL4stream13Additivemasses, dummyDictionary,
                                               dummyDictionary, mL4stream16NonRecycAdditiveMasses, dummyDictionary, mL4stream18NonRecycAdditives, mL4stream19NonRecycAdditives,
                                               mL4stream20NonRecycAdditiveMasses, mL4stream21NonRecycAdditiveMasses, mL4stream22NonRecycAdditiveMasses, mL4stream23NonRecycAdditiveMasses,
                                               mL4stream24NonRecycAdditiveMasses, mL4stream25NonRecycAdditiveMasses, mL4stream26NonRecycAdditiveMasses, 
                                               mL4stream27NonRecycAdditiveMasses, mL4stream23NonRecycAdditiveMasses, mL4stream29NonRecycAdditiveMasses, dummyDictionary,
                                               mL4totalIncinerationNonRecycAdditives, mL4totalLandfillNonRecycAdditives]
    
    listOfStreamforRecycResinTRVWmL4 = [mL4stream1RecycResinMasses, dummyDictionary, dummyDictionary, mL4stream4RecycResinMasses, mL4stream5RecycResinMasses,
                                        mL4stream6RecycResinMasses, dummyDictionary, dummyDictionary, mL4stream9RecycPlasticMasses, mL4stream10RecycPlasticMasses,
                                        dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, mL4stream16RecycPlasticMasses,
                                        dummyDictionary, dummyDictionary, dummyDictionary, mL4stream20RecycResinMasses, dummyDictionary, dummyDictionary, 
                                        mL4stream23RecycResinMasses, mL4stream24RecycResinMasses, mL4stream25RecycResinMasses, mL4stream26RecycResinMasses, dummyDictionary,
                                        mL4stream23RecycResinMasses, mL4stream29RecycResinMasses, dummyDictionary, mL4totalIncinerationRecycResin, mL4totalLandfillRecycResin]
    
    listOfstreamforRecycAdditivesTRVWmL4 = [mL4stream1RecycAdditiveMasses, dummyDictionary, dummyDictionary, mL4stream4RecycAdditiveMasses, mL4stream5RecycAdditiveMasses,
                                            mL4stream6RecycAdditiveMasses, dummyDictionary, dummyDictionary, mL4stream9RecycAdditiveMasses, mL4stream10RecycAdditiveMasses, 
                                            dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, mL4stream16RecycAdditiveMasses,
                                            dummyDictionary, mL4stream18RecycAdditives, dummyDictionary, mL4stream20RecycAdditiveMasses, dummyDictionary, dummyDictionary,
                                            mL4stream23RecycAdditiveMasses, mL4stream24RecycAdditiveMasses, mL4stream25RecycAdditiveMasses, mL4stream26RecycAdditiveMasses,
                                            dummyDictionary, mL4stream28RecycAdditiveMasses, mL4stream29RecycAdditiveMasses, dummyDictionary, mL4totalIncinerationRecycAdditives, 
                                            mL4totalLandfillRecycAdditives]
    
    listOfStreamMSWTRVW = [dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, 
                           stream8MSWMasses_, dummyDictionary, stream8MSWMasses_, stream11MSWValues, stream12MSWValues, stream13MSW, stream14MSWValues,
                           dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary,
                           dummyDictionary, dummyDictionary, stream25MSWValues, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary,
                          totalIncinerationMSW, totalLandfilledOtherMSW]
    matLoopRecycAdditives.append(sum(list(mL4stream1RecycAdditiveMasses.values())))

    global mL4TRVWLists
    mL4TRVWLists = []
    mL4TRVWLists.clear() #clears to make sure that when new data is input, old data is erased
    
    #list comprehension that will create list of lists for addition to stream summary table. streamSummaryTRVWLister defined above
    mL4TRVWLists = [streamSummaryTRVWLister(listOfStreamsForNonRecycResinTRVWmL4, i) for i in typesOfPlasticDomestic]+[streamSummaryTRVWLister(listOfStreamforNonRecycAdditivesTRVWmL4, i) for i in otherResinAdditives] + [streamSummaryTRVWLister(listOfStreamforRecycResinTRVWmL4, i) for i in recycledTypesOfPlasticDomestic] + [streamSummaryTRVWLister(listOfstreamforRecycAdditivesTRVWmL4, i) for i in recycledAdditivesList] +[streamSummaryTRVWLister(listOfStreamMSWTRVW, i) for i in typesOfWastesForCalculations]
   
    #following list will be used to make other calculations easier later on by removing row title, which can then be added later on
    mL4listsWithoutTitles = [streamSummaryTRVWLister(listOfStreamsForNonRecycResinTRVWmL4, i) for i in typesOfPlasticDomestic]+[streamSummaryTRVWLister(listOfStreamforNonRecycAdditivesTRVWmL4, i) for i in otherResinAdditives] + [streamSummaryTRVWLister(listOfStreamforRecycResinTRVWmL4, i) for i in recycledTypesOfPlasticDomestic] + [streamSummaryTRVWLister(listOfstreamforRecycAdditivesTRVWmL4, i) for i in recycledAdditivesList] +[streamSummaryTRVWLister(listOfStreamMSWTRVW, i) for i in typesOfWastesForCalculations]
    for i in mL4listsWithoutTitles:
        del i[0]
    
    #Creates ash row list for addition to TRVW
    mL4ashTRVWList = ['Ash', 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,stream25AshMass, 0,0,0,0,0,0,0,]
    
    #Creates list for column sums at bottom of table, then Creates list of data lists that will be tacked on to the end of the stream summary TRVW
    mL4totalStreamMassesList = ['Total Mass excluding emissions']+[sum([i[b] for i in mL4listsWithoutTitles]) for b in range(32)]
    
    mL4listsToAdd =[mL4ashTRVWList, mL4totalStreamMassesList]
    
    mL4totalPlasticsStreamSummaryList = ['Total Plastics'] + [sum(i.values()) for i in listOfStreamsForNonRecycResinTRVWmL4]
    
    for i in range(len(mL4totalPlasticsStreamSummaryList)):
        if mL4totalPlasticsStreamSummaryList[i] is int:
            mL4totalPlasticsStreamSummaryList[i] += sum(listOfStreamforRecycResinTRVWmL4[i].values())            
    
    mL4listsToAdd.append(mL4totalPlasticsStreamSummaryList)
    
    mL4totalAdditivesStreamSummaryList = ['Total Additives'] + [sum(i.values()) for i in listOfStreamforNonRecycAdditivesTRVWmL4]
    
    for i in range(len(mL4totalAdditivesStreamSummaryList)):
        if mL4totalAdditivesStreamSummaryList[i] is int:
            mL4totalAdditivesStreamSummaryList[i] += sum(listOfstreamforRecycAdditivesTRVWmL4[i].values())
    
    mL4listsToAdd.append(mL4totalAdditivesStreamSummaryList)
    
    mL4actualMassEmissionTotalTRVWList = ['Actual mass of emission (Tons):'] + [0, 0, '-', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, stream25AshMass, 0, 0, 0, 0, 0, 0, 0]
    mL4listsToAdd.append(mL4actualMassEmissionTotalTRVWList)
    
    mL4totalEmissionsTRVWList = ['Total Emissions', 0,0, (sum(stream4AdditiveMasses_.values())+sum(stream4ResinMasses_.values()))*0.0025+sum(stream3Emissions.values()), 0,0,0, totalStream10Waste*230*0.00110231, 0,0,0,0,0,0,0, conditions[9]*1.10231131, 0, sum(emissionStream16.values()), 0, 0, sum(stream20Emissions.values()), 0, 0, sum(stream23Emissions.values()), 0, sum(stream24Emissions.values())+1.05*sum(stream11MSWValues.values()), sum(stream27Emissions.values()), sum(stream23Emissions.values()), sum(stream29Emissions.values()), stream30Emissions, 0, 0]
    mL4listsToAdd.append(mL4totalEmissionsTRVWList)
    
    
    
    mL4emissionsFromPlasticList = ['Emissions from plastic', 0,0, (sum(stream4AdditiveMasses_.values())+sum(stream4ResinMasses_.values()))*0.0025+sum(stream3Emissions.values()), 0,0,0, totalStream10Waste*230*0.00110231, 0,0,0,0,0,0,0, conditions[9]*1.10231131, 0, sum(emissionStream16.values()), 0, 0, sum(stream20Emissions.values()), 0, 0, sum(stream23Emissions.values()), 0, sum(stream24Emissions.values()),0, sum(stream27Emissions.values()), sum(stream23Emissions.values()), sum(stream29Emissions.values()), sum(stream26Emissions.values()), 0, 0]
    mL4listsToAdd.append(mL4emissionsFromPlasticList)
    
    
    mL4TRVWLists = mL4TRVWLists+mL4listsToAdd
    
    
    matLoopRecycAdditives.append(sum(mL4stream20NonRecycAdditiveMasses.values())+sum(mL4stream20RecycAdditiveMasses.values()))
    
    
    ################################################################################
    ################################################################################
    #LCI Summary
    #Sheet= Material Flow Analysis Summary
    #Creates list of categories for following dicts
    
    #Manufacturing Phase
    #Used as divisor in following input calculations:
    matFlowManufactureDivisor = stream1_stream2_total+sum(stream20PlasticCalcMasses.values())
    #Sums each kind of resin from streams 1 and 20 and divides by total mass in streams1,2, and 20; then does same for total chemical additives in those same streams
    matFlowManufactureInput = dict(zip(typesOfPlasticDomestic, [(stream1PlasticMasses[i]+stream20ResinMasses[i])/matFlowManufactureDivisor for i in typesOfPlasticDomestic]))
    matFlowManufactureInput['Chemical Additives'] = (sum(stream2AdditiveMasses.values())+sum(stream20TotalAdditives.values()))/matFlowManufactureDivisor
    
    #Sums each kind of resin and additive (additives all grouped together) from stream4 and divides by total mass in stream 4
    matFlowManufactureOutput = dict(zip(typesOfPlasticDomestic, [stream4ResinMasses_[i]/stream4TotalMass_ for i in typesOfPlasticDomestic]))
    matFlowManufactureOutput['Chemical Additives'] = sum(stream4AdditiveMasses_.values())/stream4TotalMass_
    
    
    #Littering, Inhalation, and derm expos unavailable
    matFlowManufactureLitter = dict(zip(matFlowAnalSumCategories, ["Unavailable" for i in matFlowAnalSumCategories]))
    matFlowManufactureWater = dict(zip(matFlowAnalSumCategories, ["Unavailable" for i in matFlowAnalSumCategories]))
    matFlowManufactureAir = dict(zip(matFlowAnalSumCategories, ["Unavailable" for i in matFlowAnalSumCategories]))
    matFlowManufactureInhal = matFlowManufactureLitter
    matFlowManufactureDerm = matFlowManufactureLitter
    
    #Greenhouse gas emissions from manufacturing= stream3 Emission factor*conversion factor +0.0025: 
    matFlowManufactureGHG = dict(zip(typesOfPlasticDomestic, [stream3EmissionFactor[i]*1.10231+0.0025 for i in typesOfPlasticDomestic]))
    matFlowManufactureGHG['Chemical Additives'] = matFlowManufactureGHG['Other Resin']
    
    
    #TRVW (table) lists
    global manufactureDictList
    manufactureDictList = []
    manufactureDictList = [matFlowManufactureInput, matFlowManufactureOutput, matFlowManufactureLitter, matFlowManufactureAir, matFlowManufactureWater, matFlowManufactureInhal, 
                               matFlowManufactureDerm, matFlowManufactureGHG]

    #####################################################
    #Use Phase
    
    #Input same as output of manufacture
    matFlowUseInput = matFlowManufactureOutput
    
    #Output determined based on stream 6 resins, total additives, and total mass
    matFlowUseOutput = dict(zip(typesOfPlasticDomestic, [stream6ResinTotals[i]/(sum(plasticsMassDict.values())) for i in typesOfPlasticDomestic]))
    matFlowUseOutput['Chemical Additives'] = sum(stream6AdditiveTotals.values())/(sum(plasticsMassDict.values()))
    
    
    #Littering Calculations: stream 5/(total of stream 4)
    matFlowUseLittering = dict(zip(typesOfPlasticDomestic, [(stream5ResinMasses[i]/stream4TotalMass_)*(1-0.029) for i in typesOfPlasticDomestic]))
    matFlowUseLittering['Chemical Additives'] = sum(stream5AdditiveMasses.values())/stream4TotalMass_*(1-0.029)
    
    matFlowUseWater = dict(zip(typesOfPlasticDomestic, [(stream5ResinMasses[i]/stream4TotalMass_)*(0.029) for i in typesOfPlasticDomestic]))
    matFlowUseWater['Chemical Additives'] = sum(stream5AdditiveMasses.values())/stream4TotalMass_*(0.029)

    matFlowUseAir = dict(zip(matFlowAnalSumCategories, ["Unavailable" for i in matFlowAnalSumCategories]))
    
    #Inhalation, dermal and GHG unavailable
    matFlowUseInhal = matFlowManufactureDerm
    matFlowUseDerm = matFlowManufactureDerm
    matFlowUseGHG = matFlowManufactureDerm
    
    
    global useDictList #creates list of above dicts
    useDictList = []
    useDictList = [matFlowUseInput, matFlowUseOutput, matFlowUseLittering, matFlowUseAir, matFlowUseWater, matFlowUseInhal, matFlowUseDerm, 
                       matFlowUseGHG]
    
    
    ############################################################
    #Collection and Sorting Phase (CSP)
    
    #Input: divisor is total plastic and additive mass in stream 6, 27
    #Creates dict, key = category, value = proportion of total mass. stream6+27
    matFlowCSPInputDivisor = sum(stream6AdditiveTotals.values())+sum(stream6ResinTotals.values())+sum(stream27ResinMasses.values())+sum(stream27TotalAdditivesMasses.values())
    matFlowCSPInput = dict(zip(typesOfPlasticDomestic, [(stream6ResinTotals[i]+stream27ResinMasses[i])/matFlowCSPInputDivisor for i in typesOfPlasticDomestic]))
    matFlowCSPInput['Chemical Additives'] = (sum(stream6AdditiveTotals.values())+sum(stream27TotalAdditivesMasses.values()))/matFlowCSPInputDivisor
    
    
    #Output: stream27+16+24+26
    matFlowCSPOutput = dict(zip(typesOfPlasticDomestic, [(stream27ResinMasses[i]+stream16ResinMasses_[i]+stream24ResinMasses[i]+stream26ResinMasses[i])/matFlowCSPInputDivisor for i in typesOfPlasticDomestic]))
    matFlowCSPOutput['Chemical Additives'] = (sum(stream27TotalAdditivesMasses.values())+sum(totalAdditivesStream16_.values())+sum(stream24AdditiveTotals.values())+sum(stream26AdditiveTotals.values()))/matFlowCSPInputDivisor
    
    #Littering: Input-Output
    matFlowCSPLittering = dict(zip(matFlowCSPOutput.keys(), [(matFlowCSPInput[i]-matFlowCSPOutput[i])*(1-0.029) for i in matFlowCSPOutput.keys()]))
    matFlowCSPWater = dict(zip(matFlowCSPOutput.keys(), [(matFlowCSPInput[i]-matFlowCSPOutput[i])*(0.029) for i in matFlowCSPOutput.keys()]))
    matFlowCSPAir = dict(zip(matFlowAnalSumCategories, ["Unavailable" for i in matFlowAnalSumCategories]))

    #Emissions: 
    matFlowCSPGHG = dict(zip(matFlowAnalSumCategories, [wasteFacilityEmissions/totalStream10Waste for i in matFlowAnalSumCategories]))
        
    #Inhalation and dermal exposure unavailable
    matFlowCSPInhal = matFlowUseInhal
    matFlowCSPDerm = matFlowUseInhal
    
    #creates list of above dicts
    global cspDictList
    cspDictList = []
    cspDictList = [matFlowCSPInput, matFlowCSPOutput, matFlowCSPLittering, matFlowCSPWater, matFlowCSPAir, matFlowCSPInhal, matFlowCSPDerm,
                       matFlowCSPGHG]
    
 
    ############################################################
    #Mechanical Recycling
    
    #Input: (stream16+19+21)/combined total of those streams
    matFlowMechRecycInputDivisor = sum(stream16PlasticCalcMasses.values())+sum(stream19AdditivesTotals.values())+sum(stream21PlasticMasses.values())+stream19DegradationProducts+stream19Contaminants
    matFlowMechRecycInput = dict(zip(typesOfPlasticDomestic, [(stream16ResinMasses_[i]+stream21ResinMasses_[i])/matFlowMechRecycInputDivisor for i in typesOfPlasticDomestic]))
    matFlowMechRecycInput['Chemical Additives']=(sum(totalAdditivesStream16_.values())+sum(stream19AdditivesTotals.values())+sum(stream21AdditivesTotals.values())+stream19Contaminants+stream19DegradationProducts)/matFlowMechRecycInputDivisor
    
    #Output: (stream20+28+23+22)/sum of all three
    matFlowMechRecycOutDivisor = 2*(sum(stream23AdditiveMasses_.values())+sum(stream23ResinMasses_.values()))+sum(stream22PlasticMasses.values())+sum(stream20ResinMasses.values())+sum(stream20TotalAdditives.values())
    matFlowMechRecycOutput = dict(zip(typesOfPlasticDomestic, [(stream20ResinMasses[i]+2*stream23ResinMasses_[i]+stream22ResinMasses_[i])/matFlowMechRecycOutDivisor for i in typesOfPlasticDomestic]))
    matFlowMechRecycOutput['Chemical Additives'] = (sum(stream20TotalAdditives.values())+2*sum(stream23AdditiveMasses_.values())+sum(stream22AdditivesTotals.values()))/matFlowMechRecycOutDivisor
    
    #Releases/littering (input*0.0001)
    matFlowMechRecycLittering = dict(zip(matFlowAnalSumCategories, [matFlowMechRecycInput[i]*0.0001*(1-0.029) for i in matFlowAnalSumCategories]))
    matFlowMechRecycWater = dict(zip(matFlowAnalSumCategories, [matFlowMechRecycInput[i]*0.0001*(0.029) for i in matFlowAnalSumCategories]))
    matFlowMechRecycAir = dict(zip(matFlowAnalSumCategories, ["Unavailable" for i in matFlowAnalSumCategories]))

    #Inhalation Exposure (105/(9.072*10^8)*21834*250)/matFlowInputDivisor*Input
    matFlowMechRecycInhal = dict(zip(matFlowAnalSumCategories, [matFlowMechRecycInput[i]*(105/(9.072*10**8)*21834*250)/matFlowMechRecycInputDivisor for i in matFlowAnalSumCategories]))
    
    #Dermal Exposure (2170/(9.072*10^8))*21834*250*Input/matFlowInputDivisor
    matFlowMechRecycDermExp = dict(zip(matFlowAnalSumCategories, [matFlowMechRecycInput[i]*(2170/(9.072*10**8))*21834*250/matFlowMechRecycInputDivisor for i in matFlowAnalSumCategories]))
    
    #GHG Emissions stream16 emissions factors
    matFlowMechRecycGHG = dict(zip(typesOfPlasticDomestic, [emissionFactors[i]*1.10231 for i in typesOfPlasticDomestic]))
    matFlowMechRecycGHG['Chemical Additives']=matFlowMechRecycGHG['Other Resin']
    
    #creates list of above dicts
    global mechRecycDictList
    mechRecycDictList = []
    mechRecycDictList = [matFlowMechRecycInput, matFlowMechRecycOutput, matFlowMechRecycLittering, matFlowMechRecycAir, matFlowMechRecycWater,
                             matFlowMechRecycInhal, matFlowMechRecycDermExp, matFlowMechRecycGHG]

    
    ###############################################################
    #Incineration
    #Input: (stream23+24)/sum of stream totals
    matFlowIncinInputDivisor = sum(stream23AdditiveMasses_.values())+sum(stream23ResinMasses_.values())+sum(stream24PlasticMasses.values())
    matFlowIncinInput = dict(zip(typesOfPlasticDomestic, [(stream23ResinMasses_[i]+stream24ResinMasses[i])/matFlowIncinInputDivisor for i in typesOfPlasticDomestic]))
    matFlowIncinInput['Chemical Additives'] = (sum(stream23AdditiveMasses_.values())+sum(stream24AdditiveTotals.values()))/matFlowIncinInputDivisor
    
    #Output: 0
    matFlowIncinOutput = dict(zip(matFlowAnalSumCategories, [0 for i in matFlowAnalSumCategories]))
    
    #Littering: stream25/sum of stream 23, 24
    matFlowIncinLitter = dict(zip(typesOfPlasticDomestic, [stream25ResinMasses[i]/matFlowIncinInputDivisor*(1-0.029) for i in typesOfPlasticDomestic]))
    matFlowIncinLitter['Chemical Additives']=sum(stream25AdditiveMasses.values())/matFlowIncinInputDivisor*(1-0.029)
    
    matFlowIncinWater = dict(zip(typesOfPlasticDomestic, [stream25ResinMasses[i]/matFlowIncinInputDivisor*(0.029) for i in typesOfPlasticDomestic]))
    matFlowIncinWater['Chemical Additives']=sum(stream25AdditiveMasses.values())/matFlowIncinInputDivisor*(0.029)
    
    matFlowIncinAir = dict(zip(matFlowAnalSumCategories, ["Unavailable" for i in matFlowAnalSumCategories]))
    
    #Inhalataion and dermal exposure: 0
    matFlowIncinInhal = dict(zip(matFlowAnalSumCategories, [0 for i in matFlowAnalSumCategories]))
    matFlowIncinDerm = matFlowIncinInhal
    
    #GHG: stream24 emission factors
    matFlowIncinGHG = dict(zip(typesOfPlasticDomestic, [stream24EmissionsFactors[i]*1.10231 for i in typesOfPlasticDomestic]))
    matFlowIncinGHG['Chemical Additives'] = matFlowIncinGHG['Other Resin']
    
    
    global incinDictList
    incinDictList = []
    incinDictList = [matFlowIncinInput, matFlowIncinOutput, matFlowIncinLitter, matFlowIncinWater, matFlowIncinAir, matFlowIncinInhal, matFlowIncinDerm,
                         matFlowIncinGHG]
    
    ################################################################
    #Landfilling: 
    
    #Input: stream26+28/sum of the two
    matFlowLandInputDivisor = sum(stream26PlasticMasses.values())+sum(stream23ResinMasses_.values())+sum(stream23AdditiveMasses_.values())
    matFlowLandInput = dict(zip(typesOfPlasticDomestic, [(stream26ResinMasses[i]+stream23ResinMasses_[i])/matFlowLandInputDivisor for i in typesOfPlasticDomestic]))
    matFlowLandInput['Chemical Additives'] = (sum(stream26AdditiveTotals.values())+sum(stream23AdditiveMasses_.values()))/matFlowLandInputDivisor 
    
    
    #Output = 0
    matFlowLandOutput = matFlowIncinInhal
    
    #Littering: stream29/sum of stream26,28
    matFlowLandLitter = dict(zip(typesOfPlasticDomestic, [stream29ResinMasses[i]/matFlowLandInputDivisor*(1-0.029) for i in typesOfPlasticDomestic]))
    matFlowLandLitter['Chemical Additives'] = (sum(stream29AdditiveMasses.values())/matFlowLandInputDivisor)*(1-0.029)
    
    matFlowLandWater = dict(zip(typesOfPlasticDomestic, [stream29ResinMasses[i]/matFlowLandInputDivisor*(0.029) for i in typesOfPlasticDomestic]))
    matFlowLandWater['Chemical Additives'] = (sum(stream29AdditiveMasses.values())/matFlowLandInputDivisor)*(0.029)

    matFlowLandAir = dict(zip(matFlowAnalSumCategories, ["Unavailable" for i in matFlowAnalSumCategories]))

    
    #Dermal and Inhalation Exposure = 0
    matFlowLandInhal = matFlowIncinInhal
    matFlowLandDerm = matFlowIncinInhal
    
    #GHG: emission factor = 0.04*1.10231
    matFlowLandGHG = dict(zip(matFlowAnalSumCategories, [0.04*1.10231 for i in matFlowAnalSumCategories]))
    
    #Creates list of above dicts
    global landDictList
    landDictList = []
    landDictList = [matFlowLandInput, matFlowLandOutput, matFlowLandLitter, matFlowLandAir, matFlowLandWater, matFlowLandInhal, matFlowLandDerm,
                        matFlowLandGHG]
    
    #############################################################################
    #Stream Summary TRVW shtuff
    #creates dictionary that data will be extracted from to create stream summary trvw
    dummyDictionary = {}  #to serve in place of streams where no data is (e.g. no additive data in resin lists) to make sure no inappropriate numbers are added to table
    
    #These dicts will be iterated over to look for data. (e.g. will be searched for "PET", "HDPE", etc.)
    listOfStreamsForResinTRVW = [stream1PlasticMasses, dummyDictionary, dummyDictionary, stream4ResinMasses_, stream5ResinMasses,
                                 stream6ResinTotals, dummyDictionary, stream27ResinMasses, stream9ResinTotals, stream10ResinTotals,
                                 dummyDictionary, dummyDictionary, stream13ResinMasses, dummyDictionary, dummyDictionary, stream16ResinMasses_,
                                 dummyDictionary, dummyDictionary, dummyDictionary, stream20ResinMasses, stream21ResinMasses_, stream22ResinMasses_,
                                 stream23ResinMasses_, stream24ResinMasses, stream25ResinMasses, stream26ResinMasses, stream27ResinMasses,
                                 stream23ResinMasses_, stream29ResinMasses, dummyDictionary, stream31ResinMasses, stream32ResinMasses, stream33Resinmasses, 
                                 stream34ResinMasses,  totalIncinerationPlasticResin, totalLandfillPlasticResin]
                                
    listOfStreamforAdditivesTRVW = [dummyDictionary, stream2AdditiveMasses, dummyDictionary, stream4AdditiveMasses_, stream5AdditiveMasses, 
                                    stream6AdditiveTotals, dummyDictionary, stream27TotalAdditivesMasses, stream9TotalAdditives, stream10AdditiveTotals,
                                    dummyDictionary, dummyDictionary, stream13AdditiveTotals, dummyDictionary, dummyDictionary, totalAdditivesStream16_,
                                    dummyDictionary, stream18AdditiveMigration, stream19AdditivesTotals, stream20TotalAdditives, stream21AdditivesTotals,
                                    stream22AdditivesTotals, stream23AdditiveMasses_, stream24AdditiveTotals, stream25AdditiveMasses, stream26AdditiveTotals,
                                    stream27TotalAdditivesMasses, stream23AdditiveMasses_, stream29AdditiveMasses, dummyDictionary, stream31AdditiveMasses,
                                    stream32AdditiveMasses, stream33AdditiveMasses, stream34AdditiveMasses, totalIncinerationAdditives, totalLandfillAdditives]
    
    listOfStreamMSWTRVW = [dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, 
                           stream8MSWMasses_, dummyDictionary, stream8MSWMasses_, stream11MSWValues, stream12MSWValues, stream13MSW, stream14MSWValues,
                           dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary,
                           dummyDictionary, dummyDictionary, stream25MSWValues, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary,
                          dummyDictionary, dummyDictionary, dummyDictionary, dummyDictionary, totalIncinerationMSW, totalLandfilledOtherMSW]
    
    #creates single list to be iterated over for filling stream summary trvw
    
    global streamTRVWLists
    streamTRVWLists = []
    streamTRVWLists.clear() #clears to make sure that when new data is input, old data is erased
    
    #list comprehension that will create list of lists for addition to stream summary table. streamSummaryTRVWLister defined above
    streamTRVWLists = [streamSummaryTRVWLister(listOfStreamsForResinTRVW, i) for i in typesOfPlasticDomestic]+[streamSummaryTRVWLister(listOfStreamforAdditivesTRVW, i) for i in otherResinAdditives]+[streamSummaryTRVWLister(listOfStreamMSWTRVW, i) for i in typesOfWastesForCalculations]
   
    #following list will be used to make other calculations easier later on by removing row title, which can then be added later on
    listsWithoutTitles = [streamSummaryTRVWLister(listOfStreamsForResinTRVW, i) for i in typesOfPlasticDomestic]+[streamSummaryTRVWLister(listOfStreamforAdditivesTRVW, i) for i in otherResinAdditives]+[streamSummaryTRVWLister(listOfStreamMSWTRVW, i) for i in typesOfWastesForCalculations]
    for i in listsWithoutTitles:
        del i[0]
    
    #Creates ash row list for addition to TRVW
    ashTRVWList = ['Ash', 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,stream25AshMass, 0,0,0,0,0,0,0,]
    
    #Creates list for column sums at bottom of table, then Creates list of data lists that will be tacked on to the end of the stream summary TRVW
    totalStreamMassesList = ['Total Mass excluding emissions']+[sum([i[b] for i in listsWithoutTitles]) for b in range(32)]
    
    listsToAdd =[ashTRVWList, totalStreamMassesList]
    
    totalPlasticsStreamSummaryList = ['Total Plastics'] + [sum(i.values()) for i in listOfStreamsForResinTRVW]
    listsToAdd.append(totalPlasticsStreamSummaryList)
    
    totalAdditivesStreamSummaryList = ['Total Additives'] + [sum(i.values()) for i in listOfStreamforAdditivesTRVW]
    listsToAdd.append(totalAdditivesStreamSummaryList)
    
    actualMassEmissionTotalTRVWList = ['Actual mass of emission (Tons):'] + [0, 0, '-', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, stream25AshMass, 0, 0, 0, 0, 0, 0, 0]
    listsToAdd.append(actualMassEmissionTotalTRVWList)
    
    totalEmissionsTRVWList = ['Total Emissions', 0,0, (sum(stream4AdditiveMasses_.values())+sum(stream4ResinMasses_.values()))*0.0025+sum(stream3Emissions.values()), 0,0,0, totalStream10Waste*230*0.00110231, 0,0,0,0,0,0,0, conditions[9]*1.10231131, 0, sum(emissionStream16.values()), 0, 0, sum(stream20Emissions.values()), 0, 0, sum(stream23Emissions.values()), 0, sum(stream24Emissions.values())+1.05*sum(stream11MSWValues.values()), sum(stream27Emissions.values()), sum(stream23Emissions.values()), sum(stream29Emissions.values()), stream30Emissions, 0, 0]
    listsToAdd.append(totalEmissionsTRVWList)
    
    emissionsFromPlasticList = ['Emissions from plastic', 0,0, (sum(stream4AdditiveMasses_.values())+sum(stream4ResinMasses_.values()))*0.0025+sum(stream3Emissions.values()), 0,0,0, totalStream10Waste*230*0.00110231, 0,0,0,0,0,0,0, conditions[9]*1.10231131, 0, sum(emissionStream16.values()), 0, 0, sum(stream20Emissions.values()), 0, 0, sum(stream23Emissions.values()), 0, sum(stream24Emissions.values()),0, sum(stream27Emissions.values()), sum(stream23Emissions.values()), sum(stream29Emissions.values()), sum(stream26Emissions.values()), 0, 0]
    listsToAdd.append(emissionsFromPlasticList)
    
    
    streamTRVWLists = streamTRVWLists+listsToAdd

    
    #Changes text on user specs page to confirm calcualtions are complete
    gapLabel1.config(text = 'Calculations Complete')
    
    
    
    
    if True in chemRecyc: 
        #For additive migration:
        a=sum(stream20TotalAdditives.values()) 
        chemRecyc_addies.append(a)
      
        return
    
    #Now for sensitivity tests
    #Will create list of points to be used to generate sensitivity analysis graph and function
    if sensitivity == True: 
       #For additive migration:
        a = 2*sum(list(stream23AdditiveMasses_.values()))+sum(list(stream18AdditiveMigration.values()))
        sensitivityPoints.append(a)
        
        
        #For total greenhouse emissions in EoL:
        g = stream7TotalEmissions + wasteFacilityEmissions + sum(emissionStream16.values()) + sum(stream20Emissions.values()) + sum(stream24Emissions.values()) +  sum(stream11MSWValues.values()) + stream30Emissions + sum(stream29Emissions.values())
        ghgEmitSA.append(g)
        
        #For releases to land:
        litter = sum(matFlowUseLittering.values())+sum(matFlowCSPLittering.values())+sum(matFlowMechRecycLittering.values())+sum(matFlowIncinLitter.values())+ sum(matFlowLandLitter.values())
        litterAnal.append(litter)
        
        #For releases to water:
        water = sum(matFlowUseWater.values())+sum(matFlowCSPWater.values())+sum(matFlowMechRecycWater.values())+sum(matFlowIncinLitter.values())+sum(matFlowLandWater.values())
        waterAnal.append(water)    
        
        
        
        return
    #Creates pie chart for data analysis stream. Shows msw composition
    #PIE CHART
    plt.rcParams.update({'font.size': 18})
    piecharttest=np.array(mswCompProp)
    plasticexplode = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5] #make the plastic section wedge out from the center of the pie.
    plt.rcParams["figure.figsize"] = (10, 7) #adjusts the whitespace to show the entirety of the figure
      
      
    fig1, ax1=plt.subplots()
    ax1.pie(piecharttest, labels=typesOfWastes, explode=plasticexplode, autopct='%1.1f%%', pctdistance=0.9, labeldistance=1.05,
              shadow=True, startangle=180)
    ax1.set_title('MSW Composition', fontsize=22) #adjust the title of the figure. pad = distance from the figure
    ax1.plot(label=typesOfWastes)

    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    fig1.tight_layout()
    canvasPieChart = FigureCanvasTkAgg(fig1, master=plotFrame) # Convert the Figure to the data frame (tab)
    canvasPieChart.get_tk_widget().grid(column = 0, row = 0) # Show the widget on the screen
    #canvasPieChart.draw() # Draw the graph on the canvas   
      
      
      ### Bar Chart
      #Creates dictionary showing amount of each kind of plastic recycled, then creates list of values from that dict
    amountOfPlasticRecycled = dict(zip(typesOfPlasticDomestic, [stream16ResinMasses_[i]+stream27ResinMasses[i] for i in typesOfPlasticDomestic]))
    barData1 = list(amountOfPlasticRecycled.values())
     
      #creates list of generated plastic masses from earlier dict
    barData2 = list(plasticsMassDict.values())
      
      
      #Comparison bar graph creation
    index = np.arange(len(typesOfPlasticDomestic)) #Creates x-axis categories
    bar_width = 0.35 #width of each bar
      
    barChart, ax = plt.subplots() #defines graph
      
    barRecyc = ax.bar(index, barData1, bar_width, label = "Amount Of Plastic Recycled") #creates data one data set for graph
    barCollected = ax.bar(index+bar_width, barData2, bar_width, label = "Amount of Plastic Collected") #creates second data set for graph
      
      #Creates labels for axes and graph
    ax.set_xlabel("Type Of Plastic")
    ax.set_ylabel("Amount (tons)")
    ax.set_title("Amount of Plastic Collected and Recycled")
    ax.set_xticks(index+bar_width/2)
    ax.set_xticklabels(typesOfPlasticDomestic)
    ax.legend()
     
    
      #creates canvas for placement in GUI
    barCanvas = FigureCanvasTkAgg(barChart, master = plotFrame)
    #barCanvas.draw()
    barCanvas.get_tk_widget().grid(column = 1, row = 0)
    
    values = [streamTRVWLists[-5][6], streamTRVWLists[-4][6], 
              streamTRVWLists[-4][9], streamTRVWLists[-5][9], 
              streamTRVWLists[-5][6]+streamTRVWLists[-4][6], streamTRVWLists[-5][26]+streamTRVWLists[-4][26], 
              streamTRVWLists[-5][26], streamTRVWLists[-5][29], 
              streamTRVWLists[-4][26], streamTRVWLists[-4][29],
              streamTRVWLists[-5][27]+streamTRVWLists[-4][27], streamTRVWLists[-5][27], 
              streamTRVWLists[-4][27], streamTRVWLists[-5][24]+streamTRVWLists[-4][24], 
              streamTRVWLists[-5][24], streamTRVWLists[-4][24], 
              streamTRVWLists[-5][13]+streamTRVWLists[-4][13], streamTRVWLists[-5][16]+streamTRVWLists[-4][16],
              streamTRVWLists[-5][28]+streamTRVWLists[-4][28], streamTRVWLists[-5][23]+streamTRVWLists[-4][23], 
              streamTRVWLists[-5][20], streamTRVWLists[-4][18],
              streamTRVWLists[-5][22], streamTRVWLists[-4][21]+streamTRVWLists[-5][21], 
              streamTRVWLists[-4][19], streamTRVWLists[-4][31]+streamTRVWLists[-5][31],
              streamTRVWLists[-4][32]+streamTRVWLists[-5][32], streamTRVWLists[-4][33]+streamTRVWLists[-5][33]]
    values = [i/(values[2]+values[3]+values[4]) for i in values]
    
    stages = ['Plastic (Resin): {:.3f}'.format(values[0]), 'Chemical Additives: {:.3f}'.format(values[1]), 
              'Collection: {:.3f}'.format(values[2]+values[3]+values[4]), 'Chemical Additives Littered: {:.3f}'.format(values[2]), 
              'Plastics Littered: {:.3f}'.format(values[3]), 'Sorting: {:.3f}'.format(values[4]), 'Landfilling: {:.3f}'.format(values[5]+values[18]), 
              'Plastics Landfilled: {:.3f}'.format(values[6]), 'Chemical Additives Landfilled: {:.3f}'.format(values[8]), 
              'Plastics Released: {:.3f}'.format(values[7]), 'Chemical Additives Released: {:.2e}'.format(values[9]),
              'Export: {:.3f}'.format(values[10]), 'Plastics Exported: {:.3f}'.format(values[11]), 
              'Chemical Additives Exported: {:.2e}'.format(values[12]), 'Incineration: {:.3f}'.format(values[13]+values[19]), 
              'Plastics Incinerated: {:.3f}'.format(values[14]), 'Chemical Additives Incinerated: {:.2e}'.format(values[15]),
              'Plastic Scraps Composted: {:.2e}'.format(values[16]), 'Mechanical Recycling: {:.3f}'.format(values[17]), 
              'Plastics Import: {:.3f}'.format(values[23]), 'Chemical Additives Contaminated/Added: {:.3f}'.format(values[24]), 
              'Recycled Plastics: {:.3f}'.format(values[20]),
              'Chemical Additives Migrated: {:.2e}'.format(values[21]), 'Plastics Re-Exported: {:.2e}'.format(values[22]), 'Chemical Reprocessing: {:.3f}'.format(values[24])]

    colors = ['rgba(31, 119, 180, 0.8)', 'rgba(255, 127, 14, 0.8)', 'rgba(44, 160, 44, 0.8)', 'rgba(214, 39, 40, 0.8)', 
              'rgba(148, 103, 189, 0.8)', 'rgba(140, 86, 75, 0.8)', 'rgba(227, 119, 194, 0.8)', 'rgba(127, 127, 127, 0.8)',
              'rgba(188, 189, 34, 0.8)', 'rgba(23, 190, 207, 0.8)', 'rgba(31, 119, 180, 0.8)', 'rgba(255, 127, 14, 0.8)', 
              'rgba(44, 160, 44, 0.8)', 'rgba(214, 39, 40, 0.8)', 'rgba(148, 103, 189, 0.8)', 'rgba(140, 86, 75, 0.8)', 
              'rgba(227, 119, 194, 0.8)', 'rgba(127, 127, 127, 0.8)', 'rgba(188, 189, 34, 0.8)', 'rgba(23, 190, 207, 0.8)',
              'rgba(31, 119, 180, 0.8)', 'rgba(255, 127, 14, 0.8)', 'rgba(44, 160, 44, 0.8)', 'rgba(214, 39, 40, 0.8)',
              'rgba(31, 119, 180, 0.8)', 'rgba(255, 127, 14, 0.8)', 'rgba(44, 160, 44, 0.8)', 'rgba(214, 39, 40, 0.8)',] 
    
    sources = [0, 1, 2, 2, 2, 5, 6, 7, 6, 8,  5,  11, 11,  5, 14, 14,  5,  5, 18, 18, 18, 18, 18, 19, 20, 18, 24, 24]
    targets = [2, 2, 3, 4, 5, 6, 7, 9, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18,  6, 14, 21, 22, 23, 18, 18, 24,  6, 14]

    colors_2 = ['rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 
                'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 
                'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 
                'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 
                'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)',
                'rgba(0,0,96,0.2)', 'rgba(0,0,96,0.2)']
    
    
    data = {'data': [{'type': 'sankey', 'domain': {'x': [0, 1], 'y': [0, 1]}, 'orientation': 'h', 'valueformat': '.0f', 
                      'valuesuffix': '', 'node': {'pad': 15, 'thickness': 15, 'line': {'color': 'black', 'width': 0.5}, 
                                                     'label': stages, 'color': colors}, 
                      'link': {'source': sources, 'target': targets, 'value': values, 'color': colors_2, 
                               'label': [round(values[i]) for i in range(len(targets))]}}], 
            'layout': {'title': {'text': "Mass Flow Rates of Plastic and Additive Waste"}, 'width': 1118, 'height': 772, 
                       'font': {'size': 1000}, 'updatemenus': [{'y': 1, 'buttons': [{'label': 'Light', 'method': 'relayout', 
                                                                                   'args': ['paper_bgcolor', 'white']}, 
                                                                                  {'label': 'Dark', 'method': 'relayout', 
                                                                                   'args': ['paper_bgcolor', 'black']}]}, 
                                                             {'y': 0.9, 'buttons': [{'label': 'Thick', 'method': 'restyle', 
                                                                                     'args': ['node.thickness', 15]}, 
                                                                                    {'label': 'Thin', 'method': 'restyle',
                                                                                     'args': ['node.thickness', 8]}]}, 
                                                             {'y': 0.8, 'buttons': [{'label': 'Small gap', 'method': 'restyle', 
                                                                                     'args': ['node.pad', 15]}, 
                                                                                    {'label': 'Large gap', 'method': 'restyle', 
                                                                                     'args': ['node.pad', 20]}]}, 
                                                             {'y': 0.7, 'buttons': [{'label': 'Snap', 'method': 'restyle', 
                                                                                     'args': ['arrangement', 'snap']}, 
                                                                                    {'label': 'Perpendicular', 'method': 'restyle', 
                                                                                     'args': ['arrangement', 'perpendicular']}, 
                                                                                    {'label': 'Freeform', 'method': 'restyle', 
                                                                                     'args': ['arrangement', 'freeform']}, 
                                                                                    {'label': 'Fixed', 'method': 'restyle', 
                                                                                     'args': ['arrangement', 'fixed']}]}, 
                                                             {'y': 0.6, 'buttons': [{'label': 'Horizontal', 'method': 'restyle', 
                                                                                     'args': ['orientation', 'h']}, 
                                                                                    {'label': 'Vertical', 'method': 'restyle', 
                                                                                     'args': ['orientation', 'v']}]}]}}

    # override gray link colors with 'source' colors
    opacity = 0.4
    # change 'magenta' to its 'rgba' value to add opacity
    data['data'][0]['node']['color'] = ['rgba(255,0,255, 0.8)' if color == "magenta" else color for color in data['data'][0]['node']['color']]
    data['data'][0]['link']['color'] = [data['data'][0]['node']['color'][src].replace("0.8", str(opacity))
                                        for src in data['data'][0]['link']['source']]

    fig = go.Figure(data=[go.Sankey(
        valueformat = ".0f",
        valuesuffix = "",
        # Define nodes
        node = dict(
          pad = 15,
          thickness = 15,
          line = dict(color = "black", width = 0.5),
          label =  data['data'][0]['node']['label'],
          color =  data['data'][0]['node']['color'],
          x = [0.0, 0.0, 0.25, 0.4, 0.40, 0.4, 0.60, 0.80, 0.80, 1.00, 1.0, 0.70, 1.00, 1.00, 0.75, 1.00, 1.00, 1.0, 0.55, 0.0, 0, 1.0, 1.00, 1.00, 0.65],
          y = [0.8, 0.4, 0.50, 1.0, 0.95, 0.5, 0.45, 0.45, 0.85, 0.30, 0.8, 1.00, 0.99, 0.95, 0.01, 0.08, 0.15, 0.4, 0.85, 0.7, 0, 0.7, 0.64, 0.60, 0.95]
        ),
        # Add links
        link = dict(
          source =  data['data'][0]['link']['source'],
          target =  data['data'][0]['link']['target'],
          value =  data['data'][0]['link']['value'],
          label =  data['data'][0]['link']['label'],
          color =  data['data'][0]['link']['color']
          
    ))])

    fig.update_layout(title_text="<b>Normalized Material Flow Analysis of Plastics and Additives<b>", font_size=18)
    plot(fig, auto_open = False)
    hti = Html2Image()

    hti.screenshot(html_file='temp-plot.html', save_as='Sankey_Diagram.png')
    

    
    image = Image.open('Sankey_Diagram.png')

    new_image = image.resize((1500, 650))
    display = ImageTk.PhotoImage(new_image)
    img_label.configure( image = display)
    img_label.image = display
    
    
    figure_loops = plt.Figure(figsize=(12,10), dpi=80)
    for widgets in mat_loopTab.winfo_children():
          widgets.destroy()
    
    mL1popUpButton = Button(mat_loopTab, text = 'Show Material Loop 1 Stream Calculations', command = mL1PopUp)
    mL2popUpButton = Button(mat_loopTab, text = 'Show Material Loop 2 Stream Calculations', command = mL2PopUp)
    mL3popUpButton = Button(mat_loopTab, text = 'Show Material Loop 3 Stream Calculations', command = mL3PopUp)
    mL4popUpButton = Button(mat_loopTab, text = 'Show Material Loop 4 Stream Calculations', command = mL4PopUp)

    popUpButtonList = [mL1popUpButton, mL2popUpButton, mL3popUpButton, mL4popUpButton]

    frameRow = 1
    frameColumn = 0

    for i in popUpButtonList:
        i.pack()
    loop_scatter = FigureCanvasTkAgg(figure_loops, mat_loopTab)

    
    loop_scatter.get_tk_widget().pack()
    ax_loop = figure_loops.add_subplot(111)
    ax_loop.set_xlabel('Material Loop Number')
    ax_loop.set_ylabel('Plastic Additive Accumulation')
    ax_loop.set_title('Additive Accumulation Over Multiple Life Cycles')
    
    
    ax_loop.plot([i for i in range(5)], matLoopRecycAdditives)
    ax_loop.set_xticks([i for i in range(5)])
    #ax_loop.axis([0, 4, 0, matLoopRecycAdditives[-1]*1.2])

    
    
##################################################################
#Abstract Tab

#Adding text boxes to Frame 1 
#note: this information is no longer the abstract but the instructions
#old widget names remain though sorry bout it
abstract_frame1 = tk.Text(my_frame1, bd = 0, highlightthickness= 0, bg = "white",  height = 25, width = 90)
title_frame1 = tk.Text(my_frame1, bd = 0, highlightthickness= 0, bg = "white", height = 4, width = 50)
subtitle_frame1 = tk.Text(my_frame1, bd = 0, highlightthickness = 0, bg = "white", height = 1, width =50)

#Adding text to instructions textbox (formerly the abstract)
abstract_frame1.insert(tk.INSERT, "1. Municipal solid waste (MSW) data can be input under the “User Specifications” tab. Click on this tab, then begin\nfilling in the data in the entry boxes provided. To autofill all boxes at once, click the year at the top, then “Select.” Alternatively, you can fill each category individually.") #abstract
abstract_frame1.insert(tk.INSERT, "\n\n2. Once a set of data is input, click “Enter Above Dataset” to submit that data and move on to the next set. At any time, you may return to previously entered data sets by clicking on the appropriate category on the left. Submitting will also\ncheck the data, ensuring all proportions sum to 1 as necessary. At any time, you may check the proportions yourself by clicking “Check Proportions.” This button will NOT submit data.") #abstract
abstract_frame1.insert(tk.INSERT, "\n\n3. Once all data has been submitted, press “Calculate Streams.” If not all data has been entered, an error message\nwill appear prompting you to go back and check that every box is filled with a number. ") #abstract
abstract_frame1.insert(tk.INSERT, "\n\n4. At this point, all calculations have been completed and you may analyze the data. In the “Stream Calculations” tab, a flow chart shows the MSW lifecycle and stream numbers and titles for the processes within.") #abstract
abstract_frame1.insert(tk.INSERT, "\n\n5. On this same page, the mass calculations for each stream are generated by clicking “Show Stream Calculations.”\nThis will generate a spreadsheet of stream data in a pop-up window that can then be exported to an Excel\nspreadsheet by clicking “Export to Excel. This will send the data to an excel file called 'Stream Summary Calculations'\nthat will be generated in the same file as this program. This file must be closed when more data is added.") #abstract
abstract_frame1.insert(tk.INSERT, "\n\n6. Under the “Material Flow Results” tab, various plots are shown, and clicking “Display User Input” will show the data\nvalues input by the user.") #abstract
abstract_frame1.insert(tk.INSERT, "\n\n7. The “LCI” tab shows a lifecycle inventory, giving information about each plastic resin and a lump category of plastic additives in each major step of the plastic lifecycle.") #abstract



#Add text to title
title_frame1.insert(tk.INSERT, "\nA Generic Scenario Analysis of End-of-Life Plastic\nManagement: Chemical Additives") #title for frame

#Configure title text boxes, fonts, etc.
title_frame1.tag_configure("center", justify = 'center') 
title_frame1.tag_add("center", 1.0, 'end')
title_frame1.configure(font = ("Helvetica", 24, "bold"))
subtitle_frame1.insert(tk.INSERT, "Instructions")
subtitle_frame1.tag_configure("center", justify = "center")
subtitle_frame1.tag_add("center", 1.0, 'end')
subtitle_frame1.configure(font = ("Helvetica 20 bold"))
abstract_frame1.configure(font = ("Helvetica 14"))

#disables editing of text boxes
title_frame1.config(state="disabled")
subtitle_frame1.config(state="disabled")
abstract_frame1.config(state="disabled")

#places text boxes on screen
title_frame1.pack()
subtitle_frame1.pack()
abstract_frame1.pack()


########################################################################
#LCI Tab

#Create and place canvas inside my_frame5 so that a scrollbar can be added
#Note: material flow is name carried over from older versions. This is all part of LCI Tab
#note2: material flow is an old name. this now refers to LCI, but names have been preserved
materialFlowCanvas = Canvas(my_frame5, bg = 'white')
materialFlowCanvas.pack(side = LEFT, fill = BOTH, expand = 1)

#Create and configure scrollbar
matFlowScrollbar = Scrollbar(my_frame5, orient = 'vertical', command = materialFlowCanvas.yview)
matFlowScrollbar.pack(side = 'right', fill = 'y')
matFlowScrollbar.config(command=materialFlowCanvas.yview)
materialFlowCanvas.configure(yscrollcommand=matFlowScrollbar.set)
materialFlowCanvas.bind('<Configure>', lambda e: materialFlowCanvas.configure(scrollregion = materialFlowCanvas.bbox('all')))


#Creates frame for tables that will show life cycle inventory tables and places inside canvas
materialFlowFrame = Frame(materialFlowCanvas, bg = 'white')
materialFlowCanvas.create_window((0,0), window = materialFlowFrame, anchor = 'nw')


#Creates and configures title and subtitle for LCI Frame
fontChoice = 'Helvetica 12 bold'
materialFlowTitle = tk.Text(materialFlowFrame, bd = 0, highlightthickness = 0, bg = 'white', height = 2, width = 50)
materialFlowTitle.insert(tk.INSERT, "\nLife Cycle Inventory")
materialFlowTitle.tag_configure("center", justify = 'center') 
materialFlowTitle.tag_add("center", 1.0, 'end')
materialFlowTitle.configure(font = ("Helvetica 20 bold"))
materialFlowTitle.config(state = 'disabled')

materialFlowSubtitle = tk.Text(materialFlowFrame, bd = 0, highlightthickness = 0, bg = 'white', height = 1, width = 75)
materialFlowSubtitle.insert(tk.INSERT, 'Select year or custom in "User Specifications" tab to populate table.')
materialFlowSubtitle.tag_configure("center", justify = 'center') 
materialFlowSubtitle.tag_add("center", 1.0, 'end')
materialFlowSubtitle.configure(font = ("Helvetica 16 bold"))
materialFlowSubtitle.config(state = 'disabled')

#places title and subtitle
materialFlowTitle.pack()
materialFlowSubtitle.pack()


#Creates  tables (TRVWs) that will contain LCI information
matFlowManufactureTRVW = ttk.Treeview(materialFlowFrame)
matFlowUseTRVW = ttk.Treeview(materialFlowFrame)
matFlowCSPTRVW = ttk.Treeview(materialFlowFrame)
matFlowMechRecycTRVW = ttk.Treeview(materialFlowFrame)
matFlowIncinTRVW = ttk.Treeview(materialFlowFrame)
matFlowLandTRVW = ttk.Treeview(materialFlowFrame)

#Creates title for each TRVW
matFlowManufactureText = Text(materialFlowFrame, bd=0, highlightthickness = 0, bg = "white", height = 3, width = 125)
matFlowUseText = Text(materialFlowFrame, bd=0, highlightthickness = 0, bg = "white", height = 3, width = 125)
matFlowCSPText = Text(materialFlowFrame, bd=0, highlightthickness = 0, bg = "white", height = 3, width = 125)
matFlowMechRecycText = Text(materialFlowFrame, bd=0, highlightthickness = 0, bg = "white", height = 3, width = 125)
matFlowIncinText = Text(materialFlowFrame, bd=0, highlightthickness = 0, bg = "white", height = 3, width = 125)
matFlowLandText = Text(materialFlowFrame, bd=0, highlightthickness = 0, bg = "white", height = 3, width = 125)

#Creates lists of rows to be added to each LCI table
matFlowColumnHeadings = ('Materials', 'Input (ton/total ton input)', 'Output (ton/total ton input)', 'Releases to Land (ton/total ton input)', 'Releases to Air (ton/total ton input)', 'Releases to Water (ton/total ton input)', 'Inhalation Exposure (Tons/total ton input)', 'Dermal Exposure (Tons/total ton input)', 'Greenhouse Gas Emissions (Tons CO2-eq/ton input)')
matFlowCategories = ['\nManufacture', "\nUse", '\nCollection and Sorting', '\nMechanical Recycling', '\nIncineration', '\nLandfill']
matFlowTRVWList = [matFlowManufactureText, matFlowManufactureTRVW, matFlowUseText, matFlowUseTRVW, matFlowCSPText, matFlowCSPTRVW, matFlowMechRecycText, 
                   matFlowMechRecycTRVW, matFlowIncinText, matFlowIncinTRVW, matFlowLandText, matFlowLandTRVW]



for i in range(len(matFlowTRVWList)):
    if i%2 == 1:
        matFlowTRVWList[i]['columns'] = matFlowColumnHeadings #adds headers to tables and packs
        matFlowTRVWList[i].column('#0', width = 0, stretch = NO)
        for name in matFlowColumnHeadings:
            matFlowTRVWList[i].heading(name, text = name)
        matFlowTRVWList[i].pack(fill = BOTH)
    if i%2 ==0:
        matFlowTRVWList[i].insert(tk.INSERT, matFlowCategories[i//2]) #adds in between titles for each trvw
        matFlowTRVWList[i].tag_configure("center", justify = 'center')
        matFlowTRVWList[i].tag_add("center", 1.0, 'end')
        matFlowTRVWList[i].configure(font = ("Helvetica 16 bold"))
        matFlowTRVWList[i].config(state="disabled")
        matFlowTRVWList[i].pack()
    
def fillMatFlowAnalSumTRVW(): #will be used to fill each LCI trvw table
    
    try:
        manufactureList = trvwListMaker(manufactureDictList) #in case of error won't crash code
    except: 
        return
    
    #creates list for each trvw and its row
    useList = trvwListMaker(useDictList)
    cspList = trvwListMaker(cspDictList)
    mechRecycList = trvwListMaker(mechRecycDictList)
    incinList = trvwListMaker(incinDictList)
    landList = trvwListMaker(landDictList)
    count = 0
    
    #inserts above data into trvw tables
    for record in manufactureList:
        matFlowManufactureTRVW.insert(parent ='', index ='end', iid = count, text = '', values = (record[0], record[1], record[2], record[3], record[4], record[5], record[6]))
        count +=1
    
    count = 0
    for record in useList:
        matFlowUseTRVW.insert(parent ='', index ='end', iid = count, text = '', values = (record[0], record[1], record[2], record[3], record[4], record[5], record[6]))
        count +=1
        
    count = 0
    for record in cspList:
        matFlowCSPTRVW.insert(parent ='', index ='end', iid = count, text = '', values = (record[0], record[1], record[2], record[3], record[4], record[5], record[6]))
        count +=1
        
    count = 0
    for record in mechRecycList:
        matFlowMechRecycTRVW.insert(parent ='', index ='end', iid = count, text = '', values = (record[0], record[1], record[2], record[3], record[4], record[5], record[6]))
        count +=1    
        
    count = 0
    for record in incinList:
        matFlowIncinTRVW.insert(parent ='', index ='end', iid = count, text = '', values = (record[0], record[1], record[2], record[3], record[4], record[5], record[6]))
        count +=1    
        
    count = 0
    for record in landList:
        matFlowLandTRVW.insert(parent ='', index ='end', iid = count, text = '', values = (record[0], record[1], record[2], record[3], record[4], record[5], record[6]))
        count +=1    
        
        
        
        
###################################################
### Entries tab


#makes sure that all proportions sum to within 1% of appropriate total. works for every category but conditions
def checkProportions(listOfEntries, finalSum):
    g = 0
    for i in listOfEntries:
        try:
            g += float(i.get()) #makes sure input is numbers only
        except:
            gapLabel1.config(text = 'Error: Please enter a number into each box to continue.', fg = 'red')
            return
    if  0.99*finalSum<g<1.01*finalSum: #checks to be within 1%
        gapLabel1.config(text = 'Check successful.') #indicates success
        return True
    else:
        gapLabel1.config(text = 'Proportions do not sum to 1.', fg = 'red') #indicates failure
        return False

#Above check function does not work for conditions category, so this function is used instead
def conditionsCheckProp(): 
    g = 0 
    for i in conditionsPropCheckList:
        try: #makes sure input is numbers only
            g += float(i.get())
        except:
            gapLabel1.config(text = 'Error: Please enter a number into each box to continue.')
            return
    
    h = 0
    for b in conditionsPropCheckList2:
        h+= float(b.get())
    
    standard = float(plasticRecycledPropEntry.get())  #ensures plastic recycled domestically and exported sum to total recycled
    if 99<g<101: #makes sure total waste proportions (incinerated, landfilled, recycled) sum to 100
        if 0.99*standard<h<1.01*standard:
            gapLabel1.config(text = 'Check successful.')
            return True
        else:
            gapLabel1.config(text = 'Domestic and exported recycling do not sum to total recycled Fraction.') #for if
            gapLabel1.config(fg = 'red')
    else: 
        if 0.99*standard<h<1.01*standard:
            gapLabel1.config(fg = 'red')
            gapLabel1.config(text = "Plastic recycled proportion, landfill proportion, and incineration proportion do not sum to 1.")
        else:
            gapLabel1.config(text = "Plastic recycled proportion, landfill proportion, and incineration proportion do not sum to 1. Domestic and exported recycling do not sum to total recycled Fraction.")
            gapLabel1.config(fg = 'red')
            
    return False

#Packs canvas that will have data input section on it. Canvas allows for scroll bar to be added if necessary
userSpecificationsCanvas.pack(side = LEFT, fill = BOTH, expand = 1)
userSpecificationsCanvas.create_window((0,0), window = my_frame2, anchor = 'nw')


#Creates and configures title/subtitle for user specs tab
#Text to frame 2
title_frame2 = tk.Text(my_frame2, bd=0, highlightthickness = 0, bg = "white", height=1, width=125)
title_frame2.insert(tk.INSERT,"User Specifications")
title_frame2.tag_configure("center", justify = 'center')
title_frame2.tag_add("center", 1.0, 'end')
title_frame2.configure(font = ("Helvetica 16 bold"))
title_frame2.config(state="disabled")
title_frame2.grid(column=0,row=0,columnspan=3)

subtitle_frame2 = tk.Text(my_frame2, bd=0, highlightthickness = 0, bg = "white", height=2, width = 75)
subtitle_frame2.insert(tk.INSERT,"Please select the simulated year for default MSW composition.\nYou may adjust these values accordingly.") #" #Note: Please fill all boxes, entering 0 where applicable.")
subtitle_frame2.configure(font = ("Helvetica 10 bold"))
subtitle_frame2.tag_configure("center", justify="center")
subtitle_frame2.tag_add('center', 1.0, 'end')
subtitle_frame2.config(state="disabled")
subtitle_frame2.grid(column =0, row=1, columnspan=3)



# Dictionary to create multiple radio buttons
values = {"2018" : "2018",
          "Custom" : "Custom",
          "Show Basic": "Show Basic",
          "Show Full": "Show Full"}

#Variable for those radio buttons
selectYear = StringVar()

 
# Loop is used to create multiple RadiobutTons
# rather than creating each button separately
fontChoice = 'Helvetica 9 bold' #Assign font choices

frame2Row = 2
#create radiobuttons and grid them
for (text, value) in values.items():
    Radiobutton(my_frame2, text = text, variable = selectYear,
                value = value, indicator = 0,
                background = "gray81", font = fontChoice).grid(column = 0, row = frame2Row, columnspan=3, sticky=EW, ipady=5)
    frame2Row +=1
    
#Creates functions associated with radio buttons that will auto fill the entry boxes on the input tab
def select2018():
    for i in customEntryList:
        for b in i:
            if b!= innerGap15 and b != innerGap16 and b!= innerGap17:
                b.delete(0, END)
            
#Inserts values into data entry boxes. Will round to three decimal places as long as the number is >0.01
    for i in range(len(typesOfWasteEntry)):
        if mswCompProp2018[i] > 0.01:
            typesOfWasteEntry[i].insert(END, round(mswCompProp2018[i],3))
        else:
            typesOfWasteEntry[i].insert(END, mswCompProp2018[i])

    for i in range(len(conditionsentryList)):
        if conditions2018[i] > 0.01:
            conditionsentryList[i].insert(END, round(conditions2018[i],3) )
        else:
            conditionsentryList[i].insert(END, conditions2018[i])
            
    for i in range(11):
        if mswIncin2018[i] > 0.01:
            IncinMSWPropsEntry[i].insert(END, round(mswIncin2018[i],3))
        else:
            IncinMSWPropsEntry[i].insert(END, mswIncin2018[i])
            
    for i in range(11):
        if mswRecyc2018[i] > 0.01:
            recycMSWPropsEntry[i].insert(END, round(mswRecyc2018[i],3))
        else:
            recycMSWPropsEntry[i].insert(END, mswRecyc2018[i])
            
    for i in range(11):
        if mswLand2018[i] > 0.01:
            LandMSWPropsEntry[i].insert(END, round(mswLand2018[i], 3))
        else:
            LandMSWPropsEntry[i].insert(END, mswLand2018[i])
            
    for i in range(11):
        if mswCompost2018[i] > 0.01:
            CompostMSWPropsEntry[i].insert(END, round(mswCompost2018[i],3))
        else: 
            CompostMSWPropsEntry[i].insert(END, mswCompost2018[i])

    for i in range(8):
        if plasticRecycledFractionsList2018[i] > 0.01:
            recycPlasticEntry[i].insert(END, round(plasticRecycledFractionsList2018[i], 3)) 
        else: 
            recycPlasticEntry[i].insert(END, plasticRecycledFractionsList2018[i]) 

    for i in range(8):
        if plasticLandFractionsList2018[i] > 0.01:
            LandPlasticEntry[i].insert(END, round(plasticLandFractionsList2018[i], 3))
        else: 
            LandPlasticEntry[i].insert(END, plasticLandFractionsList2018[i])

    for i in range(8):
        if plasticIncinFractionsList2018[i] > 0.01:
            IncinPlasticEntry[i].insert(END, round(plasticIncinFractionsList2018[i], 3))
        else: 
            IncinPlasticEntry[i].insert(END, plasticIncinFractionsList2018[i])

    for i in range(8):
        if repRecPlastics2018[i] > 0.01:
            RepRecycPlasticEntry[i].insert(END, round(repRecPlastics2018[i], 3))
        else: 
            RepRecycPlasticEntry[i].insert(END, repRecPlastics2018[i])

    for i in range(4):
        if repPlasticImport2018[i] > 0.01:
            ImportPlasticEntry[i].insert(END, round(repPlasticImport2018[i], 3))
        else: 
            ImportPlasticEntry[i].insert(END, repPlasticImport2018[i])

    for i in range(4):
        if repPlasticsExport2018[i] > 0.01:
            ExportPlasticEntry[i].insert(END, round(repPlasticsExport2018[i], 3))
        else: 
            ExportPlasticEntry[i].insert(END, repPlasticsExport2018[i])

    for i in range(4):
        if repPlasticsReExport2018[i] > 0.01:
            ReExportPlasticEntry[i].insert(END, round(repPlasticsReExport2018[i], 3))
        else: 
            ReExportPlasticEntry[i].insert(END, repPlasticsReExport2018[i])
    
    for i in range(3):
        chemRecycEntries[i].insert(END, 0)
    
#When custom is selected via radio button, the entry boxes will be cleared
def selectCustom():
    for i in customEntryList:
        for b in i:
            if b!= innerGap15 and b != innerGap16 and b!= innerGap17:
                b.delete(0, END)

def showBasic():
    select2018()
    
    for i in customEntryList:
        for b in i:
            if b!= innerGap15 and b != innerGap16 and b!= innerGap17:
               b.grid_remove()
    for i in customLabelsList:
        for b in i:
            b.grid_remove()
    for i in checkButtonList:
        i.grid_remove()
    for i in extraButTonsList:
        i.grid_remove()
    for i in showButtonLists:
        i.grid_remove()
    calculateButton.grid_remove()
    basicListLabels = [plasticDomesticLabel, plasticIncineratedPropLabel, plasticLandfillPropLabel]
    
    basicEntryLabels = [plasticDomesticEntry, plasticIncineratedPropEntry, plasticLandfillPropEntry]
    
    frameRow = 13
    for i in range(len(basicListLabels)): 
        basicListLabels[i].grid(column = 1, row = frameRow, sticky = E)
        basicEntryLabels[i].grid(column = 2, row = frameRow, sticky = W)
        frameRow += 1
        
    for i in basicEntryLabels:
        i.delete(0, END)
    basicCalcButton.grid(column=1, row=frameRow, columnspan = 2)


def basicCalculations():
    assignValues()
    domRecycProp = float(plasticDomesticEntry.get())
    incinProp = float(plasticIncineratedPropEntry.get())
    landProp = float(plasticLandfillPropEntry.get())
    conditions = [292_360_000.0, 0.0456706+domRecycProp, domRecycProp, 0.6670, 0.0456706, 0.0002, incinProp, landProp, 109_000_000, 630_000_000] #B2:B10
    makeCalculations(False, [False])
    fillMatFlowAnalSumTRVW()

basicCalcButton = Button(my_frame2, text = 'Make Calculations (Basic)', command = basicCalculations)
ToolTip(basicCalcButton, msg = 'Hover info')

def showFull():
    selectCustom()
    conditionsLabelsListForPlacement[0].grid(column = 1, row = 11, columnspan = 2)
    gapLabel1.grid(column = 2, row = 12, sticky = W)
    gapLabel3.grid(column = 1, row = 12, sticky = E)
    frameRow = 13
    for i in range(len(conditionsLabelsListForPlacement)-1):
        conditionsLabelsListForPlacement[i+1].grid(column = 1, row = frameRow, sticky = E)
        conditionsEntryListForPlacement[i].grid(column = 2, row = frameRow, sticky = W)
        frameRow+=1
    gapLabel2.grid(column = 1, row = frameRow, columnspan = 2)
    frameRow +=1
    conditionsButtonChecker.grid(column = 1, row = frameRow, columnspan = 2)
    frameRow +=1
    conditionsAutoButton.grid(column = 1, row = frameRow, columnspan = 2)
    frameRow +=1
    conditionsEnterButton.grid(column = 1, row = frameRow, columnspan = 2)
    frameRow +=1
    calculateButton.grid(column=1, row=frameRow, columnspan = 2)
    frameRow +=1
    conditions_help.grid(column = 1, row = frameRow, columnspan = 2)

    frameRow =11
    #loop that places these buttons
    for i in showButtonLists:
        i.grid(column = 0, row = frameRow, sticky = EW)
        frameRow +=1
        
    basicCalcButton.grid_remove()
#When enter button below will autofill data appropriately
def clicked(value):
    totalMSWEntry.delete(0, END)
    for i in range(10):
        typesOfWasteEntry[i].delete(0,END) #Clears entry boxes
    if value == "2018":
        select2018()
    if value == 'Custom':
        selectCustom()
    if value == 'Show Basic':
        showBasic()
    if value == "Show Full":
        showFull()
    
#Create button to set year and autofill data
myButtonyear = Button(my_frame2, bg =  "grey", text="Select", fg = 'white', font = fontChoice, command=lambda: clicked(selectYear.get()))
myButtonyear.grid(column=0, row=8, columnspan=3, sticky=EW, ipady=5)

#Is currently a programmer's shortcut to take all values in entry boxes. This will be removed before distribution, forcing user to enter each individual category of data 
def assignValues():
    enter(typesOfWasteEntry, mswCompProp, recycMSWPropsLabels, recycMSWPropsEntry, recycMSWButtonChecker, recycMSWAutoButton, recycMSWEnterButton)    
    enter(conditionsentryList, conditions, typesOfWasteLabels, typesOfWasteEntry, mswCompButtonCheck, mswCompAuto, mswCompEnter)    
    enter(IncinMSWPropsEntry, mswIncin, LandMSWPropsLabels, LandMSWPropsEntry, landMSWButtonChecker, landMSWAutoButton, landMSWEnterButton)
    enter(recycMSWPropsEntry, mswRecyc, IncinMSWPropsLabels, IncinMSWPropsEntry, incinMSWButtonChecker, incinMSWAutoButton, incinMSWEnterButton)
    enter(LandMSWPropsEntry, mswLand, CompostMSWPropsLabels, CompostMSWPropsEntry, compostMSWCheckerButton, compostMSWAutoButton, compostMSWEnterButton)
    enter(CompostMSWPropsEntry, mswCompost, recycPlasticLabels, recycPlasticEntry, plasticRecycButtonChecker, plasticRecycAutoButton, plasticRecycEnterButton)
    enter(recycPlasticEntry, plasticRecycledFractionsList, IncinPlasticLabels, IncinPlasticEntry, plasticIncinButtonChecker, plasticIncinAutoButton, plasticIncinEnterButton)
    enter(IncinPlasticEntry, plasticIncinFractionsList, LandPlasticLabels, LandPlasticEntry, plasticLandButtonChecker, plasticLandAutoButton, plasticLandEnterButton)    
    enter(LandPlasticEntry, plasticLandFractionsList, RepRecycPlasticLabels, RepRecycPlasticEntry, NONE, plasticRepRecycAutoButton, plasticRepRecycEnterButton)
    enter(RepRecycPlasticEntry, repRecPlastics, ImportPlasticLabels, ImportPlasticEntry, NONE, plasticImportAutoButton, plasticImportEnterButton)
    enter(ImportPlasticEntry, repPlasticImport, ExportPlasticLabels, ExportPlasticEntry, NONE, plasticExportAutoButton, plasticExportEnterButton)
    enter(ExportPlasticEntry, repPlasticsExport, ReExportPlasticLabels, ReExportPlasticEntry, NONE, plasticReExportAutoButton, plasticReExportEnterButton)
    enter(ReExportPlasticEntry, repPlasticsReExport, chemRecycLabels, chemRecycEntries, chemRecycCheckButton, chemRecycAutoButton, chemRecycEnterButton)
    enter(chemRecycEntries, chemRecycData, conditionsLabelsListForPlacement, conditionsEntryListForPlacement, conditionsButtonChecker, conditionsAutoButton, conditionsEnterButton)
#will enter data currently shown on screen
def enter(entry, appList, nextLabel, nextEntry, nextCheck, nextAuto, nextEnter):
    value = 0
    appList.clear()
    for i in entry:
        
        try:
            value = float(i.get()) #in case user doesn't enter a number
        except:
            gapLabel1.config(text = 'Error, please enter a number in each box.')
            return
        
        
        
        if entry in percent_except_0: #this will create list that can be checked later on for correct proportions
            newList = [entry[i] for i in range(1, len(entry))]
        elif entry in total_percent:
            newList = entry
        else:
            newList = entry
        #Below is condition that will subject data to checks unless it is a set that doesn't need to be checked
        if entry in total_percent:
            if checkProportions(newList, 100):
                appList.append(value/100) #if check is successful, will append data
            else:
                checkProportions(newList, 100) #if check is unsuccessful, will give error message
                return
        elif entry in percent_except_0:
              if checkProportions(newList, 100):
                  if entry.index(i) ==0:
                      appList.append(value)
                  else:
                      appList.append(value/100) #if check is successful, will append data
              else:
                  checkProportions(newList, 100) #if check is unsuccessful, will give error message
                  return
                
        elif entry == conditionsentryList: #will complete conditions check if conditions category is shown
            if conditionsCheckProp():
                if i == conditionsentryList[0] or i == conditionsentryList[8] or i == conditionsentryList[9]:
                    appList.append(value)
                else:
                    appList.append(value/100)
            else:
                conditionsCheckProp()
                return
        elif entry == chemRecycEntries:
            if checkChemRecyc():
                appList.append(value/100)
            else:
                checkChemRecyc()
                return
        else:
            appList.append(value) #if data doesn't need to be checked, data will be automatically appended

    gapLabel1.config(text = 'Previous data Entered') #will give confirmation message to user that data has been entered
    
        
#autofills data for each category as necessary
def autofill(entry, data):
    for i in range(len(entry)):
        entry[i].delete(0, END)
        entry[i].insert(0, round(data[i],3))

def help_popup(title, text): #creates pop up menu for help- to explain the different 
    
    #Creates pop up window with title
   con_top= Toplevel(streamFrame, bg = 'white')
   con_top.geometry('%dx%d+%d+%d' % (600, 500, x, y-25))
   con_top.title("Help - {:}".format(title))
   con_title = tk.Text(con_top, bd=0, highlightthickness = 0, bg = "white", height=1, width=50)
   con_title.insert(tk.INSERT,"Help - {:}".format(title))
   con_title.tag_configure("center", justify = 'center')
   con_title.tag_add("center", 1.0, 'end')
   con_title.configure(font = ("Helvetica 16 bold"))
   con_title.config(state="disabled")
   con_title.grid(column=0,row=0)


   con_body = tk.Text(con_top, bd=0, highlightthickness = 0, bg = "white", height=50, width=60)
   con_body.insert(tk.INSERT, text)
   con_body.configure(font = ("Helvetica 12"))
   con_body.config(state="disabled")   
   con_body.grid(column = 0, row = 1)


help_text = ['Total MSW: Enter the total mass of municipal solid waste\n\nTotal Plastic Recycled: Enter the total percentage of plastic recycled, including domestic and export\n\nPlastic Incinerated: Enter the percentage of plastic that is incinerated\n\nPlastic landfilled: Enter the total percentage of plastic that is landfilled\n\nPlastic Recycled Domestically: Enter the percentage of total plastic that is\nrecycled domestically\n\nPlastic Export Percent: Enter the percentage of total plastic that is exported for recycling (e.g. if 8% of total plastic is recycled in total between domestic and\nexports and 5% of plastic is recycled domestically, enter 8 in total, 5 in\ndomestic and 3 in export)\n\nPlastic Re-Export: Enter the percentage of plastic that is re-exported after\nhaving been imported for domestic recycling\n\nPlastic recycling efficiency: Enter the efficiency as a percent. The remainder\nwill be split evenly between incineration and landfilling (e.g. with a 66.7%\nefficiency, 16.65% of plastic recycled will go to each of incineration and\nlandfill',
             'Enter the make-up of municipal solid waste by percent.\n\nExamples:\n\nMisc. Inorganic Waste: soil, bits of concreate, stones\n\nOther: waste that does not comply with other categories\n\nYard trimmings: lawn clippings\n\nFood: meat, eggs, produce\n\nRubber, Leather, Textiles: rubber gloves, leather clothing, fabric\n\nWood: wooden boxes, branches\n\nMetals: aluminum cans, electronic appliances\n\nGlass: glass bottles, windows\n\nPaper and paperboard: newspaper, paper, cardboard boxes\n\nPlastics: plastic bottles, packaging plastics', 'Total Recycled Mass: Enter the total mass of municipal solid waste that is\nrecycled\n\nEnter make-up of MSW recyclate using percentages in each category (see\nMSW composition for examples of each waste category)', 'Total Incinerated Mass: Enter the total mass of municipal solid waste that is\nincinerated\n\nEnter make-up of MSW incinerate using percentages in each category (see\nMSW composition for examples of each waste category)', 'Total Landfilled Mass: Enter the total mass of municipal solid waste that is\nlandfilled\n\nEnter make-up of MSW landfilling using percentages in each category (see\nMSW composition for examples of each waste category)',
             'Total Composted Mass: Enter the total mass of municipal solid waste that is\ncomposted\n\nEnter make-up of MSW compost using percentages in each category (see\nMSW composition for examples of each waste category)', 'Enter make up of plastic recyclate by entering percentage in each resin type.\n\nPET: Polyethylene terephthalate (#1)\n\nHDPE: High-density polyethylene (#2)\n\nPVC: Polyvinyl Chloride (#3)\n\nLDPE: Low-density polyethylene (#4)\n\nPLA: Polylactic acid (#7, other)\n\nPP: Polypropylene (#5)\n\nPS: Polystyrene (#6)\n\nOther Plastics: Other resins (#7)', 'Enter make up of plastic incinerate by entering percentage in each resin type.\n\nPET: Polyethylene terephthalate (#1)\n\nHDPE: High-density polyethylene (#2)\n\nPVC: Polyvinyl Chloride (#3)\n\nLDPE: Low-density polyethylene (#4)\n\nPLA: Polylactic acid (#7, other)\n\nPP: Polypropylene (#5)\n\nPS: Polystyrene (#6)\n\nOther Plastics: Other resins (#7)', 'Enter make up of plastic landfilling by entering percentage in each resin type.\n\nPET: Polyethylene terephthalate (#1)\n\nHDPE: High-density polyethylene (#2)\n\nPVC: Polyvinyl Chloride (#3)\n\nLDPE: Low-density polyethylene (#4)\n\nPLA: Polylactic acid (#7, other)\n\nPP: Polypropylene (#5)\n\nPS: Polystyrene (#6)\n\nOther Plastics: Other resins (#7)',
             'Enter reported tons of each resin type (comes from EPA Municipal Solid\nWaste Report: This will be used for overall resin proportions to match the mass flow rate specified in Conditions tab.', 'Enter mass of each resin type imported.\n\nEthylene: Assumed to be split evenly between HDPE and LDPE\n\nVinyl Chloride: PVC\n\nStyrene: Polystyrene\n\nOther: 40% Polyethylene Terephthalate, 60% Other Resin', 'Enter mass of each resin type exported.\n\nEthylene: Assumed to be split evenly between HDPE and LDPE\n\nVinyl Chloride: PVC\n\nStyrene: Polystyrene\n\nOther: 40% Polyethylene Terephthalate, 60% Other Resin', 'Enter mass of each resin type re-exported.\n\nEthylene: Assumed to be split evenly between HDPE and LDPE\n\nVinyl Chloride: PVC\n\nStyrene: Polystyrene\n\nOther: 40% Polyethylene Terephthalate, 60% Other Resin', 'Enter percentage of plastic that is chemically reprocessed \n\nPercent of chemical recycling sent to landfill: Enter percent of chemical\nrecyclate sent to landfill\n\nPercent of chemical recycling sent to incineration: Enter percent of chemical\nrecyclate sent to incineration(e.g. if 30% of plastic is recycled and 50% is\nchemically reprocessed, 15% of the overall plastic mass will be chemically\nreprocessed. If 20% of chemical reprocessing is sent to landfill and 20% is sent to\nincineration, 3% of the overall plastic mass will be sent from chemical recycling\nto each of landfill and incineration']

#section subtitle
mswLabel = Label(my_frame2, bg = 'white', text = "Municipal Solid Waste Composition in the United States", font = 'Helvetica 12 bold')

#Creating labels for types of waste to go next to entry boxes MJC
miscInOrgWasteLabel = Label(my_frame2, text = "Misc. Inorganic Waste (Percent): ", font = fontChoice, bg="white")
otherWasteLabel = Label(my_frame2, text = "Other (Percent): ", font = fontChoice, bg="white")
yardTrimmingsLabel = Label(my_frame2, text = "Yard Trimmings (Percent): ", font = fontChoice, bg="white")
foodWasteLabel = Label(my_frame2, text = "Food (Percent): ", font = fontChoice, bg="white")
rltWasteLabel = Label(my_frame2, text = "Rubber, Leather, Textiles (Percent): ", font = fontChoice, bg="white")
woodWasteLabel = Label(my_frame2, text = "Wood (Percent): ", font = fontChoice, bg="white")
metalsWasteLabel = Label(my_frame2, text = "Metals (Percent): ", font = fontChoice, bg="white")
glassWasteLabel = Label(my_frame2, text = "Glass (Percent): ", font = fontChoice, bg="white")
paperAndBoardLabel = Label(my_frame2, text = "Paper and Paperboard (Percent): ", font = fontChoice, bg="white")
plasticsLabel = Label(my_frame2, text = "Plastics (Percent): ", font = fontChoice, bg="white")


#Creating list of labels MJC
typesOfWasteLabels = [mswLabel, miscInOrgWasteLabel, otherWasteLabel, yardTrimmingsLabel, foodWasteLabel, rltWasteLabel, woodWasteLabel, metalsWasteLabel, glassWasteLabel, paperAndBoardLabel, plasticsLabel]

#Entry boxes for custom waste stream creation MJC
miscInOrgWasteEntry = Entry(my_frame2, width=50)
otherWasteEntry = Entry(my_frame2, width=50)
yardTrimmingsEntry = Entry(my_frame2, width=50)
foodWasteEntry = Entry(my_frame2, width=50)
rltWasteEntry = Entry(my_frame2, width=50)
woodWasteEntry = Entry(my_frame2, width=50)
metalsWasteEntry = Entry(my_frame2, width=50)
glassWasteEntry = Entry(my_frame2, width=50)
paperAndBoardEntry = Entry(my_frame2, width=50)
plasticsEntry = Entry(my_frame2, width=50)


#Creates buttons using check, enter, and autofill functions
mswCompButtonCheck = Button(my_frame2, text = ' Check Proportions ', command = lambda:checkProportions(typesOfWasteEntry, 1))
mswCompEnter = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(typesOfWasteEntry, mswCompProp, recycMSWPropsLabels, recycMSWPropsEntry, recycMSWButtonChecker, recycMSWAutoButton, recycMSWEnterButton))
mswCompAuto = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(typesOfWasteEntry, mswCompProp2018))
mswComp_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('MSW Composition', help_text[1]))
#Create list of entry boxes to be placed MJC
typesOfWasteEntry = [miscInOrgWasteEntry, otherWasteEntry, yardTrimmingsEntry, foodWasteEntry, rltWasteEntry, woodWasteEntry, metalsWasteEntry, glassWasteEntry, paperAndBoardEntry, plasticsEntry]
 

#Creates conditions labels and entries
conditionsTitleLabel = Label(my_frame2, text = "Conditions", bg = 'white', font = 'Helvetica 12 bold')
totalMSWLabel = Label(my_frame2, text = 'Total MSW (Tons):', bg = 'white', font = fontChoice)
plasticRecycledPropLabel = Label(my_frame2, text = 'Total Plastic Recycled (Percent, Domestic and Export):', bg = 'white', font = fontChoice)
plasticDomesticLabel = Label(my_frame2, text = 'Plastic Recycled Domestically (Percent):', bg = 'white', font = fontChoice)
plasticRecycEfficiencyLabel = Label(my_frame2, text = 'Plastic Recycling Efficiency (Percent):', bg = 'white', font = fontChoice)
plasticExportPropLabel = Label(my_frame2, text = 'Plastic Export Percent (Percent):', bg = 'white', font = fontChoice)
plasticReExportPropLabel = Label(my_frame2, text = "Plastic Re-Export (Percent):", bg = 'white', font = fontChoice)
plasticIncineratedPropLabel = Label(my_frame2, text = 'Plastic Incinerated (Percent):', bg = 'white', font = fontChoice)
plasticLandfillPropLabel = Label(my_frame2, text = "Plastic Landfilled (Percent):", bg = 'white', font = fontChoice)
wasteFacilityEmissionsLabel = Label(my_frame2, text = 'Waste Facility Emissions (Tons):', bg = 'white', font = fontChoice)
landfillEmissionsLabel = Label(my_frame2, text = 'Emissions from Landfill (Tons):', bg = 'white', font = fontChoice)

totalMSWEntry = Entry(my_frame2, width = 50)
plasticRecycledPropEntry = Entry(my_frame2, width = 50)
plasticDomesticEntry = Entry(my_frame2, width = 50)
plasticRecycEfficiencyEntry = Entry(my_frame2, width = 50)
plasticExportPropEntry = Entry(my_frame2, width = 50)
plasticReExportPropEntry = Entry(my_frame2, width = 50)
plasticIncineratedPropEntry = Entry(my_frame2, width = 50)
plasticLandfillPropEntry = Entry(my_frame2, width = 50)
wasteFacilityEmissionsEntry = Entry(my_frame2, width = 50)
landfillEmissionsEntry = Entry(my_frame2, width = 50)

innerGap15 = Label(my_frame2, bg = 'white')
innerGap16 = Label(my_frame2, bg = 'white')
innerGap17 = Label(my_frame2, bg = 'white')

#creates lists of widgets for placement
conditionsLabelsListForPlacement = [conditionsTitleLabel, totalMSWLabel, innerGap15, plasticRecycledPropLabel, plasticIncineratedPropLabel, plasticLandfillPropLabel, innerGap16, plasticDomesticLabel, plasticExportPropLabel, plasticReExportPropLabel,
                                    innerGap17, plasticRecycEfficiencyLabel]

gapsInConditions = [innerGap15, innerGap16, innerGap17]

conditionsEntryListForPlacement = [totalMSWEntry, innerGap15, plasticRecycledPropEntry, plasticIncineratedPropEntry, plasticLandfillPropEntry, innerGap16, plasticDomesticEntry, plasticExportPropEntry, plasticReExportPropEntry, 
                                   innerGap17, plasticRecycEfficiencyEntry]


conditionsentryList = [totalMSWEntry, plasticRecycledPropEntry, plasticDomesticEntry, plasticRecycEfficiencyEntry, plasticExportPropEntry,
                       plasticReExportPropEntry, plasticIncineratedPropEntry, plasticLandfillPropEntry, wasteFacilityEmissionsEntry, landfillEmissionsEntry]


#Creates list of conditions entries that will be used for checking
conditionsPropCheckList = [plasticRecycledPropEntry, plasticIncineratedPropEntry, plasticLandfillPropEntry]
conditionsPropCheckList2 = [plasticDomesticEntry, plasticExportPropEntry, plasticReExportPropEntry]




#Creates buttons for checking, autofilling, and entering
conditionsButtonChecker = Button(my_frame2, text = ' Check Proportions ', command = conditionsCheckProp)
conditionsAutoButton = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(conditionsentryList, conditions2018))
conditionsEnterButton = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(conditionsentryList, conditions, typesOfWasteLabels, typesOfWasteEntry, mswCompButtonCheck, mswCompAuto, mswCompEnter))
conditions_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('Conditions', help_text[0]))



   
   
#Recycling data input labels and entry boxes
totalRecycLabel = Label(my_frame2, text = "Recycling Data", bg = 'white', font = 'Helvetica 12 bold')
totalRecycMassLabel = Label(my_frame2, text = "Total Recycled Mass:", bg = 'white', font = fontChoice)
miscInOrgRecycLabel = Label(my_frame2, text = "Misc. Inorg Waste (Percent): ", bg = 'white', font = fontChoice)
otherWasteRecycLabel = Label(my_frame2, text = "Other (Percent):", bg = 'white', font = fontChoice)
yardTrimmingsRecycLabel = Label(my_frame2, text = "Yard Trimmings (Percent):", bg = 'white', font = fontChoice)
foodRecycLabel = Label(my_frame2, text = "Food (Percent):", bg = 'white', font = fontChoice)
rltRecycLabel = Label(my_frame2, text = "Rubber, Leather, Textiles (Percent):", bg = 'white', font = fontChoice)
woodRecycLabel = Label(my_frame2, text = "Wood (Percent):", bg = 'white', font = fontChoice)
metalRecycLabel = Label(my_frame2, text = "Metals (Percent):", bg = 'white', font = fontChoice)
glassRecycLabel = Label(my_frame2, text = "Glass (Percent):", bg = 'white', font = fontChoice)
paperRecycLabel = Label(my_frame2, text = "Paper and Paperboard (Percent):", bg = 'white', font = fontChoice)
plasticRecycLabel = Label(my_frame2, text = "Plastic (Percent):", bg = 'white', font = fontChoice)

totalRecycMassEntry = Entry(my_frame2, width = 50)
miscInOrgRecycEntry = Entry(my_frame2, width = 50)
otherWasteRecycEntry = Entry(my_frame2, width = 50)
yardTrimmingsRecycEntry = Entry(my_frame2, width = 50)
foodRecycEntry = Entry(my_frame2, width = 50)
rltRecycEntry = Entry(my_frame2, width = 50)
woodRecycEntry = Entry(my_frame2, width = 50)
metalRecycEntry = Entry(my_frame2, width = 50)
glassRecycEntry = Entry(my_frame2, width = 50)
paperRecycEntry = Entry(my_frame2, width = 50)
plasticRecycEntry = Entry(my_frame2, width = 50)

#Creates lists of labels and entries for placement 
recycMSWPropsLabels= [totalRecycLabel, totalRecycMassLabel, miscInOrgRecycLabel, otherWasteRecycLabel, yardTrimmingsRecycLabel, foodRecycLabel,
                      rltRecycLabel, woodRecycLabel, metalRecycLabel, glassRecycLabel, paperRecycLabel, plasticRecycLabel]

recycMSWPropsEntry = [totalRecycMassEntry, miscInOrgRecycEntry, otherWasteRecycEntry, yardTrimmingsRecycEntry, foodRecycEntry, rltRecycEntry,
                      woodRecycEntry, metalRecycEntry, glassRecycEntry, paperRecycEntry, plasticRecycEntry]

recycMSWCheckList = [miscInOrgRecycEntry, otherWasteRecycEntry, yardTrimmingsRecycEntry, foodRecycEntry, rltRecycEntry,
                      woodRecycEntry, metalRecycEntry, glassRecycEntry, paperRecycEntry, plasticRecycEntry]


#Creates buttons for checking, autofilling, and entering
recycMSWButtonChecker = Button(my_frame2, text = ' Check Proportions ', command = lambda:checkProportions(recycMSWCheckList, 1))
recycMSWAutoButton = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(recycMSWPropsEntry, mswRecyc2018))
recycMSWEnterButton = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(recycMSWPropsEntry, mswRecyc, IncinMSWPropsLabels, IncinMSWPropsEntry, incinMSWButtonChecker, incinMSWAutoButton, incinMSWEnterButton))
recycMSW_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('MSW Recycling', help_text[2]))



#Incineration data input labels and entry boxes
totalIncinLabel = Label(my_frame2, text = "Incineration Data", bg = 'white', font = 'Helvetica 12 bold')
totalIncinMassLabel = Label(my_frame2, text = "Total Mass Incinerated: ", bg = 'white', font = fontChoice)
miscInOrgIncinLabel = Label(my_frame2, text = "Misc. Inorganic Wastes (Percent):", bg = 'white', font = fontChoice)
otherWasteIncinLabel = Label(my_frame2, text = "Other Wastes (Percent):", bg = 'white', font = fontChoice)
yardTrimmingsIncinLabel = Label(my_frame2, text = "Yard Trimmings (Percent):", bg = 'white', font = fontChoice)
foodIncinLabel = Label(my_frame2, text = "Food (Percent):", bg = 'white', font = fontChoice)
rltIncinLabel = Label(my_frame2, text = "Rubber, Leather, Textiles (Percent):", bg = 'white', font = fontChoice)
woodIncinLabel = Label(my_frame2, text = "Wood (Percent):", bg = 'white', font = fontChoice)
metalIncinLabel = Label(my_frame2, text = "Metal (Percent):", bg = 'white', font = fontChoice)
glassIncinLabel = Label(my_frame2, text = "Glass (Percent):", bg = 'white', font = fontChoice)
paperIncinLabel = Label(my_frame2, text = "Paper and Paperboard (Percent):", bg = 'white', font = fontChoice)
plasticIncinLabel = Label(my_frame2, text = "Plastic (Percent):", bg = 'white', font = fontChoice)

totalIncinMassEntry = Entry(my_frame2, width = 50)
miscInOrgIncinEntry = Entry(my_frame2, width = 50)
otherWasteIncinEntry = Entry(my_frame2, width = 50)
yardTrimmingsIncinEntry = Entry(my_frame2, width = 50)
foodIncinEntry = Entry(my_frame2, width = 50)
rltIncinEntry = Entry(my_frame2, width = 50)
woodIncinEntry = Entry(my_frame2, width = 50)
metalIncinEntry = Entry(my_frame2, width = 50)
glassIncinEntry = Entry(my_frame2, width = 50)
paperIncinEntry = Entry(my_frame2, width = 50)
plasticIncinEntry = Entry(my_frame2, width = 50)


#Creates lists for widget placement
IncinMSWPropsLabels= [totalIncinLabel, totalIncinMassLabel, miscInOrgIncinLabel, otherWasteIncinLabel, yardTrimmingsIncinLabel, foodIncinLabel,
                      rltIncinLabel, woodIncinLabel, metalIncinLabel, glassIncinLabel, paperIncinLabel, plasticIncinLabel]

IncinMSWPropsEntry = [totalIncinMassEntry, miscInOrgIncinEntry, otherWasteIncinEntry, yardTrimmingsIncinEntry, foodIncinEntry, rltIncinEntry,
                      woodIncinEntry, metalIncinEntry, glassIncinEntry, paperIncinEntry, plasticIncinEntry]

IncinMSWCheckList = [miscInOrgIncinEntry, otherWasteIncinEntry, yardTrimmingsIncinEntry, foodIncinEntry, rltIncinEntry,
                      woodIncinEntry, metalIncinEntry, glassIncinEntry, paperIncinEntry, plasticIncinEntry]


#Creates buttons for checking, autofilling, and entering data
incinMSWButtonChecker = Button(my_frame2, text = ' Check Proportions ', command = lambda:checkProportions(IncinMSWCheckList, 1))
incinMSWAutoButton = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(IncinMSWPropsEntry, mswIncin2018))
incinMSWEnterButton = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(IncinMSWPropsEntry, mswIncin, LandMSWPropsLabels, LandMSWPropsEntry, landMSWButtonChecker, landMSWAutoButton, landMSWEnterButton))
incinMSW_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('MSW Incineration', help_text[3]))



#Compost data input labels and entry boxes
totalCompostLabel = Label(my_frame2, text = "Compost Data", bg = 'white', font = 'Helvetica 12 bold')
totalCompostMassLabel = Label(my_frame2, text = "Total Mass Compost: ", bg = 'white', font = fontChoice)
miscInOrgCompostLabel = Label(my_frame2, text = "Misc. Inorganic Wastes (Percent):", bg = 'white', font = fontChoice)
otherWasteCompostLabel = Label(my_frame2, text = "Other Wastes (Percent):", bg = 'white', font = fontChoice)
yardTrimmingsCompostLabel = Label(my_frame2, text = "Yard Trimmings (Percent):", bg = 'white', font = fontChoice)
foodCompostLabel = Label(my_frame2, text = "Food (Percent):", bg = 'white', font = fontChoice)
rltCompostLabel = Label(my_frame2, text = "Rubber, Leather, Textiles (Percent):", bg = 'white', font = fontChoice)
woodCompostLabel = Label(my_frame2, text = "Wood (Percent):", bg = 'white', font = fontChoice)
metalCompostLabel = Label(my_frame2, text = "Metal (Percent):", bg = 'white', font = fontChoice)
glassCompostLabel = Label(my_frame2, text = "Glass (Percent):", bg = 'white', font = fontChoice)
paperCompostLabel = Label(my_frame2, text = "Paper and Paperboard (Percent):", bg = 'white', font = fontChoice)
plasticCompostLabel = Label(my_frame2, text = "Plastic (Percent):", bg = 'white', font = fontChoice)

totalCompostMassEntry = Entry(my_frame2, width = 50)
miscInOrgCompostEntry = Entry(my_frame2, width = 50)
otherWasteCompostEntry = Entry(my_frame2, width = 50)
yardTrimmingsCompostEntry = Entry(my_frame2, width = 50)
foodCompostEntry = Entry(my_frame2, width = 50)
rltCompostEntry = Entry(my_frame2, width = 50)
woodCompostEntry = Entry(my_frame2, width = 50)
metalCompostEntry = Entry(my_frame2, width = 50)
glassCompostEntry = Entry(my_frame2, width = 50)
paperCompostEntry = Entry(my_frame2, width = 50)
plasticCompostEntry = Entry(my_frame2, width = 50)

#creates lists for widget placement
CompostMSWPropsLabels= [totalCompostLabel, totalCompostMassLabel, miscInOrgCompostLabel, otherWasteCompostLabel, yardTrimmingsCompostLabel, foodCompostLabel,
                      rltCompostLabel, woodCompostLabel, metalCompostLabel, glassCompostLabel, paperCompostLabel, plasticCompostLabel]

CompostMSWPropsEntry = [totalCompostMassEntry, miscInOrgCompostEntry, otherWasteCompostEntry, yardTrimmingsCompostEntry, foodCompostEntry, rltCompostEntry,
                      woodCompostEntry, metalCompostEntry, glassCompostEntry, paperCompostEntry, plasticCompostEntry]

compostMSWCheckList = [miscInOrgCompostEntry, otherWasteCompostEntry, yardTrimmingsCompostEntry, foodCompostEntry, rltCompostEntry,
                      woodCompostEntry, metalCompostEntry, glassCompostEntry, paperCompostEntry, plasticCompostEntry]

#Creates buttons for checking proportions, autofilling, and entering data
compostMSWCheckerButton = Button(my_frame2, text = ' Check Proportions ', command = lambda:checkProportions(compostMSWCheckList, 1))
compostMSWAutoButton = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(CompostMSWPropsEntry, mswCompost2018))
compostMSWEnterButton = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(CompostMSWPropsEntry, mswCompost, recycPlasticLabels, recycPlasticEntry, plasticRecycButtonChecker, plasticRecycAutoButton, plasticRecycEnterButton))
compostMSW_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('MSW Compost', help_text[5]))


#Landfill Data input labels and entries
totalLandLabel = Label(my_frame2, text = "Landfill Data", bg = 'white', font = 'Helvetica 12 bold')
totalLandMassLabel = Label(my_frame2, text = "Total Mass Landfilled: ", bg = 'white', font = fontChoice)
miscInOrgLandLabel = Label(my_frame2, text = "Misc. Inorganic Wastes (Percent):", bg = 'white', font = fontChoice)
otherWasteLandLabel = Label(my_frame2, text = "Other Wastes (Percent):", bg = 'white', font = fontChoice)
yardTrimmingsLandLabel = Label(my_frame2, text = "Yard Trimmings (Percent):", bg = 'white', font = fontChoice)
foodLandLabel = Label(my_frame2, text = "Food (Percent):", bg = 'white', font = fontChoice)
rltLandLabel = Label(my_frame2, text = "Rubber, Leather, Textiles (Percent):", bg = 'white', font = fontChoice)
woodLandLabel = Label(my_frame2, text = "Wood (Percent):", bg = 'white', font = fontChoice)
metalLandLabel = Label(my_frame2, text = "Metal (Percent):", bg = 'white', font = fontChoice)
glassLandLabel = Label(my_frame2, text = "Glass (Percent):", bg = 'white', font = fontChoice)
paperLandLabel = Label(my_frame2, text = "Paper and Paperboard (Percent):", bg = 'white', font = fontChoice)
plasticLandLabel = Label(my_frame2, text = "Plastic (Percent):", bg = 'white', font = fontChoice)

totalLandMassEntry = Entry(my_frame2, width = 50)
miscInOrgLandEntry = Entry(my_frame2, width = 50)
otherWasteLandEntry = Entry(my_frame2, width = 50)
yardTrimmingsLandEntry = Entry(my_frame2, width = 50)
foodLandEntry = Entry(my_frame2, width = 50)
rltLandEntry = Entry(my_frame2, width = 50)
woodLandEntry = Entry(my_frame2, width = 50)
metalLandEntry = Entry(my_frame2, width = 50)
glassLandEntry = Entry(my_frame2, width = 50)
paperLandEntry = Entry(my_frame2, width = 50)
plasticLandEntry = Entry(my_frame2, width = 50)


#Creates lists for widget placement
LandMSWPropsLabels= [totalLandLabel, totalLandMassLabel, miscInOrgLandLabel, otherWasteLandLabel, yardTrimmingsLandLabel, foodLandLabel,
                      rltLandLabel, woodLandLabel, metalLandLabel, glassLandLabel, paperLandLabel, plasticLandLabel]

LandMSWPropsEntry = [totalLandMassEntry, miscInOrgLandEntry, otherWasteLandEntry, yardTrimmingsLandEntry, foodLandEntry, rltLandEntry,
                      woodLandEntry, metalLandEntry, glassLandEntry, paperLandEntry, plasticLandEntry]

LandMSWChecker = [miscInOrgLandEntry, otherWasteLandEntry, yardTrimmingsLandEntry, foodLandEntry, rltLandEntry,
                      woodLandEntry, metalLandEntry, glassLandEntry, paperLandEntry, plasticLandEntry]


#Creates buttons for checking, autofilling, and entering data
landMSWButtonChecker = Button(my_frame2, text = ' Check Proportions ', command = lambda:checkProportions(LandMSWChecker, 1))
landMSWAutoButton = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(LandMSWPropsEntry, mswLand2018))
landMSWEnterButton = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(LandMSWPropsEntry, mswLand, CompostMSWPropsLabels, CompostMSWPropsEntry, compostMSWCheckerButton, compostMSWAutoButton, compostMSWEnterButton))
landMSW_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('MSW Landfill', help_text[4]))



#Types of plastics entry boxes and labels for recycled list
plasticRecycProportionsLabel = Label(my_frame2, text = "Plastic Recycled Proportions", bg = 'white', font = 'Helvetica 12 bold')

petRecycLabel = Label(my_frame2, text = "PET Proportion (Percent):", bg = 'white', font = fontChoice)
hdpeRecycLabel = Label(my_frame2, text = "HDPE Proportion (Percent):", bg = 'white', font = fontChoice)
pvcRecycLabel = Label(my_frame2, text = "PVC Proportion (Percent):", bg = 'white', font = fontChoice)
ldpeRecycLabel = Label(my_frame2, text = "LDPE Proportion (Percent):", bg = 'white', font = fontChoice)
ppRecycLabel = Label(my_frame2, text = "PP Proportion (Percent):", bg = 'white', font = fontChoice)
psRecycLabel = Label(my_frame2, text = "PS Proportion (Percent):", bg = 'white', font = fontChoice)
otherRecycPlasticsLabel = Label(my_frame2, text = "Other Plastics Proportion (Percent):", bg = 'white', font = fontChoice)
plaRecycLabel = Label(my_frame2, text = "PLA Proportion (Percent):", bg = 'white', font = fontChoice)


petRecycEntry = Entry(my_frame2, width=50)
hdpeRecycEntry = Entry(my_frame2, width=50)
pvcRecycEntry = Entry(my_frame2, width=50)
ldpeRecycEntry = Entry(my_frame2, width=50)
ppRecycEntry = Entry(my_frame2, width=50)
psRecycEntry = Entry(my_frame2, width=50)
otherRecycPlasticsEntry = Entry(my_frame2, width=50)
plaRecycEntry = Entry(my_frame2, width=50)


#Creates lists for widget placement 
recycPlasticLabels = [plasticRecycProportionsLabel, petRecycLabel, hdpeRecycLabel, pvcRecycLabel, ldpeRecycLabel, plaRecycLabel, ppRecycLabel, psRecycLabel, otherRecycPlasticsLabel]
recycPlasticEntry = [petRecycEntry, hdpeRecycEntry, pvcRecycEntry, ldpeRecycEntry, plaRecycEntry, ppRecycEntry, psRecycEntry, otherRecycPlasticsEntry]

#Creates buttons for checking, autofilling, and entering data
plasticRecycButtonChecker = Button(my_frame2, text = ' Check Proportions ', command = lambda:checkProportions(recycPlasticEntry, 1))
plasticRecycAutoButton = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(recycPlasticEntry, plasticRecycledFractionsList2018))
plasticRecycEnterButton = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(recycPlasticEntry, plasticRecycledFractionsList, IncinPlasticLabels, IncinPlasticEntry, plasticIncinButtonChecker, plasticIncinAutoButton, plasticIncinEnterButton))
plasticRecyc_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('Plastic Recycling', help_text[6]))






#Types of plastics entry boxes and labels for landfilled list
plasticLandProportionsLabel = Label(my_frame2, text = "Plastic Landfilled Proportions", bg = 'white', font = 'Helvetica 12 bold')

petLandLabel = Label(my_frame2, text = "PET Proportion (Percent):", bg = 'white', font = fontChoice)
hdpeLandLabel = Label(my_frame2, text = "HDPE Proportion (Percent):", bg = 'white', font = fontChoice)
pvcLandLabel = Label(my_frame2, text = "PVC Proportion (Percent):", bg = 'white', font = fontChoice)
ldpeLandLabel = Label(my_frame2, text = "LDPE Proportion (Percent):", bg = 'white', font = fontChoice)
ppLandLabel = Label(my_frame2, text = "PP Proportion (Percent):", bg = 'white', font = fontChoice)
psLandLabel = Label(my_frame2, text = "PS Proportion (Percent):", bg = 'white', font = fontChoice)
otherLandPlasticsLabel = Label(my_frame2, text = "Other Plastics Proportion (Percent):", bg = 'white', font = fontChoice)
plaLandLabel = Label(my_frame2, text = "PLA Proportion (Percent):", bg = 'white', font = fontChoice)


petLandEntry = Entry(my_frame2, width=50)
hdpeLandEntry = Entry(my_frame2, width=50)
pvcLandEntry = Entry(my_frame2, width=50)
ldpeLandEntry = Entry(my_frame2, width=50)
ppLandEntry = Entry(my_frame2, width=50)
psLandEntry = Entry(my_frame2, width=50)
otherLandPlasticsEntry = Entry(my_frame2, width=50)
plaLandEntry = Entry(my_frame2, width=50)


#Creates lists for widget placement
LandPlasticLabels = [plasticLandProportionsLabel, petLandLabel, hdpeLandLabel, pvcLandLabel, ldpeLandLabel, plaLandLabel, ppLandLabel, psLandLabel, otherLandPlasticsLabel]
LandPlasticEntry = [petLandEntry, hdpeLandEntry, pvcLandEntry, ldpeLandEntry, plaLandEntry, ppLandEntry, psLandEntry, otherLandPlasticsEntry]


#Creates buttons for checking, autofilling, and entering data
plasticLandButtonChecker = Button(my_frame2, text = ' Check Proportions ', command = lambda:checkProportions(LandPlasticEntry, 1))
plasticLandAutoButton = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(LandPlasticEntry, plasticLandFractionsList))
plasticLandEnterButton = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(LandPlasticEntry, plasticLandFractionsList, RepRecycPlasticLabels, RepRecycPlasticEntry, NONE, plasticRepRecycAutoButton, plasticRepRecycEnterButton))
plasticLand_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('Plastic Landfill', help_text[8]))




#Types of plastics entry boxes and labels for Incinerated list
plasticIncinProportionsLabel = Label(my_frame2, text = "Plastic Incinerated Proportions", bg = 'white', font = 'Helvetica 12 bold')

petIncinLabel = Label(my_frame2, text = "PET Proportion (Percent):", bg = 'white', font = fontChoice)
hdpeIncinLabel = Label(my_frame2, text = "HDPE Proportion (Percent):", bg = 'white', font = fontChoice)
pvcIncinLabel = Label(my_frame2, text = "PVC Proportion (Percent):", bg = 'white', font = fontChoice)
ldpeIncinLabel = Label(my_frame2, text = "LDPE Proportion (Percent):", bg = 'white', font = fontChoice)
ppIncinLabel = Label(my_frame2, text = "PP Proportion (Percent):", bg = 'white', font = fontChoice)
psIncinLabel = Label(my_frame2, text = "PS Proportion (Percent):", bg = 'white', font = fontChoice)
otherIncinPlasticsLabel = Label(my_frame2, text = "Other Plastics Proportion (Percent):", bg = 'white', font = fontChoice)
plaIncinLabel = Label(my_frame2, text = "PLA Proportion (Percent):", bg = 'white', font = fontChoice)


petIncinEntry = Entry(my_frame2, width=50)
hdpeIncinEntry = Entry(my_frame2, width=50)
pvcIncinEntry = Entry(my_frame2, width=50)
ldpeIncinEntry = Entry(my_frame2, width=50)
ppIncinEntry = Entry(my_frame2, width=50)
psIncinEntry = Entry(my_frame2, width=50)
otherIncinPlasticsEntry = Entry(my_frame2, width=50)
plaIncinEntry = Entry(my_frame2, width=50)


#Creates lists for placement of widgets
IncinPlasticLabels = [plasticIncinProportionsLabel, petIncinLabel, hdpeIncinLabel, pvcIncinLabel, ldpeIncinLabel, plaIncinLabel, ppIncinLabel, psIncinLabel, otherIncinPlasticsLabel]
IncinPlasticEntry = [petIncinEntry, hdpeIncinEntry, pvcIncinEntry, ldpeIncinEntry, plaIncinEntry, ppIncinEntry, psIncinEntry, otherIncinPlasticsEntry]

#Creates buttons for checking, autofilling, and entering data
plasticIncinButtonChecker = Button(my_frame2, text = ' Check Proportions ', command = lambda:checkProportions(IncinPlasticEntry, 1))
plasticIncinAutoButton = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(IncinPlasticEntry, plasticIncinFractionsList2018))
plasticIncinEnterButton = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(IncinPlasticEntry, plasticIncinFractionsList, LandPlasticLabels, LandPlasticEntry, plasticLandButtonChecker, plasticLandAutoButton, plasticLandEnterButton))
plasticIncin_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('Plastic Incineration', help_text[7]))


#Types of plastics entry boxes and labels for reported recycled list
plasticRepRecycProportionsLabel = Label(my_frame2, text = "Plastic Reported Recycled Masses", bg = 'white', font = 'Helvetica 12 bold')

petRepRecycLabel = Label(my_frame2, text = "PET Proportion (Tons):", bg = 'white', font = fontChoice)
hdpeRepRecycLabel = Label(my_frame2, text = "HDPE Proportion (Tons):", bg = 'white', font = fontChoice)
pvcRepRecycLabel = Label(my_frame2, text = "PVC Proportion (Tons):", bg = 'white', font = fontChoice)
ldpeRepRecycLabel = Label(my_frame2, text = "LDPE Proportion (Tons):", bg = 'white', font = fontChoice)
ppRepRecycLabel = Label(my_frame2, text = "PP Proportion (Tons):", bg = 'white', font = fontChoice)
psRepRecycLabel = Label(my_frame2, text = "PS Proportion (Tons):", bg = 'white', font = fontChoice)
otherRepRecycPlasticsLabel = Label(my_frame2, text = "Other Plastics Proportion (Tons):", bg = 'white', font = fontChoice)
plaRepRecycLabel = Label(my_frame2, text = "PLA Proportion (Tons):", bg = 'white', font = fontChoice)


petRepRecycEntry = Entry(my_frame2, width=50)
hdpeRepRecycEntry = Entry(my_frame2, width=50)
pvcRepRecycEntry = Entry(my_frame2, width=50)
ldpeRepRecycEntry = Entry(my_frame2, width=50)
ppRepRecycEntry = Entry(my_frame2, width=50)
psRepRecycEntry = Entry(my_frame2, width=50)
otherRepRecycPlasticsEntry = Entry(my_frame2, width=50)
plaRepRecycEntry = Entry(my_frame2, width=50)

#Creates lists for widget placement
RepRecycPlasticLabels = [plasticRepRecycProportionsLabel, petRepRecycLabel, hdpeRepRecycLabel, pvcRepRecycLabel, ldpeRepRecycLabel, plaRepRecycLabel, ppRepRecycLabel, psRepRecycLabel, otherRepRecycPlasticsLabel]
RepRecycPlasticEntry = [petRepRecycEntry, hdpeRepRecycEntry, pvcRepRecycEntry, ldpeRepRecycEntry, plaRepRecycEntry, ppRepRecycEntry, psRepRecycEntry, otherRepRecycPlasticsEntry]


#Creates buttons for autofilling and entering the data
plasticRepRecycAutoButton = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(RepRecycPlasticEntry, repRecPlastics2018))
plasticRepRecycEnterButton = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(RepRecycPlasticEntry, repRecPlastics, ImportPlasticLabels, ImportPlasticEntry, NONE, plasticImportAutoButton, plasticImportEnterButton))
plasticRepRecyc_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('Reported Recycled Masses', help_text[9]))



#Types of plastics entry boxes and labels for import list
plasticImportProportionsLabel = Label(my_frame2, text = "Plastic Imported Mass", bg = 'white', font = 'Helvetica 12 bold')

ethyleneImportLabel = Label(my_frame2, text = "Ethylene Mass (Tons):", bg = 'white', font = fontChoice)
vinylChlorideImportLabel = Label(my_frame2, text = "Vinyl Chloride Mass (Tons):", bg = 'white', font = fontChoice)
styreneImportLabel = Label(my_frame2, text = "Styrene Mass (Tons):", bg = 'white', font = fontChoice)
otherImportLabel = Label(my_frame2, text = "Other Plastics (Tons):", bg = 'white', font = fontChoice)


ethyleneImportEntry = Entry(my_frame2, width=50)
vinylChlorideImportEntry = Entry(my_frame2, width=50)
styreneImportEntry = Entry(my_frame2, width=50)
otherImportEntry = Entry(my_frame2, width=50)


#Creates lists for widget placement
ImportPlasticLabels = [plasticImportProportionsLabel, ethyleneImportLabel, vinylChlorideImportLabel, styreneImportLabel, otherImportLabel]
ImportPlasticEntry = [ethyleneImportEntry, vinylChlorideImportEntry, styreneImportEntry, otherImportEntry]

#Creates button for autofilling and entering the data
plasticImportAutoButton = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(ImportPlasticEntry, repPlasticImport2018))
plasticImportEnterButton = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(ImportPlasticEntry, repPlasticImport, ExportPlasticLabels, ExportPlasticEntry, NONE, plasticExportAutoButton, plasticExportEnterButton))
plasticImport_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('Imported Plastics', help_text[10]))


#Types of plastics entry boxes and labels for Export list
plasticExportProportionsLabel = Label(my_frame2, text = "Plastic Exported Mass", bg = 'white', font = 'Helvetica 12 bold')

ethyleneExportLabel = Label(my_frame2, text = "Ethylene Mass (Tons):", bg = 'white', font = fontChoice)
vinylChlorideExportLabel = Label(my_frame2, text = "Vinyl Chloride Mass (Tons):", bg = 'white', font = fontChoice)
styreneExportLabel = Label(my_frame2, text = "Styrene Mass (Tons):", bg = 'white', font = fontChoice)
otherExportLabel = Label(my_frame2, text = "Other Plastics (Tons):", bg = 'white', font = fontChoice)


ethyleneExportEntry = Entry(my_frame2, width=50)
vinylChlorideExportEntry = Entry(my_frame2, width=50)
styreneExportEntry = Entry(my_frame2, width=50)
otherExportEntry = Entry(my_frame2, width=50)

#Creates lists for widget placement
ExportPlasticLabels = [plasticExportProportionsLabel, ethyleneExportLabel, vinylChlorideExportLabel, styreneExportLabel, otherExportLabel]
ExportPlasticEntry = [ethyleneExportEntry, vinylChlorideExportEntry, styreneExportEntry, otherExportEntry]
plasticExport_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('Exported Plastics', help_text[11]))

#Creates buttons for autofilling and entering data
plasticExportAutoButton = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(ExportPlasticEntry, repPlasticsExport2018))
plasticExportEnterButton = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(ExportPlasticEntry, repPlasticsExport, ReExportPlasticLabels, ReExportPlasticEntry, NONE, plasticReExportAutoButton, plasticReExportEnterButton))


#Types of plastics entry boxes and labels for ReExport list
plasticReExportProportionsLabel = Label(my_frame2, text = "Plastic ReExported Mass", bg = 'white', font = 'Helvetica 12 bold')

ethyleneReExportLabel = Label(my_frame2, text = "Ethylene Mass (Tons):", bg = 'white', font = fontChoice)
vinylChlorideReExportLabel = Label(my_frame2, text = "Vinyl Chloride Mass (Tons):", bg = 'white', font = fontChoice)
styreneReExportLabel = Label(my_frame2, text = "Styrene Mass (Tons):", bg = 'white', font = fontChoice)
otherReExportLabel = Label(my_frame2, text = "Other Plastics (Tons):", bg = 'white', font = fontChoice)


ethyleneReExportEntry = Entry(my_frame2, width=50)
vinylChlorideReExportEntry = Entry(my_frame2, width=50)
styreneReExportEntry = Entry(my_frame2, width=50)
otherReExportEntry = Entry(my_frame2, width=50)

#Creates lists for widget placement
ReExportPlasticLabels = [plasticReExportProportionsLabel, ethyleneReExportLabel, vinylChlorideReExportLabel, styreneReExportLabel, otherReExportLabel]
ReExportPlasticEntry = [ethyleneReExportEntry, vinylChlorideReExportEntry, styreneReExportEntry, otherReExportEntry]

#Creates buttons for autofilling and entering data
plasticReExportAutoButton = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(ReExportPlasticEntry, repPlasticsReExport2018))
plasticReExportEnterButton = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(ReExportPlasticEntry, repPlasticsReExport, conditionsLabelsListForPlacement, conditionsEntryListForPlacement, conditionsButtonChecker, conditionsAutoButton, conditionsEnterButton))
plasticReExport_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('Re-Exported Plastics', help_text[12]))



#Chemical Recycling section

def checkChemRecyc():
    for i in chemRecycEntries:
        try:
            g = float(i.get()) #makes sure input is numbers only
        except:
            gapLabel1.config(text = 'Error: Please enter a number into each box to continue.', fg = 'red')
            return
    g = float(chemRecyc_tolandEntry.get()) + float(chemRecyc_toIncinEntry.get())
    if g <100:
        gapLabel1.config(text = 'Check successful.') #indicates success
        return True
    else:
        gapLabel1.config(text = 'Landfill and incineration values greater than 1.', fg = 'red') #indicates failure
        return False
    
totalChemRecycLabel = Label(my_frame2, text = "Chemical Reprocessing Data (Optional)", bg = 'white', font = 'Helvetica 12 bold')
chemRecycFracLabel = Label(my_frame2, text = "Percent of Recyclate Sent to Chem. Recycling:", bg = 'white', font = fontChoice)
chemRecyc_tolandLabel = Label(my_frame2, text = "Percent of Chem. Recycling Sent to Landfill:", bg = 'white', font = fontChoice)
chemRecyc_toIncinLabel = Label(my_frame2, text = "Percent of Chem. Recycling Sent to Incineration:", bg = 'white', font = fontChoice)

chemRecycFracEntry = Entry(my_frame2, width = 50)
chemRecyc_tolandEntry = Entry(my_frame2, width = 50)
chemRecyc_toIncinEntry = Entry(my_frame2, width = 50)

chemRecycLabels = [totalChemRecycLabel, chemRecycFracLabel, chemRecyc_tolandLabel, chemRecyc_toIncinLabel]
chemRecycEntries = [chemRecycFracEntry, chemRecyc_tolandEntry, chemRecyc_toIncinEntry]

chemRecycAutoButton = Button(my_frame2, text = ' Autofill 2018 Data', command = lambda: autofill(chemRecycEntries, chemRecyc2018))
chemRecycEnterButton = Button(my_frame2, text = 'Enter Above Dataset', command = lambda: enter(chemRecycEntries, chemRecycData, conditionsLabelsListForPlacement, conditionsEntryListForPlacement, conditionsButtonChecker, conditionsAutoButton, conditionsEnterButton))
chemRecycCheckButton = Button(my_frame2, text = 'Check Proportions', command = checkChemRecyc)
plasticChemRecyc_help = Button(my_frame2, text = 'Help', command = lambda: help_popup('Chemical Reprocessing', help_text[13]))


for i in chemRecycEntries:
    i.insert(END, 0)
    
    
    
#categorizes entries to convert percents to fractions
percent_except_0 = [recycMSWPropsEntry, IncinMSWPropsEntry, LandMSWPropsEntry, CompostMSWPropsEntry]

total_percent = [typesOfWasteEntry, recycPlasticEntry,IncinPlasticEntry, LandPlasticEntry]

other_entries = [conditionsEntryListForPlacement, RepRecycPlasticEntry, ImportPlasticEntry, ExportPlasticEntry, ReExportPlasticEntry, chemRecycEntries]

#Creates lists of labels and entries to allow for a loop to place them on screen
customLabelsList = [conditionsLabelsListForPlacement, typesOfWasteLabels, recycMSWPropsLabels, IncinMSWPropsLabels, LandMSWPropsLabels, 
                    CompostMSWPropsLabels, recycPlasticLabels, IncinPlasticLabels, LandPlasticLabels, RepRecycPlasticLabels, ImportPlasticLabels, 
                    ExportPlasticLabels, ReExportPlasticLabels, chemRecycLabels]


customEntryList = [conditionsEntryListForPlacement, typesOfWasteEntry, recycMSWPropsEntry, IncinMSWPropsEntry, LandMSWPropsEntry, CompostMSWPropsEntry,
                   recycPlasticEntry,IncinPlasticEntry, LandPlasticEntry, RepRecycPlasticEntry, ImportPlasticEntry, ExportPlasticEntry,
                   ReExportPlasticEntry, chemRecycEntries]

#Gap labels to appropriately space widgets on screen
gapLabel1 = Label(my_frame2, bg = 'white')
gapLabel2 = Label(my_frame2, bg = 'white')
gapLabel3 = Label(my_frame2, bg = 'white', text = 'Status:', font = fontChoice)


innerGap1 = Label(my_frame2, bg = 'white')
innerGap2 = Label(my_frame2, bg = 'white')
innerGap3 = Label(my_frame2, bg = 'white')
innerGap4 = Label(my_frame2, bg = 'white')
innerGap5 = Label(my_frame2, bg = 'white')
innerGap6 = Label(my_frame2, bg = 'white')
innerGap7 = Label(my_frame2, bg = 'white')
innerGap8 = Label(my_frame2, bg = 'white')
innerGap9 = Label(my_frame2, bg = 'white')
innerGap10 = Label(my_frame2, bg = 'white')
innerGap11 = Label(my_frame2, bg = 'white')
innerGap12 = Label(my_frame2, bg = 'white')
innerGap13 = Label(my_frame2, bg = 'white')
innerGap14 = Label(my_frame2, bg = 'white')


#Creates more lists of widgets for easier placement on screen


innerGapLabelsList = [innerGap1, innerGap2, innerGap3, innerGap4, innerGap5, innerGap6, innerGap7, innerGap8, innerGap9, innerGap10, 
                      innerGap11, innerGap12, innerGap13, innerGap14]

checkButtonList = [conditionsButtonChecker, mswCompButtonCheck, recycMSWButtonChecker, incinMSWButtonChecker,  landMSWButtonChecker, 
                   compostMSWCheckerButton, plasticRecycButtonChecker, plasticIncinButtonChecker, plasticLandButtonChecker, chemRecycCheckButton]

extraButTonsList = [conditionsAutoButton, conditionsEnterButton, mswCompAuto, mswCompEnter, recycMSWAutoButton, recycMSWEnterButton,
                    incinMSWAutoButton, incinMSWEnterButton, landMSWAutoButton, landMSWEnterButton, compostMSWAutoButton, compostMSWEnterButton,
                    plasticRecycAutoButton, plasticRecycEnterButton, plasticIncinAutoButton, plasticIncinEnterButton, plasticLandAutoButton,
                    plasticLandEnterButton, plasticRepRecycAutoButton, plasticRepRecycEnterButton, plasticImportAutoButton, plasticImportEnterButton,
                    plasticExportAutoButton, plasticExportEnterButton, plasticReExportAutoButton, plasticReExportEnterButton, chemRecycAutoButton, 
                    chemRecycEnterButton, conditions_help, mswComp_help, recycMSW_help, incinMSW_help, landMSW_help, compostMSW_help, 
                    plasticRecyc_help, plasticIncin_help, plasticLand_help, plasticRepRecyc_help, plasticImport_help, plasticExport_help, 
                    plasticReExport_help, plasticChemRecyc_help]

# title label and placement
userSpecificationsLabel = Label(my_frame2, text = "User Specifications", bg = 'white', font = 'Helvetica 14 bold')
userSpecificationsLabel.grid(column = 1, row = 10, columnspan = 2)

#Function connected to calculate button to extract values from entry boxes, append to list
    # and complete appropriate calculations MJC
def calculateWasteProportions():
   assignValues() #will be removed before distribution. This is a programming shortcut
   makeCalculations(False, [False])
   fillMatFlowAnalSumTRVW()

#Create Button that will assign values and make calculations based on input 
calculateButton = Button(my_frame2, text=" Calculate Streams ", command=calculateWasteProportions)

#Grids conditions widgets at boot up
def placeConditions():
    conditionsLabelsListForPlacement[0].grid(column = 1, row = 11, columnspan = 2)
    gapLabel1.grid(column = 2, row = 12, sticky = W)
    gapLabel3.grid(column = 1, row = 12, sticky = E)
    frameRow = 13
    for i in range(len(conditionsLabelsListForPlacement)-1):
        if conditionsLabelsListForPlacement not in gapsInConditions:
            conditionsLabelsListForPlacement[i+1].grid(column = 1, row = frameRow, sticky = E)
            conditionsEntryListForPlacement[i].grid(column = 2, row = frameRow, sticky = W)
        else:
            conditionsLabelsListForPlacement[i+1].grid(column = 1, row = frameRow, columnspan = 2)
            
        frameRow+=1

    gapLabel2.grid(column = 1, row = frameRow, columnspan = 2)
    frameRow +=1
    conditionsButtonChecker.grid(column = 1, row = frameRow, columnspan = 2)
    frameRow +=1
    conditionsAutoButton.grid(column = 1, row = frameRow, columnspan = 2)
    frameRow +=1
    conditionsEnterButton.grid(column = 1, row = frameRow, columnspan = 2)
    frameRow +=1
    calculateButton.grid(column=1, row=frameRow, columnspan = 2)
    frameRow +=1
    conditions_help.grid(column = 1, row = frameRow, columnspan = 2)

placeConditions()
#Function that will remove category widgets from screen 
def removeLabels():
    for i in customLabelsList:
        for b in i:
            b.grid_remove()
    for c in customEntryList:
        for q in c:
            q.grid_remove()
    for v in checkButtonList:
        v.grid_remove()
    gapLabel2.grid_remove()
    calculateButton.grid_remove()
    for i in extraButTonsList:
        i.grid_remove()
            
#function that will add next set of widgets to stream
def showSection(label, entry, checkButton, autofill, enter, helpButton):
    removeLabels()
    gapLabel1.config(text = '')
    frameRow = 13
    if label!= conditionsLabelsListForPlacement:
        label[0].grid(column = 1, row = 11, columnspan = 2)
        for i in range(len(label)-1):
            label[i+1].grid(column = 1, row = frameRow, sticky = E)
            frameRow += 1
        frameRow = 13
        for i in entry:
            i.grid(column = 2, row = frameRow, sticky = W)
            frameRow += 1
        gapLabel2.grid(column = 1, row = frameRow, columnspan = 2)
        frameRow+=1
        if checkButton != NONE:
            checkButton.grid(column = 1, row = frameRow, columnspan = 2)
            frameRow+=1
    else:
        placeConditions()
        frameRow = 30
    autofill.grid(column = 1, row = frameRow, columnspan = 2)
    frameRow+=1
    enter.grid(column = 1, row = frameRow, columnspan = 2)
    frameRow+=1
    calculateButton.grid(column = 1, row = frameRow, columnspan = 2)
    frameRow += 1
    helpButton.grid(column = 1, row = frameRow, columnspan = 2)
    

#Menu at left of buttons that will change list of available entries
showConditionsButton = Button(my_frame2, text = 'Conditions', command = lambda:showSection(conditionsLabelsListForPlacement, conditionsEntryListForPlacement, conditionsButtonChecker, conditionsAutoButton, conditionsEnterButton, conditions_help))
showMSWCompButton = Button(my_frame2, text = 'MSW Composition', command = lambda: showSection(typesOfWasteLabels, typesOfWasteEntry, mswCompButtonCheck, mswCompAuto, mswCompEnter, mswComp_help))
showrecycMSWButton = Button(my_frame2, text = 'MSW Recycling', command = lambda:showSection(recycMSWPropsLabels, recycMSWPropsEntry, recycMSWButtonChecker, recycMSWAutoButton, recycMSWEnterButton, recycMSW_help))
showincinMSWButton = Button(my_frame2, text = 'MSW Incineration', command = lambda: showSection(IncinMSWPropsLabels, IncinMSWPropsEntry, incinMSWButtonChecker, incinMSWAutoButton, incinMSWEnterButton, incinMSW_help))
showlandMSWButton = Button(my_frame2, text = 'MSW Landfill', command = lambda:showSection(LandMSWPropsLabels, LandMSWPropsEntry, landMSWButtonChecker, landMSWAutoButton, landMSWEnterButton, landMSW_help))
showcompostMSWButton = Button(my_frame2, text = "MSW Compost", command = lambda: showSection(CompostMSWPropsLabels, CompostMSWPropsEntry, compostMSWCheckerButton, compostMSWAutoButton, compostMSWEnterButton, compostMSW_help))
showPlasticRecycButton = Button(my_frame2, text = 'Plastic Recycling', command = lambda: showSection(recycPlasticLabels, recycPlasticEntry, plasticRecycButtonChecker, plasticRecycAutoButton, plasticRecycEnterButton, plasticRecyc_help))
showIncinPlasticButton = Button(my_frame2, text = 'Incinerated Plastic', command = lambda: showSection(IncinPlasticLabels, IncinPlasticEntry, plasticIncinButtonChecker, plasticIncinAutoButton, plasticIncinEnterButton, plasticIncin_help))
showLandPlasticButton = Button(my_frame2, text = 'Landfilled Plastic', command = lambda: showSection(LandPlasticLabels, LandPlasticEntry, plasticLandButtonChecker, plasticLandAutoButton, plasticLandEnterButton, plasticLand_help))
showRepRecycButton = Button(my_frame2, text = 'Reported Recycled Masses', command = lambda: showSection(RepRecycPlasticLabels, RepRecycPlasticEntry, NONE, plasticRepRecycAutoButton, plasticRepRecycEnterButton, plasticRepRecyc_help))
showImportButton = Button(my_frame2, text = 'Imported Plastic', command = lambda: showSection(ImportPlasticLabels, ImportPlasticEntry, NONE, plasticImportAutoButton, plasticImportEnterButton, plasticImport_help))
showExportButton = Button(my_frame2, text = 'Exported Plastics', command = lambda: showSection(ExportPlasticLabels, ExportPlasticEntry, NONE, plasticExportAutoButton, plasticExportEnterButton, plasticExport_help))
showReExportButton = Button(my_frame2, text = 'Re-Exported Plastics', command = lambda: showSection(ReExportPlasticLabels, ReExportPlasticEntry, NONE, plasticReExportAutoButton, plasticReExportEnterButton, plasticReExport_help))
showChemRecycButton = Button(my_frame2, text = 'Chemical Reprocessing Data (Optional)', command = lambda: showSection(chemRecycLabels, chemRecycEntries, chemRecycCheckButton, chemRecycAutoButton, chemRecycEnterButton, plasticChemRecyc_help))

#Creates list of these buttons above
showButtonLists = [showConditionsButton, showMSWCompButton, showrecycMSWButton, showincinMSWButton, showlandMSWButton, showcompostMSWButton, 
                   showPlasticRecycButton, showIncinPlasticButton, showLandPlasticButton, showRepRecycButton, showImportButton, showExportButton,
                   showReExportButton, showChemRecycButton]
frameRow =11

#loop that places these buttons
for i in showButtonLists:
    i.grid(column = 0, row = frameRow, sticky = EW)
    frameRow +=1

#List of strings that will be used as confirmation after each set of data is entered
listOfEntryCategories = {str(conditionsentryList):"Conditions Data Entered", str(typesOfWasteEntry): "Municipal Solid Waste Composition Data Entered", str(recycMSWPropsEntry): "MSW Recycling Data Entered", 
                         str(LandMSWPropsEntry): "MSW Landfill Data Entered", str(IncinMSWPropsEntry): "MSW Incineration Data Entered", str(CompostMSWPropsEntry): "MSW Compost Data Entered", 
                         str(recycPlasticEntry): "Plastic Recycled Data Entered", str(IncinPlasticEntry): "Plastic Incinerated Data Entered", str(LandPlasticEntry): "Plastic Landfill Data Entered",
                         str(RepRecycPlasticEntry): "Reported Recycling Data Entered", str(ImportPlasticEntry): "Import Data Entered", str(ExportPlasticEntry): "Export Data Entered", 
                         str(ReExportPlasticEntry): "Re-Export Data Entered"}
        

####################################################
### Stream Summary Tab
#Function that will be used to check data has been input:

def dataInputQuestionMark():
    listOfInputs = [conditions, mswCompProp, mswRecyc, mswIncin, mswLand, mswCompost, repRecPlastics, repPlasticImport, repPlasticsExport,
                    repPlasticsReExport, plasticLandFractionsList, plasticRecycledFractionsList, plasticIncinFractionsList, chemRecycData]
    
    for i in listOfInputs:
        if i == []:
            return True
            
    
    return False


#Function that will be used to display frame that contains labels of user input
def displayInput():
    
    if dataInputQuestionMark():
        
        errorLabel.config(text = 'Error: Please finish inputting data.', font = fontChoice)
        return
    
    top1= Toplevel(dataAnalysisFrame)
    top1.geometry('%dx%d+%d+%d' % (w, h, x, y-25))
    top1.title("User Input")
    dataAnalysisCanvas = Canvas(top1, bg = 'white') #Added to frame above so a scrollbar can be created
    my_frame7 = Frame(dataAnalysisCanvas, width = 300, height = 300, bg = 'white', bd = 5) #Will contain widgets to display input and graphs
    dataAnalysisCanvas.pack(fill = BOTH, expand = 1)
    my_frame7.pack(side = LEFT, fill = BOTH, expand = 1)
    
    #Creates scrollbar for input data frame
    dataAnalysisScrollBar = Scrollbar(my_frame7, orient = 'vertical', command = dataAnalysisCanvas.yview)
    dataAnalysisScrollBar.grid(column = 6, row = 0, rowspan = 80, sticky = NS)
    dataAnalysisScrollBar.config(command=dataAnalysisCanvas.yview)

    dataAnalysisCanvas['yscrollcommand']=dataAnalysisScrollBar.set
    
    dataAnalysisCanvas.bind('<Configure>', lambda e: dataAnalysisCanvas.configure(scrollregion = dataAnalysisCanvas.bbox('all')))

    dataAnalysisCanvas.create_window((0,0), window = my_frame7, anchor = 'nw')
    my_program.bind_all('<MouseWheel>', lambda event: dataAnalysisCanvas.yview_scroll(int(-1*(event.delta/120)), "units"))
    
    
    
    gapLabel4 = Label(my_frame7, bg = 'white', text = '                     ')
    gapLabel5 = Label(my_frame7, bg = 'white', text = '________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________')
    gapLabel6 = Label(my_frame7, bg = 'white', text = '                     ')
    gapLabel7 = Label(my_frame7, bg = 'white', text = '________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________')
    gapLabel8 = Label(my_frame7, bg = 'white', text = '                     ')
    gapLabel9 = Label(my_frame7, bg = 'white', text = '________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________')
    gapLabel10 = Label(my_frame7, bg = 'white', text = '                     ')
    gapLabel11 = Label(my_frame7, bg = 'white', text = '________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________')
    gapLabel12 = Label(my_frame7, bg = 'white', text = '                     ')
    gapLabel13 = Label(my_frame7, bg = 'white', text = '                     ')
    gapLabel14 = Label(my_frame7, bg = 'white', text = '                     ')
    gapLabel15 = Label(my_frame7, bg = 'white', text = '                     ')
    gapLabel16 = Label(my_frame2, bg = 'white', text = '                     ')
    gapLabel17 = Label(my_frame7, bg = 'white', text = '                     ')

    gapLabelsList = [gapLabel4, gapLabel5, gapLabel6, gapLabel7, gapLabel8, gapLabel9, gapLabel10, gapLabel11,
                     gapLabel12, gapLabel13, gapLabel14, gapLabel15]
    
    #Creates and configures titles for data analysis frames
    dataAnalTitle = tk.Text(my_frame7, bd=0, highlightthickness = 0, bg = "white", height=1, width=125)
    dataAnalTitle.insert(tk.INSERT,"User Specifications")
    dataAnalTitle.tag_configure("center", justify = 'center')
    dataAnalTitle.tag_add("center", 1.0, 'end')
    dataAnalTitle.configure(font = ("Helvetica 16 bold"))
    dataAnalTitle.config(state="disabled")
    dataAnalTitle.grid(column=0,row=0,columnspan=6)
    gapLabel17.grid(column = 0, row = 1, columnspan = 6)
    
    #Creates category titles for each section of data
    mswStreamLabel = Label(my_frame7, text = "MSW Composition", font = 'Helvetica 14 bold', bg = 'white')
    miscInOrgWasteStreamLabel = Label(my_frame7, text = "Misc. Inorganic Waste (Percent): ", font = fontChoice, bg="white")
    otherWasteStreamLabel = Label(my_frame7, text = "Other (Percent): ", font = fontChoice, bg="white")
    yardTrimmingsStreamLabel = Label(my_frame7, text = "Yard Trimmings (Percent): ", font = fontChoice, bg="white")
    foodWasteStreamLabel = Label(my_frame7, text = "Food (Percent): ", font = fontChoice, bg="white")
    rltWasteStreamLabel = Label(my_frame7, text = "Rubber, Leather, Textiles (Percent): ", font = fontChoice, bg="white")
    woodWasteStreamLabel = Label(my_frame7, text = "Wood (Percent): ", font = fontChoice, bg="white")
    metalsWasteStreamLabel = Label(my_frame7, text = "Metals (Percent): ", font = fontChoice, bg="white")
    glassWasteStreamLabel = Label(my_frame7, text = "Glass (Percent): ", font = fontChoice, bg="white")
    paperAndBoardStreamLabel = Label(my_frame7, text = "Paper and Paperboard (Percent): ", font = fontChoice, bg="white")
    plasticsStreamLabel = Label(my_frame7, text = "Plastics (Percent): ", font = fontChoice, bg="white")
    
    #Creating list of input data labels (not values) MJC
    typesOfWasteStreamStreamLabels = [mswStreamLabel, miscInOrgWasteStreamLabel, otherWasteStreamLabel, yardTrimmingsStreamLabel, foodWasteStreamLabel, rltWasteStreamLabel, woodWasteStreamLabel, metalsWasteStreamLabel, glassWasteStreamLabel, paperAndBoardStreamLabel, plasticsStreamLabel]
    
    
    
    #Creates conditions StreamLabels and entries
    conditionsTitleStreamLabel = Label(my_frame7, text = "Conditions", bg = 'white', font = 'Helvetica 12 bold')
    totalMSWStreamLabel = Label(my_frame7, text = 'Total MSW (Tons):', bg = 'white', font = fontChoice)
    plasticRecycledPropStreamLabel = Label(my_frame7, text = 'Total Plastic Recycled (Fraction, Domestic and Export):', bg = 'white', font = fontChoice)
    plasticDomesticStreamLabel = Label(my_frame7, text = 'Plastic Recycled Domestically (Percent):', bg = 'white', font = fontChoice)
    plasticRecycEfficiencyStreamLabel = Label(my_frame7, text = 'Plastic Recycling Efficiency (Percent):', bg = 'white', font = fontChoice)
    plasticExportPropStreamLabel = Label(my_frame7, text = 'Plastic Export Fraction (Percent):', bg = 'white', font = fontChoice)
    plasticReExportPropStreamLabel = Label(my_frame7, text = "Plastic Re-Export (Percent):", bg = 'white', font = fontChoice)
    plasticIncineratedPropStreamLabel = Label(my_frame7, text = 'Plastic Incinerated (Percent):', bg = 'white', font = fontChoice)
    plasticLandfillPropStreamLabel = Label(my_frame7, text = "Plastic Landfilled (Percent):", bg = 'white', font = fontChoice)
    wasteFacilityEmissionsStreamLabel = Label(my_frame7, text = 'Waste Facility Emissions (Tons):', bg = 'white', font = fontChoice)
    landfillEmissionsStreamLabel = Label(my_frame7, text = 'Emissions from Landfill (Tons):', bg = 'white', font = fontChoice)
    
    
    
    conditionsStreamStreamLabelsList = [conditionsTitleStreamLabel, totalMSWStreamLabel, plasticRecycledPropStreamLabel, plasticDomesticStreamLabel, plasticRecycEfficiencyStreamLabel, plasticExportPropStreamLabel,
                            plasticReExportPropStreamLabel, plasticIncineratedPropStreamLabel, plasticLandfillPropStreamLabel, wasteFacilityEmissionsStreamLabel, landfillEmissionsStreamLabel]
    
    conditionsStreamStreamLabelsListForPlacement = [conditionsTitleStreamLabel, totalMSWStreamLabel, plasticRecycledPropStreamLabel, plasticDomesticStreamLabel, plasticExportPropStreamLabel, plasticReExportPropStreamLabel,
                                                    plasticRecycEfficiencyStreamLabel, plasticIncineratedPropStreamLabel,  plasticLandfillPropStreamLabel, wasteFacilityEmissionsStreamLabel, landfillEmissionsStreamLabel]
    
    
    
    #Recycling data input StreamLabels and entry boxes
    totalRecycStreamLabel = Label(my_frame7, text = "Recycling Data", bg = 'white', font = 'Helvetica 12 bold')
    totalRecycMassStreamLabel = Label(my_frame7, text = "Total Recycled Mass:", bg = 'white', font = fontChoice)
    miscInOrgRecycStreamLabel = Label(my_frame7, text = "Misc. Inorg Waste (Percent): ", bg = 'white', font = fontChoice)
    otherWasteRecycStreamLabel = Label(my_frame7, text = "Other (Percent):", bg = 'white', font = fontChoice)
    yardTrimmingsRecycStreamLabel = Label(my_frame7, text = "Yard Trimmings (Percent):", bg = 'white', font = fontChoice)
    foodRecycStreamLabel = Label(my_frame7, text = "Food (Percent):", bg = 'white', font = fontChoice)
    rltRecycStreamLabel = Label(my_frame7, text = "Rubber, Leather, Textiles (Percent):", bg = 'white', font = fontChoice)
    woodRecycStreamLabel = Label(my_frame7, text = "Wood (Percent):", bg = 'white', font = fontChoice)
    metalRecycStreamLabel = Label(my_frame7, text = "Metals (Percent):", bg = 'white', font = fontChoice)
    glassRecycStreamLabel = Label(my_frame7, text = "Glass (Percent):", bg = 'white', font = fontChoice)
    paperRecycStreamLabel = Label(my_frame7, text = "Paper and Paperboard (Percent):", bg = 'white', font = fontChoice)
    plasticRecycStreamLabel = Label(my_frame7, text = "Plastic (Percent):", bg = 'white', font = fontChoice)
    
    
    recycMSWPropsStreamStreamLabels= [totalRecycStreamLabel, totalRecycMassStreamLabel, miscInOrgRecycStreamLabel, otherWasteRecycStreamLabel, yardTrimmingsRecycStreamLabel, foodRecycStreamLabel,
                          rltRecycStreamLabel, woodRecycStreamLabel, metalRecycStreamLabel, glassRecycStreamLabel, paperRecycStreamLabel, plasticRecycStreamLabel]
    
    
    
    #Incineration data input StreamLabels and entry boxes
    totalIncinStreamLabel = Label(my_frame7, text = "Incineration Data", bg = 'white', font = 'Helvetica 12 bold')
    totalIncinMassStreamLabel = Label(my_frame7, text = "Total Mass Incinerated: ", bg = 'white', font = fontChoice)
    miscInOrgIncinStreamLabel = Label(my_frame7, text = "Misc. Inorganic Wastes (Percent):", bg = 'white', font = fontChoice)
    otherWasteIncinStreamLabel = Label(my_frame7, text = "Other Wastes (Percent):", bg = 'white', font = fontChoice)
    yardTrimmingsIncinStreamLabel = Label(my_frame7, text = "Yard Trimmings (Percent):", bg = 'white', font = fontChoice)
    foodIncinStreamLabel = Label(my_frame7, text = "Food (Percent):", bg = 'white', font = fontChoice)
    rltIncinStreamLabel = Label(my_frame7, text = "Rubber, Leather, Textiles (Percent):", bg = 'white', font = fontChoice)
    woodIncinStreamLabel = Label(my_frame7, text = "Wood (Percent):", bg = 'white', font = fontChoice)
    metalIncinStreamLabel = Label(my_frame7, text = "Metal (Percent):", bg = 'white', font = fontChoice)
    glassIncinStreamLabel = Label(my_frame7, text = "Glass (Percent):", bg = 'white', font = fontChoice)
    paperIncinStreamLabel = Label(my_frame7, text = "Paper and Paperboard (Percent):", bg = 'white', font = fontChoice)
    plasticIncinStreamLabel = Label(my_frame7, text = "Plastic (Percent):", bg = 'white', font = fontChoice)
    
    
    IncinMSWPropsStreamStreamLabels= [totalIncinStreamLabel, totalIncinMassStreamLabel, miscInOrgIncinStreamLabel, otherWasteIncinStreamLabel, yardTrimmingsIncinStreamLabel, foodIncinStreamLabel,
                                      rltIncinStreamLabel, woodIncinStreamLabel, metalIncinStreamLabel, glassIncinStreamLabel, paperIncinStreamLabel, plasticIncinStreamLabel]
    
    
    #Compost data input StreamLabels and entry boxes
    totalCompostStreamLabel = Label(my_frame7, text = "Compost Data", bg = 'white', font = 'Helvetica 12 bold')
    totalCompostMassStreamLabel = Label(my_frame7, text = "Total Mass Compost: ", bg = 'white', font = fontChoice)
    miscInOrgCompostStreamLabel = Label(my_frame7, text = "Misc. Inorganic Wastes (Percent):", bg = 'white', font = fontChoice)
    otherWasteCompostStreamLabel = Label(my_frame7, text = "Other Wastes (Percent):", bg = 'white', font = fontChoice)
    yardTrimmingsCompostStreamLabel = Label(my_frame7, text = "Yard Trimmings (Percent):", bg = 'white', font = fontChoice)
    foodCompostStreamLabel = Label(my_frame7, text = "Food (Percent):", bg = 'white', font = fontChoice)
    rltCompostStreamLabel = Label(my_frame7, text = "Rubber, Leather, Textiles (Percent):", bg = 'white', font = fontChoice)
    woodCompostStreamLabel = Label(my_frame7, text = "Wood (Percent):", bg = 'white', font = fontChoice)
    metalCompostStreamLabel = Label(my_frame7, text = "Metal (Percent):", bg = 'white', font = fontChoice)
    glassCompostStreamLabel = Label(my_frame7, text = "Glass (Percent):", bg = 'white', font = fontChoice)
    paperCompostStreamLabel = Label(my_frame7, text = "Paper and Paperboard (Percent):", bg = 'white', font = fontChoice)
    plasticCompostStreamLabel = Label(my_frame7, text = "Plastic (Percent):", bg = 'white', font = fontChoice)
    
    
    
    CompostMSWPropsStreamStreamLabels= [totalCompostStreamLabel, totalCompostMassStreamLabel, miscInOrgCompostStreamLabel, otherWasteCompostStreamLabel, yardTrimmingsCompostStreamLabel, foodCompostStreamLabel,
                          rltCompostStreamLabel, woodCompostStreamLabel, metalCompostStreamLabel, glassCompostStreamLabel, paperCompostStreamLabel, plasticCompostStreamLabel]
    
    
    
    #Landfill Data input StreamLabels and entries
    totalLandStreamLabel = Label(my_frame7, text = "Landfill Data", bg = 'white', font = 'Helvetica 12 bold')
    totalLandMassStreamLabel = Label(my_frame7, text = "Total Mass Landfilled: ", bg = 'white', font = fontChoice)
    miscInOrgLandStreamLabel = Label(my_frame7, text = "Misc. Inorganic Wastes (Percent):", bg = 'white', font = fontChoice)
    otherWasteLandStreamLabel = Label(my_frame7, text = "Other Wastes (Percent):", bg = 'white', font = fontChoice)
    yardTrimmingsLandStreamLabel = Label(my_frame7, text = "Yard Trimmings (Percent):", bg = 'white', font = fontChoice)
    foodLandStreamLabel = Label(my_frame7, text = "Food (Percent):", bg = 'white', font = fontChoice)
    rltLandStreamLabel = Label(my_frame7, text = "Rubber, Leather, Textiles (Percent):", bg = 'white', font = fontChoice)
    woodLandStreamLabel = Label(my_frame7, text = "Wood (Percent):", bg = 'white', font = fontChoice)
    metalLandStreamLabel = Label(my_frame7, text = "Metal (Percent):", bg = 'white', font = fontChoice)
    glassLandStreamLabel = Label(my_frame7, text = "Glass (Percent):", bg = 'white', font = fontChoice)
    paperLandStreamLabel = Label(my_frame7, text = "Paper and Paperboard (Percent):", bg = 'white', font = fontChoice)
    plasticLandStreamLabel = Label(my_frame7, text = "Plastic (Percent):", bg = 'white', font = fontChoice)
    
    
    LandMSWPropsStreamStreamLabels= [totalLandStreamLabel, totalLandMassStreamLabel, miscInOrgLandStreamLabel, otherWasteLandStreamLabel, yardTrimmingsLandStreamLabel, foodLandStreamLabel,
                          rltLandStreamLabel, woodLandStreamLabel, metalLandStreamLabel, glassLandStreamLabel, paperLandStreamLabel, plasticLandStreamLabel]
    
    
    
    #Types of plastics entry boxes and StreamLabels for recycled list
    plasticRecycProportionsStreamLabel = Label(my_frame7, text = "Plastic Recycled Proportions", bg = 'white', font = 'Helvetica 12 bold')
    
    petRecycStreamLabel = Label(my_frame7, text = "PET Proportion (Percent):", bg = 'white', font = fontChoice)
    hdpeRecycStreamLabel = Label(my_frame7, text = "HDPE Proportion (Percent):", bg = 'white', font = fontChoice)
    pvcRecycStreamLabel = Label(my_frame7, text = "PVC Proportion (Percent):", bg = 'white', font = fontChoice)
    ldpeRecycStreamLabel = Label(my_frame7, text = "LDPE Proportion (Percent):", bg = 'white', font = fontChoice)
    ppRecycStreamLabel = Label(my_frame7, text = "PP Proportion (Percent):", bg = 'white', font = fontChoice)
    psRecycStreamLabel = Label(my_frame7, text = "PS Proportion (Percent):", bg = 'white', font = fontChoice)
    otherRecycPlasticsStreamLabel = Label(my_frame7, text = "Other Plastics Proportion (Percent):", bg = 'white', font = fontChoice)
    plaRecycStreamLabel = Label(my_frame7, text = "PLA Proportion (Percent):", bg = 'white', font = fontChoice)
    
    plasticRecycPropsStreamsLabels = [plasticRecycProportionsStreamLabel, petRecycStreamLabel, hdpeRecycStreamLabel, pvcRecycStreamLabel, ldpeRecycStreamLabel, plaRecycStreamLabel, ppRecycStreamLabel, 
                               psRecycStreamLabel, otherRecycPlasticsStreamLabel]
    
    #Types of plastics entry boxes and StreamLabels for landfilled list
    plasticLandProportionsStreamLabel = Label(my_frame7, text = "Plastic Landfilled Proportions", bg = 'white', font = 'Helvetica 12 bold')
    
    petLandStreamLabel = Label(my_frame7, text = "PET Proportion (Percent):", bg = 'white', font = fontChoice)
    hdpeLandStreamLabel = Label(my_frame7, text = "HDPE Proportion (Percent):", bg = 'white', font = fontChoice)
    pvcLandStreamLabel = Label(my_frame7, text = "PVC Proportion (Percent):", bg = 'white', font = fontChoice)
    ldpeLandStreamLabel = Label(my_frame7, text = "LDPE Proportion (Percent):", bg = 'white', font = fontChoice)
    ppLandStreamLabel = Label(my_frame7, text = "PP Proportion (Percent):", bg = 'white', font = fontChoice)
    psLandStreamLabel = Label(my_frame7, text = "PS Proportion (Percent):", bg = 'white', font = fontChoice)
    otherLandPlasticsStreamLabel = Label(my_frame7, text = "Other Plastics Proportion (Percent):", bg = 'white', font = fontChoice)
    plaLandStreamLabel = Label(my_frame7, text = "PLA Proportion (Percent):", bg = 'white', font = fontChoice)
    
    
    
    LandPlasticStreamStreamLabels = [plasticLandProportionsStreamLabel, petLandStreamLabel, hdpeLandStreamLabel, pvcLandStreamLabel, ldpeLandStreamLabel, plaLandStreamLabel, ppLandStreamLabel, psLandStreamLabel, otherLandPlasticsStreamLabel]
    
    
    #Types of plastics entry boxes and StreamLabels for Incinerated list
    plasticIncinProportionsStreamLabel = Label(my_frame7, text = "Plastic Incinerated Proportions", bg = 'white', font = 'Helvetica 12 bold')
    
    petIncinStreamLabel = Label(my_frame7, text = "PET Proportion (Percent):", bg = 'white', font = fontChoice)
    hdpeIncinStreamLabel = Label(my_frame7, text = "HDPE Proportion (Percent):", bg = 'white', font = fontChoice)
    pvcIncinStreamLabel = Label(my_frame7, text = "PVC Proportion (Percent):", bg = 'white', font = fontChoice)
    ldpeIncinStreamLabel = Label(my_frame7, text = "LDPE Proportion (Percent):", bg = 'white', font = fontChoice)
    ppIncinStreamLabel = Label(my_frame7, text = "PP Proportion (Percent):", bg = 'white', font = fontChoice)
    psIncinStreamLabel = Label(my_frame7, text = "PS Proportion (Percent):", bg = 'white', font = fontChoice)
    otherIncinPlasticsStreamLabel = Label(my_frame7, text = "Other Plastics Proportion (Percent):", bg = 'white', font = fontChoice)
    plaIncinStreamLabel = Label(my_frame7, text = "PLA Proportion (Percent):", bg = 'white', font = fontChoice)
    
    
    IncinPlasticStreamStreamLabels = [plasticIncinProportionsStreamLabel, petIncinStreamLabel, hdpeIncinStreamLabel, pvcIncinStreamLabel, ldpeIncinStreamLabel, plaIncinStreamLabel, ppIncinStreamLabel, psIncinStreamLabel, otherIncinPlasticsStreamLabel]
    
    #Types of plastics entry boxes and StreamLabels for reported recycled list
    plasticRepRecycProportionsStreamLabel = Label(my_frame7, text = "Plastic Reported Recycled Masses", bg = 'white', font = 'Helvetica 12 bold')
    
    petRepRecycStreamLabel = Label(my_frame7, text = "PET Proportion (Tons):", bg = 'white', font = fontChoice)
    hdpeRepRecycStreamLabel = Label(my_frame7, text = "HDPE Proportion (Tons):", bg = 'white', font = fontChoice)
    pvcRepRecycStreamLabel = Label(my_frame7, text = "PVC Proportion (Tons):", bg = 'white', font = fontChoice)
    ldpeRepRecycStreamLabel = Label(my_frame7, text = "LDPE Proportion (Tons):", bg = 'white', font = fontChoice)
    ppRepRecycStreamLabel = Label(my_frame7, text = "PP Proportion (Tons):", bg = 'white', font = fontChoice)
    psRepRecycStreamLabel = Label(my_frame7, text = "PS Proportion (Tons):", bg = 'white', font = fontChoice)
    otherRepRecycPlasticsStreamLabel = Label(my_frame7, text = "Other Plastics Proportion (Tons):", bg = 'white', font = fontChoice)
    plaRepRecycStreamLabel = Label(my_frame7, text = "PLA Proportion (Tons):", bg = 'white', font = fontChoice)
    
    
    RepRecycPlasticStreamStreamLabels = [plasticRepRecycProportionsStreamLabel, petRepRecycStreamLabel, hdpeRepRecycStreamLabel, pvcRepRecycStreamLabel, ldpeRepRecycStreamLabel, plaRepRecycStreamLabel, ppRepRecycStreamLabel, psRepRecycStreamLabel, otherRepRecycPlasticsStreamLabel]
    
    #Types of plastics entry boxes and StreamLabels for import list
    plasticImportProportionsStreamLabel = Label(my_frame7, text = "Plastic Imported Mass", bg = 'white', font = 'Helvetica 12 bold')
    
    ethyleneImportStreamLabel = Label(my_frame7, text = "Ethylene Mass (Tons):", bg = 'white', font = fontChoice)
    vinylChlorideImportStreamLabel = Label(my_frame7, text = "Vinyl Chloride Mass (Tons):", bg = 'white', font = fontChoice)
    styreneImportStreamLabel = Label(my_frame7, text = "Styrene Mass (Tons):", bg = 'white', font = fontChoice)
    otherImportStreamLabel = Label(my_frame7, text = "Other Plastics (Tons):", bg = 'white', font = fontChoice)
    
    
    
    ImportPlasticStreamStreamLabels = [plasticImportProportionsStreamLabel, ethyleneImportStreamLabel, vinylChlorideImportStreamLabel, styreneImportStreamLabel, otherImportStreamLabel]
    
    
    #Types of plastics entry boxes and StreamLabels for Export list
    plasticExportProportionsStreamLabel = Label(my_frame7, text = "Plastic Exported Mass", bg = 'white', font = 'Helvetica 12 bold')
    
    ethyleneExportStreamLabel = Label(my_frame7, text = "Ethylene Mass (Tons):", bg = 'white', font = fontChoice)
    vinylChlorideExportStreamLabel = Label(my_frame7, text = "Vinyl Chloride Mass (Tons):", bg = 'white', font = fontChoice)
    styreneExportStreamLabel = Label(my_frame7, text = "Styrene Mass (Tons):", bg = 'white', font = fontChoice)
    otherExportStreamLabel = Label(my_frame7, text = "Other Plastics (Tons):", bg = 'white', font = fontChoice)
    
    
    
    ExportPlasticStreamStreamLabels = [plasticExportProportionsStreamLabel, ethyleneExportStreamLabel, vinylChlorideExportStreamLabel, styreneExportStreamLabel, otherExportStreamLabel]
    
    
    #Types of plastics entry boxes and StreamLabels for ReExport list
    plasticReExportProportionsStreamLabel = Label(my_frame7, text = "Plastic ReExported Mass", bg = 'white', font = 'Helvetica 12 bold')
    
    ethyleneReExportStreamLabel = Label(my_frame7, text = "Ethylene Mass (Tons):", bg = 'white', font = fontChoice)
    vinylChlorideReExportStreamLabel = Label(my_frame7, text = "Vinyl Chloride Mass (Tons):", bg = 'white', font = fontChoice)
    styreneReExportStreamLabel = Label(my_frame7, text = "Styrene Mass (Tons):", bg = 'white', font = fontChoice)
    otherReExportStreamLabel = Label(my_frame7, text = "Other Plastics (Tons):", bg = 'white', font = fontChoice)
    
    ReExportPlasticStreamStreamLabels = [plasticReExportProportionsStreamLabel, ethyleneReExportStreamLabel, vinylChlorideReExportStreamLabel, styreneReExportStreamLabel, otherReExportStreamLabel]
    
    
    chemRecyc_title = Label(my_frame7, text = 'Chemical Reprocessing Data', bg = 'white', font = 'Helvetic 12 bold')
    
    chemRecycFracLabelInput = Label(my_frame7, text = 'Fraction of Recyclate to Chemical Reprocessing', bg = 'white', font = fontChoice)
    chemRecycLabelInput_toLand = Label(my_frame7, text = 'Fraction of Chemical Reprocessing to Landfill', bg = 'white', font = fontChoice)
    chemRecycLabelInput_toIncin = Label(my_frame7, text = 'Fraction of Chemical Reprocessing to Incineration', bg = 'white', font = fontChoice)
    
    chemRecycStreamlabels = [chemRecyc_title, chemRecycFracLabelInput, chemRecycLabelInput_toLand, chemRecycLabelInput_toIncin]
    #######################################################################################################################################
    #######################################################################################################################################
    #######################################################################################################################################
    #######################################################################################################################################
    ##################################################################################################################################################################
    #Labels whose text will show Values
    miscInOrgWasteValueLabel = Label(my_frame7, font = fontChoice, bg="white")
    otherWasteValueLabel = Label(my_frame7, font = fontChoice, bg="white")
    yardTrimmingsValueLabel = Label(my_frame7, font = fontChoice, bg="white")
    foodWasteValueLabel = Label(my_frame7, font = fontChoice, bg="white")
    rltWasteValueLabel = Label(my_frame7, font = fontChoice, bg="white")
    woodWasteValueLabel = Label(my_frame7, font = fontChoice, bg="white")
    metalsWasteValueLabel = Label(my_frame7, font = fontChoice, bg="white")
    glassWasteValueLabel = Label(my_frame7, font = fontChoice, bg="white")
    paperAndBoardValueLabel = Label(my_frame7, font = fontChoice, bg="white")
    plasticsValueLabel = Label(my_frame7, font = fontChoice, bg="white")
    
    
    #Creating list of value labels MJC
    typesOfWasteValueLabels = [miscInOrgWasteValueLabel, otherWasteValueLabel, yardTrimmingsValueLabel, foodWasteValueLabel, rltWasteValueLabel, woodWasteValueLabel, metalsWasteValueLabel, glassWasteValueLabel, paperAndBoardValueLabel, plasticsValueLabel]
    
    for i in range(len(mswCompProp)):
        typesOfWasteValueLabels[i].config(text = str(round((mswCompProp[i])*100, 1)), font = fontChoice, fg = 'saddlebrown', bg = 'white')
    
    
    
    #Creates conditions StreamLabels and entries
    totalMSWValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plasticRecycledPropValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plasticDomesticValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plasticRecycEfficiencyValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plasticExportPropValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plasticReExportPropValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plasticIncineratedPropValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plasticLandfillPropValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    wasteFacilityEmissionsValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    landfillEmissionsValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    
    
    
    conditionsValueValueLabelsList = [totalMSWValueLabel, plasticRecycledPropValueLabel, plasticDomesticValueLabel, plasticRecycEfficiencyValueLabel, plasticExportPropValueLabel,
                            plasticReExportPropValueLabel, plasticIncineratedPropValueLabel, plasticLandfillPropValueLabel, wasteFacilityEmissionsValueLabel, landfillEmissionsValueLabel]
    
    conditionsValueValueLabelsListForPlacement = [totalMSWValueLabel, plasticRecycledPropValueLabel, plasticDomesticValueLabel, plasticExportPropValueLabel,
                                      plasticReExportPropValueLabel, plasticRecycEfficiencyValueLabel, plasticIncineratedPropValueLabel, plasticLandfillPropValueLabel, wasteFacilityEmissionsValueLabel, 
                                      landfillEmissionsValueLabel]
    addIn = conditions[1]
    del conditions[1]
    for i in range(len(conditions)):
        if i == 0 or i == 8 or i == 9:
            conditionsValueValueLabelsListForPlacement[i].config(text = str(round(conditions[i], 1)), font = fontChoice, fg = 'saddlebrown', bg = 'white')
        else:
            conditionsValueValueLabelsListForPlacement[i].config(text = str(round(conditions[i]*100, 3)), font = fontChoice, fg = 'saddlebrown', bg = 'white')

    conditions.insert(1, addIn)

    #Recycling data input StreamLabels and entry boxes
    totalRecycMassValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    miscInOrgRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    otherWasteRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    yardTrimmingsRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    foodRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    rltRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    woodRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    metalRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    glassRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    paperRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plasticRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    
    
    recycMSWPropsValueLabels= [totalRecycMassValueLabel, miscInOrgRecycValueLabel, otherWasteRecycValueLabel, yardTrimmingsRecycValueLabel, foodRecycValueLabel,
                          rltRecycValueLabel, woodRecycValueLabel, metalRecycValueLabel, glassRecycValueLabel, paperRecycValueLabel, plasticRecycValueLabel]

    
    for i in range(len(mswRecyc)):
        if i !=0:
            recycMSWPropsValueLabels[i].config(text = str(round(mswRecyc[i]*100, 3)), font = fontChoice, fg = 'saddlebrown', bg = 'white')
        else:
            recycMSWPropsValueLabels[i].config(text = str(round(mswRecyc[i], 3)), font = fontChoice, fg = 'saddlebrown', bg = 'white')

    
    #Incineration data input StreamLabels and entry boxes
    totalIncinMassValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    miscInOrgIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    otherWasteIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    yardTrimmingsIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    foodIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    rltIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    woodIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    metalIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    glassIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    paperIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plasticIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    
    
    IncinMSWPropsValueLabels= [totalIncinMassValueLabel, miscInOrgIncinValueLabel, otherWasteIncinValueLabel, yardTrimmingsIncinValueLabel, foodIncinValueLabel,
                          rltIncinValueLabel, woodIncinValueLabel, metalIncinValueLabel, glassIncinValueLabel, paperIncinValueLabel, plasticIncinValueLabel]
    
    for i in range(len(mswIncin)):
        if i !=0:
            IncinMSWPropsValueLabels[i].config(text = str(round(mswIncin[i]*100, 3)), font = fontChoice, fg = 'saddlebrown', bg = 'white')
        else:
            IncinMSWPropsValueLabels[i].config(text = str(round(mswIncin[i], 3)), font = fontChoice, fg = 'saddlebrown', bg = 'white')

    #Compost data input StreamLabels and entry boxes
    totalCompostMassValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    miscInOrgCompostValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    otherWasteCompostValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    yardTrimmingsCompostValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    foodCompostValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    rltCompostValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    woodCompostValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    metalCompostValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    glassCompostValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    paperCompostValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plasticCompostValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    
    
    
    CompostMSWPropsValueLabels= [totalCompostMassValueLabel, miscInOrgCompostValueLabel, otherWasteCompostValueLabel, yardTrimmingsCompostValueLabel, foodCompostValueLabel,
                          rltCompostValueLabel, woodCompostValueLabel, metalCompostValueLabel, glassCompostValueLabel, paperCompostValueLabel, plasticCompostValueLabel]

     
    for i in range(len(mswCompost)):
        if i !=0:
            CompostMSWPropsValueLabels[i].config(text = str(round(mswCompost[i]*100, 3)), font = fontChoice, fg = 'saddlebrown', bg = 'white')
        else:
            CompostMSWPropsValueLabels[i].config(text = str(round(mswCompost[i], 3)), font = fontChoice, fg = 'saddlebrown', bg = 'white')

    
    #Landfill Data input StreamLabels and entries
    totalLandMassValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    miscInOrgLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    otherWasteLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    yardTrimmingsLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    foodLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    rltLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    woodLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    metalLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    glassLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    paperLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plasticLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    
    
    LandMSWPropsValueLabels= [totalLandMassValueLabel, miscInOrgLandValueLabel, otherWasteLandValueLabel, yardTrimmingsLandValueLabel, foodLandValueLabel,
                          rltLandValueLabel, woodLandValueLabel, metalLandValueLabel, glassLandValueLabel, paperLandValueLabel, plasticLandValueLabel]
    
     
    for i in range(len(mswLand)):
        if i !=0:
            LandMSWPropsValueLabels[i].config(text = str(round(mswLand[i]*100, 3)), font = fontChoice, fg = 'saddlebrown', bg = 'white')
        else:
            LandMSWPropsValueLabels[i].config(text = str(round(mswLand[i], 3)), font = fontChoice, fg = 'saddlebrown', bg = 'white')

    #Types of plastics entry boxes and StreamLabels for recycled list
    petRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    hdpeRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    pvcRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    ldpeRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    ppRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    psRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    otherRecycPlasticsValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plaRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    
    plasticRecycValueLabels = [petRecycValueLabel, hdpeRecycValueLabel, pvcRecycValueLabel, ldpeRecycValueLabel, plaRecycValueLabel, ppRecycValueLabel, psRecycValueLabel,
                               otherRecycPlasticsValueLabel]
    
     
    for i in range(len(plasticRecycledFractionsList)):
         plasticRecycValueLabels[i].config(text = str(round(plasticRecycledFractionsList[i]*100, 3)), font = fontChoice, fg = 'saddlebrown', bg = 'white')
    
    #Types of plastics entry boxes and StreamLabels for landfilled list
    
    petLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    hdpeLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    pvcLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    ldpeLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    ppLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    psLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    otherLandPlasticsValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plaLandValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    
    
    
    LandPlasticValueLabels = [petLandValueLabel, hdpeLandValueLabel, pvcLandValueLabel, ldpeLandValueLabel, plaLandValueLabel, ppLandValueLabel, psLandValueLabel, otherLandPlasticsValueLabel]
    
     
    for i in range(len(plasticLandFractionsList)):
         LandPlasticValueLabels[i].config(text = str(round(plasticLandFractionsList[i], 3)), font = fontChoice, fg = 'saddlebrown', bg = 'white')
    
    #Types of plastics entry boxes and StreamLabels for Incinerated list
    petIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    hdpeIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    pvcIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    ldpeIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    ppIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    psIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    otherIncinPlasticsValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plaIncinValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    
    
    IncinPlasticValueLabels = [petIncinValueLabel, hdpeIncinValueLabel, pvcIncinValueLabel, ldpeIncinValueLabel, plaIncinValueLabel, ppIncinValueLabel, psIncinValueLabel, otherIncinPlasticsValueLabel]
    
   
    for i in range(len(plasticIncinFractionsList)):
         IncinPlasticValueLabels[i].config(text = str(round(plasticIncinFractionsList[i],3)), font = fontChoice, fg = 'saddlebrown', bg = 'white')
    
    
    #Types of plastics entry boxes and StreamLabels for reported recycled list
    petRepRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    hdpeRepRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    pvcRepRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    ldpeRepRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    ppRepRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    psRepRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    otherRepRecycPlasticsValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    plaRepRecycValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    
    
    RepRecycPlasticValueLabel = [petRepRecycValueLabel, hdpeRepRecycValueLabel, pvcRepRecycValueLabel, ldpeRepRecycValueLabel, plaRepRecycValueLabel, ppRepRecycValueLabel, psRepRecycValueLabel, otherRepRecycPlasticsValueLabel]
    
    
    for i in range(len(repRecPlastics)):
         RepRecycPlasticValueLabel[i].config(text = str(repRecPlastics[i]), font = fontChoice, fg = 'saddlebrown', bg = 'white')
    
    
    #Types of plastics entry boxes and StreamLabels for import list
    ethyleneImportValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    vinylChlorideImportValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    styreneImportValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    otherImportValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    
    
    
    ImportPlasticValueLabels = [ethyleneImportValueLabel, vinylChlorideImportValueLabel, styreneImportValueLabel, otherImportValueLabel]
    
      
    for i in range(len(repPlasticImport)):
         ImportPlasticValueLabels[i].config(text = str(repPlasticImport[i]), font = fontChoice, fg = 'saddlebrown', bg = 'white')
    
    
    #Types of plastics entry boxes and StreamLabels for Export list
    ethyleneExportValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    vinylChlorideExportValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    styreneExportValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    otherExportValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    
    
    
    ExportPlasticValueLabels = [ethyleneExportValueLabel, vinylChlorideExportValueLabel, styreneExportValueLabel, otherExportValueLabel]
    

    for i in range(len(repPlasticsExport)):
         ExportPlasticValueLabels[i].config(text = str(repPlasticsExport[i]), font = fontChoice, fg = 'saddlebrown', bg = 'white')
    
    #Types of plastics entry boxes and StreamLabels for ReExport list
    ethyleneReExportValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    vinylChlorideReExportValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    styreneReExportValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    otherReExportValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    
    ReExportPlasticValueLabels = [ethyleneReExportValueLabel, vinylChlorideReExportValueLabel, styreneReExportValueLabel, otherReExportValueLabel]
    
    
    for i in range(len(repPlasticsReExport)):
         ReExportPlasticValueLabels[i].config(text = str(repPlasticsReExport[i]), font = fontChoice, fg = 'saddlebrown', bg = 'white')
    
    chemRecycFracValueLabel = Label(my_frame7, bg = 'white', font = fontChoice)
    chemRecycValueLabel_toLand = Label(my_frame7, bg = 'white', font= fontChoice)
    chemRecycValueLabel_toIncin = Label(my_frame7, bg = 'white', font = fontChoice)
    
    chemRecycValueLabels = [chemRecycFracValueLabel, chemRecycValueLabel_toLand, chemRecycValueLabel_toIncin]
    
    for i in range(len(chemRecycValueLabels)):
        chemRecycValueLabels[i].config(text = str(round(chemRecycData[i]*100)), font = fontChoice, fg = 'saddlebrown', bg = 'white')
    #list of each row's labels
    rowStream1 = [conditionsStreamStreamLabelsListForPlacement, typesOfWasteStreamStreamLabels, recycMSWPropsStreamStreamLabels]
    
    rowStream2 = [IncinMSWPropsStreamStreamLabels, LandMSWPropsStreamStreamLabels, CompostMSWPropsStreamStreamLabels]
    
    rowStream3 = [plasticRecycPropsStreamsLabels, IncinPlasticStreamStreamLabels, LandPlasticStreamStreamLabels]
    
    rowStream4 = [RepRecycPlasticStreamStreamLabels, ImportPlasticStreamStreamLabels, ExportPlasticStreamStreamLabels]
    
    rowStream5 = [ReExportPlasticStreamStreamLabels, chemRecycStreamlabels]
    
    rowValue1 = [conditionsValueValueLabelsListForPlacement, typesOfWasteValueLabels, recycMSWPropsValueLabels]
    
    rowValue2 = [IncinMSWPropsValueLabels, LandMSWPropsValueLabels, CompostMSWPropsValueLabels]
    
    rowValue3 = [plasticRecycValueLabels, IncinPlasticValueLabels, LandPlasticValueLabels]
    
    rowValue4 = [RepRecycPlasticValueLabel, ImportPlasticValueLabels, ExportPlasticValueLabels]
    
    rowValue5 = [ReExportPlasticValueLabels, chemRecycValueLabels]
    
    gapLabel13.grid(column = 0, row = 1, columnspan = 6)
    
    #Function that will place each row of labels in the appropriate spot
    def rowStreamPlacer(stream, value, gap, row):
        col = 0
        for i in range(len(stream)):
            frameNum = row
            for a in range(len(stream[i])):
                if a == 0:
                    stream[i][a].grid(column = col, row = frameNum, columnspan = 2)
                    frameNum +=1
    
                    if i ==0:
                        gapLabelsList[gap].grid(column = 0, row = frameNum, columnspan = 6)
                else:
                    stream[i][a].grid(column = col, row = frameNum, sticky = E)
                    value[i][a-1].grid(column = col +1, row = frameNum, sticky = W)
                frameNum+=1
            col +=2
        
        
    #places rows and appropriate gap labels
    rowStreamPlacer(rowStream1, rowValue1, 0, 2)
    gapLabelsList[1].grid(column = 0, row =15, columnspan = 6)
    rowStreamPlacer(rowStream2, rowValue2, 2, 16)
    gapLabelsList[3].grid(column = 0, row = 29, columnspan = 6)
    rowStreamPlacer(rowStream3, rowValue3, 4, 30)
    gapLabelsList[5].grid(column = 0, row = 40, columnspan = 6)
    rowStreamPlacer(rowStream4, rowValue4, 6, 41)
    gapLabelsList[7].grid(column = 0, row = 51, columnspan = 6)
    rowStreamPlacer(rowStream5, rowValue5, 8, 52)
    gapLabelsList[9].grid(column = 0, row = 58, columnspan = 6)
    
#Creates title for scenario visualization tab
scenarioTitle = tk.Text(dataAnalysisFrame, bg = "white", height=2, width=200, bd = 0)
scenarioTitle.config(font=("Helvetica 20 bold"))
scenarioTitle.insert(tk.INSERT,"Scenario Visualization")
scenarioTitle.tag_configure('center', justify = "center")
scenarioTitle.tag_add('center', 1.0, 'end')
scenarioTitle.config(state="disabled")
scenarioTitle.pack()

#Creates and places buttons for above two functions
displayInputButton = Button(dataAnalysisFrame, text = 'Display User Input', command = displayInput)

displayInputButton.pack()

#creates label that will indicate an error if the data has not all been input and the user tries to open up the pop up
errorLabel = Label(dataAnalysisFrame, bg = 'white')
errorLabel.pack()

#Creates frame for succeeding graphs
#creates and adds canvas that will hold frame for plots (canvas created to allow for scrollbar)
plotCanvas = Canvas(dataAnalysisFrame, bg = 'white')
plotScrollBar = Scrollbar(dataAnalysisFrame, orient = 'vertical', command = plotCanvas.yview)
plotScrollBar.pack(side = RIGHT, fill = Y)
plotCanvas.pack(fill = BOTH, expand = 1)

#creates and configures scrollbar for plot frame
plotScrollBar.config(command = plotCanvas.yview)
plotCanvas['yscrollcommand'] = plotScrollBar.set
plotCanvas.bind('<Configure>', lambda e: plotCanvas.configure(scrollregion = plotCanvas.bbox('all')))

plotFrame = Frame(plotCanvas, bg = 'white')
plotCanvas.create_window((0,0), window = plotFrame, anchor = 'nw')

###################################################
#EPR Tab
#Makes slider change cause different display for additive release in mechanical recycling
sensAnalCanvas_epr = Canvas(epr_analysis, bg = 'white')

#Creates scrollbar for sensitivity analysis

sensAnalCanvas_epr.pack(side = 'left', fill = 'both', expand = 1)


sensScroll_epr = Scrollbar(epr_analysis, orient = 'vertical', command = sensAnalCanvas_epr.yview)
sensScroll_epr.pack(side = 'right', fill = 'y')
sensScroll_epr.config(command=sensAnalCanvas_epr.yview)
sensAnalCanvas_epr.configure(yscrollcommand = sensScroll_epr.set)
sensAnalCanvas_epr.bind('<Configure>', lambda e: sensAnalCanvas_epr.configure(scrollregion = sensAnalCanvas_epr.bbox('all')))

sensitivityAnalysis_epr = Frame(sensAnalCanvas_epr, bg = 'white')
sensAnalCanvas_epr.create_window((0,0), window = sensitivityAnalysis_epr, anchor = 'nw')


sensTitle_epr = tk.Text (sensitivityAnalysis_epr, bg = 'white', height = 2, width = 60, bd = 0)
sensTitle_epr.config(font = ('Helvetica 20 bold'))
sensTitle_epr.insert(tk.INSERT, "Sensitivity Analysis")
sensTitle_epr.tag_configure('center', justify = 'center')
sensTitle_epr.tag_add('center', 1.0, 'end')
sensTitle_epr.config(state = 'disabled')


numCol = 6
rowFrame = 0
sensTitle_epr.grid(column = 0, row = rowFrame, columnspan = numCol)

def epr_command():
    
    showSensAnal()
    litterAnal_epr.clear()
    waterAnal_epr.clear()
    scatter7_epr.get_tk_widget().grid_forget()

    recs = range(9, 41)
    new_masses = [conditions[1]*(1-i/100) for i in range(40)]


    ind = round(conditions[2]*100)
    
    for i in range(len(recs)):
        litterAnal_epr.append(litterAnal[ind-1]*new_masses[i])
        waterAnal_epr.append(waterAnal[ind-1]*new_masses[i])
    
    figure3_epr = plt.Figure(figsize=(10,8), dpi=100, layout = 'tight')
    scatter4_epr = FigureCanvasTkAgg(figure3_epr, sensitivityAnalysis_epr)
    scatter4_epr.get_tk_widget().grid(column = 0, row = 6, columnspan = 4, rowspan = 30)
    ax3_epr = figure3_epr.add_subplot(111)
    ax3_epr.set_xlabel('Recycling Rate (%)')
    ax3_epr.set_ylabel('Plastic Additive Release (tons)')
    ax3_epr.set_title('EPR: Additive Release')
    ax4_epr = ax3_epr.twinx()
    ax4_epr.plot(recs, [sensitivityPoints[i+ind] for i in range(len(recs))], 'g', label = 'Additive Releases')
    ax4_epr.tick_params(right = False) 
    ax4_epr.set_ylabel('asd;fjasdfkasdf', color = 'w')
    ax4_epr.set_yticklabels([])

    
    ax3_epr.plot(recs, [sensitivityPoints[i+ind] for i in range(len(recs))], 'g', label = 'Additive Releases')
    #Creates and places figure
    figure6_epr = plt.Figure(figsize=(10.5,8), dpi=100, layout = 'tight')
    scatter6_epr = FigureCanvasTkAgg(figure6_epr, sensitivityAnalysis_epr)
    scatter6_epr.get_tk_widget().grid(column = 0, row = 70, columnspan = 4, rowspan = 30)
    ax7_epr = figure6_epr.add_subplot(111)
    
    ax7_epr.set_title('EPR: Land and Water Releases')
    land_epr = ax7_epr.plot(recs, [i/1000 for i in litterAnal_epr], 'b', label = 'EPR: Releases to Land' )
    ax7_epr.set_xlabel('Recycling Rate (%)')
    ax7_epr.set_ylabel('Releases to Land (thousands of tons)', color = 'b')
    ax7_epr.spines['left'].set_color('b')
    ax7_epr.tick_params(axis='y', colors='b')
    global landReleaseDict_epr
    landReleaseDict_epr = dict(zip(recs, litterAnal_epr))
    
    baseLand_epr = ax7_epr.plot(recs, [(litterAnal[i+4]*conditions[1])/1000 for i in range(len(recs))], 'b', linestyle = 'dashed', label = 'Base Case: Releases to Land')

    
    #Creates and places figure
    ax8_epr = ax7_epr.twinx()
    water_epr = ax8_epr.plot(recs, [i/1000 for i in waterAnal_epr], 'r',  label = 'EPR: Releases to Water')
    ax8_epr.set_ylabel('Releases to Water (thousands of tons)', color = 'r')
    ax8_epr.spines['right'].set_color('r')
    ax8_epr.tick_params(axis='y', colors='red')
    global waterReleaseDict_epr
    waterReleaseDict_epr = dict(zip(recs, waterAnal_epr))

    baseWater_epr = ax8_epr.plot(recs, [(waterAnal[i+4]*conditions[1])/1000 for i in range(len(recs))], 'r', linestyle = 'dashed', label = 'Base Case: Releases to Water')
    
    lns = land_epr + water_epr + baseWater_epr + baseLand_epr
    labs = [l.get_label() for l in lns]
    ax7_epr.legend(lns, labs, loc=0)
    
    return

sensButton_epr = Button(sensitivityAnalysis_epr, text = 'Generate Sensitivity Analysis', command = epr_command)
sensButton_epr.grid(column = 0, row = 5, columnspan = 6)

sensErrorLabel_epr = Label(sensitivityAnalysis_epr, bg = 'white', font = fontChoice)
sensErrorLabel_epr.grid(column = 0, row = 3, columnspan = 6)

sensInstruction_epr = Label(sensitivityAnalysis_epr, bg = 'white', text = 'Use slider to display additive releases.', font = ('Helvetica 14 bold'))
sensInstruction_epr.grid(column = 4, row = 3, columnspan = 2, sticky = EW)

#creates figure that will be populated with sensitivity analysis
figure3_epr = plt.Figure(figsize=(10,8), dpi=100, layout = 'tight')
scatter4_epr = FigureCanvasTkAgg(figure3_epr, sensitivityAnalysis_epr)
scatter4_epr.get_tk_widget().grid(column = 0, row = 6, columnspan = 4, rowspan = 30)
ax3_epr = figure3_epr.add_subplot(111)
ax3_epr.set_xlabel('Mechanical Recycling Rate')
ax3_epr.set_ylabel('Plastic Additive Release (tons)')
ax3_epr.set_title('EPR: Additive Release')

figure6_epr = plt.Figure(figsize=(10,8), dpi=100, layout = 'tight')
scatter7_epr = FigureCanvasTkAgg(figure6_epr, sensitivityAnalysis_epr)
scatter7_epr.get_tk_widget().grid(column = 0, row = 70, columnspan = 4, rowspan = 30)
ax7_epr = figure6_epr.add_subplot(111)
ax7_epr.set_xlabel('Mechanical Recycling Rate')
ax7_epr.set_ylabel('Releases to Land')
ax7_epr.set_title('Releases to Land/Water')
ax7_epr.spines['left'].set_color('blue')
ax7_epr.tick_params(axis='y', colors='blue')

ax8_epr = ax7_epr.twinx()
ax8_epr.set_ylabel('Releases to Water')
ax8_epr.spines['right'].set_color('r')
ax8_epr.tick_params(axis='y', colors='red')

n = 0

def epr_slider_changed(event):
    n = float(round(slider_epr.get()))
    print(n)
    
    additiveReleaseValueLabel_epr.config(text = str(sensitivityPoints[n]))
    landReleaseValueLabel_epr.config(text = str(litterAnal_epr[n]))
    waterReleaseValueLabel_epr.config(text = str(waterAnal_epr[n]))
    try:
        additiveReleaseValueLabel_epr.config(text = str(sensitivityPoints[n]))
        landReleaseValueLabel_epr.config(text = str([i/1000 for i in litterAnal_epr][n]))
        waterReleaseValueLabel_epr.config(text = str([i/1000 for i in waterAnal_epr][n]))
        '''
        additiveReleaseValueLabel_epr.config(text = str(round(additiveReleaseDict[i])))
        landReleaseValueLabel_epr.config(text = str(round(landReleaseDict_epr[i])))
        waterReleaseValueLabel_epr.config(text = str(round(waterAnal_epr[i])))
        '''
    except:
        e=0
    
    n = '{: .0f}'.format(n)
    sensAnalSliderValue_epr.config(text = str(n))
    return



#Creates and places slider that will be used to display specific points on sensitivity analysis
slider_epr = ttk.Scale(sensitivityAnalysis_epr, from_ = 0, to = 40, orient = 'horizontal', command = epr_slider_changed)

slider_epr.grid(column = 4, row = 7, columnspan = 2, sticky = EW)


#Creates labels labelling the slider
sliderLowLabel_epr = Label(sensitivityAnalysis_epr, text = '0', bg = 'white')
sliderLowLabel_epr.grid(column = 4, row = 8, sticky = W)


sliderHighLabel_epr = Label(sensitivityAnalysis_epr, text = '40', bg = 'white')
sliderHighLabel_epr.grid(column = 6, row = 8, sticky = W)


#Creates label that will display the value of the slider
sensAnalValueLabel_epr = Label(sensitivityAnalysis_epr, text = 'Mechanical Recycling (Domestic) Rate:  ', font = fontChoice, bg = 'white')
sensAnalValueLabel_epr.configure(anchor = 'center')
sensAnalValueLabel_epr.grid(column = 4, row = 9, sticky = E)

sensAnalSliderValue_epr = Label(sensitivityAnalysis_epr, font= fontChoice, text = '0', bg = 'white', fg = 'green') #Will show the slider's value
sensAnalSliderValue_epr.grid(column = 5, row = 9, sticky = W)

additiveReleaseLabel_epr = Label(sensitivityAnalysis_epr, text = 'Total Additive Release (tons):', font = fontChoice, bg = 'white') #label for where additive release value will go
additiveReleaseLabel_epr.grid(column = 4, row = 10, sticky = E)

additiveReleaseValueLabel_epr = Label(sensitivityAnalysis_epr, font = fontChoice, bg = 'white', fg = 'green') #will display additive release
additiveReleaseValueLabel_epr.grid(column = 5, row = 10, sticky = W)

landReleaseLabel_epr = Label(sensitivityAnalysis_epr, text = 'Release to Land (tons):', font = fontChoice, bg = 'white') #label for where additive release value will go
landReleaseLabel_epr.grid(column = 4, row = 11, sticky = E)

landReleaseValueLabel_epr = Label(sensitivityAnalysis_epr, font = fontChoice, bg = 'white', fg = 'green')
landReleaseValueLabel_epr.grid(column = 5, row = 11, sticky = W)

waterReleaseLabel_epr = Label(sensitivityAnalysis_epr, text = 'Release to water (tons):', font = fontChoice, bg = 'white') #label for where additive release value will go
waterReleaseLabel_epr.grid(column = 4, row = 12, sticky = E)

waterReleaseValueLabel_epr = Label(sensitivityAnalysis_epr, font = fontChoice, bg = 'white', fg = 'green')
waterReleaseValueLabel_epr.grid(column =5, row = 12, sticky = W)



###################################################
def exportToExcel(appList):
    time = datetime.now().strftime("%Y-%m-%d %H%M%S")
    
    indices = [i[0] for i in appList]
    
    tempStreamTRVWList = []
    tempStreamTRVWList.clear()
    
    for i in appList:
        tempStreamTRVWList.append(i[0])
        del i[0]
    
    tempStreamTRVWList.append(streamTitleRows[0])
    del streamTitleRows[0]
    streamSummaryColumns = [str(i) for i in range(1,35)]+['Waste Incinerated 2018', 'Waste Accumulated in Landfill 2018']

    summaryDF = pd.DataFrame(data = [streamTitleRows]+ appList, index = ['Stream Titles'] + indices, columns = streamSummaryColumns)
    
    if appList == streamTRVWLists:
        sheetTitle = "Material Loop 0"
        
    elif appList == mL1TRVWLists:
        sheetTitle = "Material Loop 1"
        
    elif appList == mL2TRVWLists:
        sheetTitle = "Material Loop 2"
    
    elif appList == mL3TRVWLists:
        sheetTitle = "Material Loop 3"
        
    else:
        sheetTitle = "Material Loop 4"
        
    
    try:
        with pd.ExcelWriter("Stream Summary Calculations.xlsx") as writer:
            summaryDF.to_excel(writer, sheet_name = time)  
        return
    except:
        workbook = xlsxwriter.Workbook('Stream Summary Calculations.xlsx')
        with pd.ExcelWriter("Stream Summary Calculations.xlsx") as writer:
            summaryDF.to_excel(writer, sheet_name = time + sheetTitle)  
            
    for i in appList:
        i.append(tempStreamTRVWList[0])
        del tempStreamTRVWList[0]
        
    streamTitleRows.append(tempStreamTRVWList[0])  
    

streamTitleRows = ['Stream Title', 'Monomer/Raw Materials', 'Additives', 'Manufacture GHG Releases', 'Manufacture to Use', 'Additives Migration', 'Use to Collection', 'Collection GHG Emissions', 'Other Waste into Collection', 
                       'Plastic Litter', 'Collection to Sort', 'Nonrecyclable Incinerate: Sort to Incineration', 'Sort to Landfill', 'Sort to Compost', 'Sort to Recycle: Recyclable Nonplastic Waste', 'Sort GHG Emissions', 'Sort to Mechanical Recycling', 'Mechanical Recycling Net GHG Emissions', 
                       'Mechanical Recycling Additive Migration', 'Mechanical Recycling Additive Contamination', 'Plastic: Mechanical Recycling to Manufacture', 'Plastic Import', 'Plastic Re-Export', 'Mechanical Recycling to Incineration', 'Plastic: Sort to Incineration', "Incineration GHG Emissions",
                       'Plastic: Sort to Landfill', 'Plastic Export from Sort', 'Mechanical Recycling to Landfill', 'Landfill Plastic Leak', 'Landfill GHG Emissions', 'Chemical Reprocessing', 'Chemical Reprocessing to Landfill', "Chemical Reprocessing to Incin", 'Chemical Reprocessing Product', '', '']


#function that will open pop up window with stream trvw when button is pressed
def open_popup():
    
    #Creates pop up window with title
   top= Toplevel(streamFrame)
   top.geometry('%dx%d+%d+%d' % (w, h, x, y-25))
   top.title("Stream Calculations")
   
   #Creates and packs stream summary trvw (table)
   streamSummaryTRVW = ttk.Treeview(top)
   streamSummaryTRVW.pack(padx=5, pady=5, fill='both', expand=True,side='top')
   
   #Creates and configures x, then y scrollbar for trvw
   streamSummaryScrollBar = Scrollbar(top, orient = 'horizontal', command = streamSummaryTRVW.xview)
   streamSummaryScrollBar.config(command = streamSummaryTRVW.xview)
   streamSummaryTRVW.configure(xscrollcommand = streamSummaryScrollBar.set)
   
   streamSummaryYScrollBar = Scrollbar(top, orient = 'vertical', command = streamSummaryTRVW.yview)
   streamSummaryYScrollBar.config(command = streamSummaryTRVW.xview)
   streamSummaryTRVW.configure(yscrollcommand = streamSummaryYScrollBar.set)
   
   #packs y scrollbar -- there is some issue here I will return to MJC
   #streamSummaryYScrollBar.pack(side = RIGHT, fill = Y)
   
   #Creates and packs button that will eventually allow data to be exported to excel
   exportButton = Button(top, text = 'Export to Excel', command = lambda: exportToExcel(streamTRVWLists))
   exportButton.pack()
   
   #creates column headings in trvw
   streamSummaryColumns = tuple(['Stream'] + [str(i) for i in range(1,35)]+['Waste Incinerated 2018', 'Waste Accumulated in Landfill 2018'])
   streamSummaryTRVW['columns']=streamSummaryColumns
   streamSummaryTRVW.column('#0', width = 0, stretch = NO)
   for name in streamSummaryColumns:
       streamSummaryTRVW.column(name, width = 250, anchor = CENTER, stretch = NO)
       streamSummaryTRVW.heading(name, text = name)
   

   
    #inserts titles into stream summary trvw

   streamSummaryTRVW.insert(parent ='', index ='end', iid = 0, text = '', values = tuple([streamTitleRows[b] for b in range(len(streamTitleRows))]))
   
   count = 1
   #inserts data into stream summary trvw
   try:
       for i in streamTRVWLists:
           streamSummaryTRVW.insert(parent ='', index ='end', iid = count, text = '', values = tuple([trvwRounder(i[b]) for b in range(len(i))]))
           count +=1
       
       
    #adds stream summary scroll bars
           streamSummaryScrollBar.pack(fill = X)
   except:
           streamSummaryScrollBar.pack(fill = X)

def mL1PopUp():
    
   mL1top = Toplevel(mat_loopTab)
   mL1top.geometry('%dx%d+%d+%d' % (w, h, x, y-25))
   mL1top.title("Material Loop 1 Stream Calculations")
   
   #Creates and packs stream summary trvw (table)
   mL1streamSummaryTRVW = ttk.Treeview(mL1top)
   mL1streamSummaryTRVW.pack(padx=5, pady=5, fill='both', expand=True,side='top')
   
   #Creates and configures x, then y scrollbar for trvw
   mL1streamSummaryScrollBar = Scrollbar(mL1top, orient = 'horizontal', command = mL1streamSummaryTRVW.xview)
   mL1streamSummaryScrollBar.config(command = mL1streamSummaryTRVW.xview)
   mL1streamSummaryTRVW.configure(xscrollcommand = mL1streamSummaryScrollBar.set)
   
   mL1streamSummaryYScrollBar = Scrollbar(mL1top, orient = 'vertical', command = mL1streamSummaryTRVW.yview)
   mL1streamSummaryYScrollBar.config(command = mL1streamSummaryTRVW.xview)
   mL1streamSummaryTRVW.configure(yscrollcommand = mL1streamSummaryYScrollBar.set)
   
   #packs y scrollbar -- there is some issue here I will return to MJC
   #streamSummaryYScrollBar.pack(side = RIGHT, fill = Y)
   
   #Creates and packs button that will eventually allow data to be exported to excel
   exportButton = Button(mL1top, text = 'Export to Excel', command = lambda: exportToExcel(mL1TRVWLists))
   exportButton.pack()
   
   #creates column headings in trvw
   streamSummaryColumns = tuple(['Stream'] + [str(i) for i in range(1,31)]+['Waste Incinerated 2018', 'Waste Accumulated in Landfill 2018'])
   mL1streamSummaryTRVW['columns']=streamSummaryColumns
   mL1streamSummaryTRVW.column('#0', width = 0, stretch = NO)
   for name in streamSummaryColumns:
       mL1streamSummaryTRVW.column(name, width = 250, anchor = CENTER, stretch = NO)
       mL1streamSummaryTRVW.heading(name, text = name)
   
    #inserts titles into stream summary trvw

   mL1streamSummaryTRVW.insert(parent ='', index ='end', iid = 0, text = '', values = tuple([streamTitleRows[b] for b in range(len(streamTitleRows))]))
   
   count = 1
   #inserts data into stream summary trvw
   try:
       for i in mL1TRVWLists:
           mL1streamSummaryTRVW.insert(parent ='', index ='end', iid = count, text = '', values = tuple([trvwRounder(i[b]) for b in range(len(i))]))
           count +=1
       
       
    #adds stream summary scroll bars
           mL1streamSummaryScrollBar.pack(fill = X)
   except:
           mL1streamSummaryScrollBar.pack(fill = X)


def mL2PopUp():
   mL2top = Toplevel(mat_loopTab)
   mL2top.geometry('%dx%d+%d+%d' % (w, h, x, y-25))
   mL2top.title("Material Loop 2 Stream Calculations")
   
   #Creates and packs stream summary trvw (table)
   mL2streamSummaryTRVW = ttk.Treeview(mL2top)
   mL2streamSummaryTRVW.pack(padx=5, pady=5, fill='both', expand=True,side='top')
   
   #Creates and configures x, then y scrollbar for trvw
   mL2streamSummaryScrollBar = Scrollbar(mL2top, orient = 'horizontal', command = mL2streamSummaryTRVW.xview)
   mL2streamSummaryScrollBar.config(command = mL2streamSummaryTRVW.xview)
   mL2streamSummaryTRVW.configure(xscrollcommand = mL2streamSummaryScrollBar.set)
   
   mL2streamSummaryYScrollBar = Scrollbar(mL2top, orient = 'vertical', command = mL2streamSummaryTRVW.yview)
   mL2streamSummaryYScrollBar.config(command = mL2streamSummaryTRVW.xview)
   mL2streamSummaryTRVW.configure(yscrollcommand = mL2streamSummaryYScrollBar.set)
   
   #packs y scrollbar -- there is some issue here I will return to MJC
   #streamSummaryYScrollBar.pack(side = RIGHT, fill = Y)
   
   #Creates and packs button that will eventually allow data to be exported to excel
   exportButton = Button(mL2top, text = 'Export to Excel', command = lambda: exportToExcel(mL2TRVWLists))
   exportButton.pack()
   
   #creates column headings in trvw
   streamSummaryColumns = tuple(['Stream'] + [str(i) for i in range(1,31)]+['Waste Incinerated 2018', 'Waste Accumulated in Landfill 2018'])
   mL2streamSummaryTRVW['columns']=streamSummaryColumns
   mL2streamSummaryTRVW.column('#0', width = 0, stretch = NO)
   for name in streamSummaryColumns:
       mL2streamSummaryTRVW.column(name, width = 250, anchor = CENTER, stretch = NO)
       mL2streamSummaryTRVW.heading(name, text = name)
   
    #inserts titles into stream summary trvw

   mL2streamSummaryTRVW.insert(parent ='', index ='end', iid = 0, text = '', values = tuple([streamTitleRows[b] for b in range(len(streamTitleRows))]))
   
   count = 1
   #inserts data into stream summary trvw
   try:
       for i in mL2TRVWLists:
           mL2streamSummaryTRVW.insert(parent ='', index ='end', iid = count, text = '', values = tuple([trvwRounder(i[b]) for b in range(len(i))]))
           count +=1
       
       
    #adds stream summary scroll bars
           mL2streamSummaryScrollBar.pack(fill = X)
   except:
           mL2streamSummaryScrollBar.pack(fill = X)
   
    
def mL3PopUp():
    
   mL3top = Toplevel(mat_loopTab)
   mL3top.geometry('%dx%d+%d+%d' % (w, h, x, y-25))
   mL3top.title("Material Loop 3 Stream Calculations")
   
   #Creates and packs stream summary trvw (table)
   mL3streamSummaryTRVW = ttk.Treeview(mL3top)
   mL3streamSummaryTRVW.pack(padx=5, pady=5, fill='both', expand=True,side='top')
   
   #Creates and configures x, then y scrollbar for trvw
   mL3streamSummaryScrollBar = Scrollbar(mL3top, orient = 'horizontal', command = mL3streamSummaryTRVW.xview)
   mL3streamSummaryScrollBar.config(command = mL3streamSummaryTRVW.xview)
   mL3streamSummaryTRVW.configure(xscrollcommand = mL3streamSummaryScrollBar.set)
   
   mL3streamSummaryYScrollBar = Scrollbar(mL3top, orient = 'vertical', command = mL3streamSummaryTRVW.yview)
   mL3streamSummaryYScrollBar.config(command = mL3streamSummaryTRVW.xview)
   mL3streamSummaryTRVW.configure(yscrollcommand = mL3streamSummaryYScrollBar.set)
   
   #packs y scrollbar -- there is some issue here I will return to MJC
   #streamSummaryYScrollBar.pack(side = RIGHT, fill = Y)
   
   #Creates and packs button that will eventually allow data to be exported to excel
   exportButton = Button(mL3top, text = 'Export to Excel', command = lambda: exportToExcel(mL3TRVWLists))
   exportButton.pack()
   
   #creates column headings in trvw
   streamSummaryColumns = tuple(['Stream'] + [str(i) for i in range(1,31)]+['Waste Incinerated 2018', 'Waste Accumulated in Landfill 2018'])
   mL3streamSummaryTRVW['columns']=streamSummaryColumns
   mL3streamSummaryTRVW.column('#0', width = 0, stretch = NO)
   for name in streamSummaryColumns:
       mL3streamSummaryTRVW.column(name, width = 250, anchor = CENTER, stretch = NO)
       mL3streamSummaryTRVW.heading(name, text = name)
   
    #inserts titles into stream summary trvw

   mL3streamSummaryTRVW.insert(parent ='', index ='end', iid = 0, text = '', values = tuple([streamTitleRows[b] for b in range(len(streamTitleRows))]))
   
   count = 1
   #inserts data into stream summary trvw
   try:
       for i in mL3TRVWLists:
           mL3streamSummaryTRVW.insert(parent ='', index ='end', iid = count, text = '', values = tuple([trvwRounder(i[b]) for b in range(len(i))]))
           count +=1
       
       
    #adds stream summary scroll bars
           mL3streamSummaryScrollBar.pack(fill = X)
   except:
           mL3streamSummaryScrollBar.pack(fill = X)        

def mL4PopUp():
    
   mL4top = Toplevel(mat_loopTab)
   mL4top.geometry('%dx%d+%d+%d' % (w, h, x, y-25))
   mL4top.title("Material Loop 4 Stream Calculations")
   
   #Creates and packs stream summary trvw (table)
   mL4streamSummaryTRVW = ttk.Treeview(mL4top)
   mL4streamSummaryTRVW.pack(padx=5, pady=5, fill='both', expand=True,side='top')
   
   #Creates and configures x, then y scrollbar for trvw
   mL4streamSummaryScrollBar = Scrollbar(mL4top, orient = 'horizontal', command = mL4streamSummaryTRVW.xview)
   mL4streamSummaryScrollBar.config(command = mL4streamSummaryTRVW.xview)
   mL4streamSummaryTRVW.configure(xscrollcommand = mL4streamSummaryScrollBar.set)
   
   mL4streamSummaryYScrollBar = Scrollbar(mL4top, orient = 'vertical', command = mL4streamSummaryTRVW.yview)
   mL4streamSummaryYScrollBar.config(command = mL4streamSummaryTRVW.xview)
   mL4streamSummaryTRVW.configure(yscrollcommand = mL4streamSummaryYScrollBar.set)
   
   #packs y scrollbar -- there is some issue here I will return to MJC
   #streamSummaryYScrollBar.pack(side = RIGHT, fill = Y)
   
   #Creates and packs button that will eventually allow data to be exported to excel
   exportButton = Button(mL4top, text = 'Export to Excel', command = lambda: exportToExcel(mL4TRVWLists))
   exportButton.pack()
   
   #creates column headings in trvw
   streamSummaryColumns = tuple(['Stream'] + [str(i) for i in range(1,31)]+['Waste Incinerated 2018', 'Waste Accumulated in Landfill 2018'])
   mL4streamSummaryTRVW['columns']=streamSummaryColumns
   mL4streamSummaryTRVW.column('#0', width = 0, stretch = NO)
   for name in streamSummaryColumns:
       mL4streamSummaryTRVW.column(name, width = 250, anchor = CENTER, stretch = NO)
       mL4streamSummaryTRVW.heading(name, text = name)
   
    #inserts titles into stream summary trvw

   mL4streamSummaryTRVW.insert(parent ='', index ='end', iid = 0, text = '', values = tuple([streamTitleRows[b] for b in range(len(streamTitleRows))]))
   
   count = 1
   #inserts data into stream summary trvw
   try:
       for i in mL4TRVWLists:
           mL4streamSummaryTRVW.insert(parent ='', index ='end', iid = count, text = '', values = tuple([trvwRounder(i[b]) for b in range(len(i))]))
           count +=1
       
       
    #adds stream summary scroll bars
           mL4streamSummaryScrollBar.pack(fill = X)
   except:
           mL4streamSummaryScrollBar.pack(fill = X)


#creates frame that will contain buttons for pop up stream spreadsheets
streamFrameButtons = Frame(streamFrame, bg = 'white')
streamFrameButtons.pack(fill = 'x', expand = True, side = 'top')

#Creates buttons that will create pop up buttons
popUpButton = Button(streamFrameButtons, text = "Show Steady State Stream Calculations (Material Loop 0)", command = open_popup)
popUpButton.pack()
#popUpButton.grid(row = 0, column = 0, columnspan = 4)

mL1popUpButton = Button(mat_loopTab, text = 'Show Material Loop 1 Stream Calculations', command = mL1PopUp)
mL2popUpButton = Button(mat_loopTab, text = 'Show Material Loop 2 Stream Calculations', command = mL2PopUp)
mL3popUpButton = Button(mat_loopTab, text = 'Show Material Loop 3 Stream Calculations', command = mL3PopUp)
mL4popUpButton = Button(mat_loopTab, text = 'Show Material Loop 4 Stream Calculations', command = mL4PopUp)

popUpButtonList = [mL1popUpButton, mL2popUpButton, mL3popUpButton, mL4popUpButton]

frameRow = 1
frameColumn = 0

for i in popUpButtonList:
    i.pack()
    

frameColumn = 0
frameRow += 1

flowFrame = tk.Canvas(streamFrame)
flowFrame.pack(fill='both', expand=True,side='top')

img_label = Label(flowFrame)
img_label.pack()

figure_loops = plt.Figure(figsize=(8,5), dpi=120)

loop_scatter = FigureCanvasTkAgg(figure_loops, mat_loopTab)


loop_scatter.get_tk_widget().pack()
ax_loop = figure_loops.add_subplot(111)
ax_loop.set_xlabel('Material Loop Number')
ax_loop.set_ylabel('Plastic Additive Accumulation')
ax_loop.set_title('Additive Accumulation Over Multiple Life Cycles')
###################################################
###Sensitivity Analysis Tab
sensAnalCanvas = Canvas(sensAnalFrame, bg = 'white')

#Creates scrollbar for sensitivity analysis

sensAnalCanvas.pack(side = 'left', fill = 'both', expand = 1)


sensScroll = Scrollbar(sensAnalFrame, orient = 'vertical', command = sensAnalCanvas.yview)
sensScroll.pack(side = 'right', fill = 'y')
sensScroll.config(command=sensAnalCanvas.yview)
sensAnalCanvas.configure(yscrollcommand = sensScroll.set)
sensAnalCanvas.bind('<Configure>', lambda e: sensAnalCanvas.configure(scrollregion = sensAnalCanvas.bbox('all')))

sensitivityAnalysis = Frame(sensAnalCanvas, bg = 'white')
sensAnalCanvas.create_window((0,0), window = sensitivityAnalysis, anchor = 'nw')


sensTitle = tk.Text (sensitivityAnalysis, bg = 'white', height = 2, width = 60, bd = 0)
sensTitle.config(font = ('Helvetica 20 bold'))
sensTitle.insert(tk.INSERT, "Sensitivity Analysis")
sensTitle.tag_configure('center', justify = 'center')
sensTitle.tag_add('center', 1.0, 'end')
sensTitle.config(state = 'disabled')


numCol = 6
rowFrame = 0
sensTitle.grid(column = 0, row = rowFrame, columnspan = numCol)

def showSensAnal():
    sensitivityPoints.clear()
    ghgEmitSA.clear()
    energyFootprintPoints.clear()
    litterAnal.clear()
    waterAnal.clear()
    
    if dataInputQuestionMark():
        sensErrorLabel.config(text = 'Error: Please input all data before generating sensitivity analysis.')
        sensErrorLabel.config(fg = 'red')
        return
    
    
    try: 
        upperLimit = int(sensLimitEntry.get())
    except:
        upperLimit = 72
        
    scatter4.get_tk_widget().grid_forget()
    slider.configure(from_ = 0, to_ = upperLimit)
    
    sliderHighLabel.config(text = str(upperLimit))
    for i in range(1,upperLimit+1):
        global sensNum
        sensNum = i
        conditions[3] = i/100
        conditions[2] = conditions[3]+conditions[5]
        conditions[7] = (1-conditions[2])*(0.158/0.758)
        conditions[8] = 1-conditions[2]-conditions[7]
        makeCalculations(True, [False])
        #assignValues()
        #fillMatFlowAnalSumTRVW()
    assignValues()
    makeCalculations(False, [False])
    
    sensErrorLabel.config(text = '')
    ### line of best fit for additive sensitivity analysis
    x = np.array([i/100 for i in range(1,upperLimit+1)])
    
    #Creating and placing figure
    
    figure3 = plt.Figure(figsize=(8,5), dpi=100)
    scatter3 = FigureCanvasTkAgg(figure3, sensitivityAnalysis)
    scatter3.get_tk_widget().grid(column = 0, row = 6, columnspan = 4, rowspan = 30)
    ax3 = figure3.add_subplot(111)
    
    ax3.plot([i*100 for i in x], sensitivityPoints)
    ax3.set_xlabel('Mechanical Recycling Rate (%)')
    ax3.set_ylabel('Plastic Additive Release (tons)')
    ax3.set_title('Additive Release in Mechanical Recycling')
    global additiveReleaseDict
    additiveReleaseDict = dict(zip(x, sensitivityPoints))

    #Creates and places figure
    
    figure6 = plt.Figure(figsize=(8,5), dpi=100, layout = 'constrained')
    scatter6 = FigureCanvasTkAgg(figure6, sensitivityAnalysis)
    scatter6.get_tk_widget().grid(column = 0, row = 70, columnspan = 4, rowspan = 30)
    ax7 = figure6.add_subplot(111)
    
    land = ax7.plot([i*100 for i in x], litterAnal, 'b', label = 'Releases to Land' )
    ax7.set_xlabel('Mechanical Recycling Rate (%)')
    ax7.set_ylabel('Releases to Land (ton/ton input)')
    ax7.spines['left'].set_color('blue')
    ax7.tick_params(axis='y', colors='blue')
    global landReleaseDict
    landReleaseDict = dict(zip(x, litterAnal))
    

    #Creates and places figure
    ax8 = ax7.twinx()
    water = ax8.plot([i*100 for i in x], waterAnal, 'r', linestyle = 'dashed', label = 'Releases to Water')
    ax8.set_ylabel('Releases to Water (ton/ton input)')
    ax8.set_title('Releases to Land/Water')
    ax8.spines['right'].set_color('r')
    ax8.tick_params(axis='y', colors='red')
    global waterReleaseDict
    waterReleaseDict = dict(zip(x, waterAnal))
    
    lns = land + water
    labs = [l.get_label() for l in lns]
    ax7.legend(lns, labs, loc=0)
    
    
    return

sensButton = Button(sensitivityAnalysis, text = 'Generate Sensitivity Analysis', command = showSensAnal)
sensButton.grid(column = 0, row = 5, columnspan = 6)

sensLimitEntry = Entry(sensitivityAnalysis, width = 50)
sensLimitEntry.grid(column = 3, row = 4, sticky = W)
sensLimitEntry.insert(END, 72)

sensLimitLabel = Label(sensitivityAnalysis, bg = 'white', text = 'Recyclability Upper Limit:', font = fontChoice)
sensLimitLabel.grid(column = 2, row = 4, sticky = E)

sensErrorLabel = Label(sensitivityAnalysis, bg = 'white', font = fontChoice)
sensErrorLabel.grid(column = 0, row = 3, columnspan = 6)

sensInstruction = Label(sensitivityAnalysis, bg = 'white', text = 'Use slider to display additive releases.', font = ('Helvetica 14 bold'))
sensInstruction.grid(column = 4, row = 3, columnspan = 2, sticky = EW)




#creates figure that will be populated with sensitivity analysis
figure3 = plt.Figure(figsize=(8,5), dpi=100, layout = 'tight')
scatter4 = FigureCanvasTkAgg(figure3, sensitivityAnalysis)
scatter4.get_tk_widget().grid(column = 0, row = 6, columnspan = 4, rowspan = 30)
ax3 = figure3.add_subplot(111)
ax3.set_xlabel('Mechanical Recycling Rate (%)')
ax3.set_ylabel('Plastic Additive Release (tons)')
ax3.set_title('Additive Release in Mechanical Recycling')

figure6 = plt.Figure(figsize=(8,5), dpi=100, layout = 'tight')
scatter6 = FigureCanvasTkAgg(figure6, sensitivityAnalysis)
scatter6.get_tk_widget().grid(column = 0, row = 70, columnspan = 4, rowspan = 30)
ax7 = figure6.add_subplot(111)
ax7.set_xlabel('Mechanical Recycling Rate (%)')
ax7.set_ylabel('Releases to Land')
ax7.set_title('Releases to Land/Water')
ax7.spines['left'].set_color('blue')
ax7.tick_params(axis='y', colors='blue')

ax8 = ax7.twinx()
ax8.set_ylabel('Releases to Water')
ax8.spines['right'].set_color('r')
ax8.tick_params(axis='y', colors='red')

n = 0

#Makes slider change cause different display for additive release in mechanical recycling
def slider_changed(event):
    n = float(round(slider.get()))
    try:
        additiveReleaseValueLabel.config(text = str(round(additiveReleaseDict[n/100])))
        landReleaseValueLabel.config(text = str(round(landReleaseDict[n/100], 4)))
        waterReleaseValueLabel.config(text = str(round(waterReleaseDict[n/100], 4)))
        
    except:
        return
    
    n = '{: .0f}'.format(n)
    sensAnalSliderValue.config(text = str(n))
    return


#Creates and places slider that will be used to display specific points on sensitivity analysis
slider = ttk.Scale(sensitivityAnalysis, from_ = 0, to = 72, orient = 'horizontal', command = slider_changed)

slider.grid(column = 4, row = 7, columnspan = 2, sticky = EW)


#Creates labels labelling the slider
sliderLowLabel = Label(sensitivityAnalysis, text = '0', bg = 'white')
sliderLowLabel.grid(column = 4, row = 8, sticky = W)


sliderHighLabel = Label(sensitivityAnalysis, text = '72', bg = 'white')
sliderHighLabel.grid(column = 6, row = 8, sticky = W)


#Creates label that will display the value of the slider
sensAnalValueLabel = Label(sensitivityAnalysis, text = 'Mechanical Recycling (Domestic) Rate:  ', font = fontChoice, bg = 'white')
sensAnalValueLabel.configure(anchor = 'center')
sensAnalValueLabel.grid(column = 4, row = 9, sticky = E)

sensAnalSliderValue = Label(sensitivityAnalysis, font= fontChoice, text = '0', bg = 'white', fg = 'green') #Will show the slider's value
sensAnalSliderValue.grid(column = 5, row = 9, sticky = W)

additiveReleaseLabel = Label(sensitivityAnalysis, text = 'Total Additive Release (tons):', font = fontChoice, bg = 'white') #label for where additive release value will go
additiveReleaseLabel.grid(column = 4, row = 10, sticky = E)

additiveReleaseValueLabel = Label(sensitivityAnalysis, font = fontChoice, bg = 'white', fg = 'green') #will display additive release
additiveReleaseValueLabel.grid(column = 5, row = 10, sticky = W)

landReleaseLabel = Label(sensitivityAnalysis, text = 'Release to Land (tons):', font = fontChoice, bg = 'white') #label for where additive release value will go
landReleaseLabel.grid(column = 4, row = 11, sticky = E)

landReleaseValueLabel = Label(sensitivityAnalysis, font = fontChoice, bg = 'white', fg = 'green')
landReleaseValueLabel.grid(column = 5, row = 11, sticky = W)

waterReleaseLabel = Label(sensitivityAnalysis, text = 'Release to water (tons):', font = fontChoice, bg = 'white') #label for where additive release value will go
waterReleaseLabel.grid(column = 4, row = 12, sticky = E)

waterReleaseValueLabel = Label(sensitivityAnalysis, font = fontChoice, bg = 'white', fg = 'green')
waterReleaseValueLabel.grid(column =5, row = 12, sticky = W)

#MJC out


EoLPlasticgui.mainloop()
