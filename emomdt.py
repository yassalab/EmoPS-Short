'''

Original module         : emodt.py
author         : Derek Delisle
email          : ddelisle@uci.edu
date           : 9/22/2016
status         : In development
usage          : python emodt.py

Short Adaptation:

Creator         : Derek Vinent Taylor
Date            : July 17, 2021
Last Modified   : August 31, 2021


This script runs an instance of the Emotional Discrimination Task.
This task is similar to the regular object task (MST), with the 
difference that images are organized by valence (emotion) and arousal
(intensity) in addition to similarity. Furthermore there are 3 sets of
stimuli to choose from, each one having unique images.

This is a shorter adaptation of the version Developed by Derek Delisle

'''

from __future__ import division
from PIL import ImageFilter, ImageDraw
import numpy as np
import os, sys, math, random, time
workingDir = os.getcwd()
from psychopy.visual import Window, ImageStim, TextStim
from psychopy.visual import Circle
from psychopy.event import clearEvents, getKeys, waitKeys
from psychopy.core import Clock, wait
from psychopy import gui
from PIL import Image

### Variable configuration ###
STIMULI_LOC = 'stimuli'
SET_A_LOC = 'setA'
SET_B_LOC = 'setB'
SET_C_LOC = 'setC'
LOG_LOC = 'logs'
TD_STUDY = 2.5      #Trial duration for study trials
TD_TEST = 2.5       #Trial duration for test trials
ITI = 0.5
IMG_FILL = 0.8
GAUSSIAN_EFFECT = False # Set to True to apply a Gaussian blur to the background

#Directory setup
logDir = os.path.join(workingDir, LOG_LOC)
setADir = os.path.join(workingDir, STIMULI_LOC, SET_A_LOC)
setBDir = os.path.join(workingDir, STIMULI_LOC, SET_B_LOC)
setCDir = os.path.join(workingDir, STIMULI_LOC, SET_C_LOC)

# Task GUI
while (1):
    dialog = gui.Dlg(title="Emotional MDT")
    dialog.addField("Subject Number:", initial="999")
    dialog.addField("Stimuli Set:", initial="A")
    dialog.show()
    subOK = False
    setOK = False
    if gui.OK:
        if dialog.data[0].isdigit():
            subID = int(dialog.data[0])
            subOK = True
        if (dialog.data[1] in (["A", "B", "C"])):
            stimSetSelection = dialog.data[1]
            setOK = True
        if (subOK and setOK):
            break

setDict = {'A': setADir, 'B': setBDir, 'C': setCDir}
imgDir = setDict[stimSetSelection]

class EmoDT(object):

    def __init__(self, subID, logDir, imgDir, tdStudy, tdTest, ITI, imgFill):
        
        #Set passed arguments as class variables
        self.subID = subID
        self.logDir = logDir
        self.imgDir = imgDir
        self.tdStudy = tdStudy
        self.tdTest = tdTest
        self.ITI = ITI
        self.imgFill = imgFill

        #Create class variables/properties
        self.log = self.MakeLog()
        self.studyImgs = self.GetStudyImgs()
        self.testImgs = self.GetTestImgs()
        self.window = Window(fullscr=True, units='pix', color='black', 
                             allowGUI=False)
        if GAUSSIAN_EFFECT:
            self.ApplyGaussianBlur()
        self.circles, self.circText = self.GetIndicators()
        self.imgScale = self.imgFill*min(self.window.size[0],self.window.size[1])
        self.fixCrs = TextStim(self.window, "+", color='White', height=100)
        self.clock = Clock()
        self.scoreList = []
        
        for i in range(0, 3):
            self.scoreList.append([[0,0],[0,0],[0,0],[0,0]])
        random.seed(subID)

    def ApplyGaussianBlur(self):
        """Creates and applies a radial gradient using NumPy for better performance."""
        # Get window size
        colorDistance = 120
        width, height = self.window.size

        # Create a coordinate grid: two 2D arrays for X and Y coordinates
        y, x = np.ogrid[:height, :width]

        # Calculate the center of the screen
        center_x, center_y = width // 2, height // 2

        # Compute the distance from each pixel to the center
        distance = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)

        # Normalize distance to [0, 1] and invert (1 at the edges, 0 in the center)
        max_distance = np.sqrt(center_x ** 2 + center_y ** 2)
        normalized_distance = (distance / max_distance)

        # Scale to 8-bit grayscale (0-255)
        smoothed_distance = normalized_distance ** 2
        gradient_array = (smoothed_distance * colorDistance).astype(np.uint8)
        noise = np.random.normal(0, 5, gradient_array.shape)
        gradient_array = np.clip(gradient_array + noise, 0, colorDistance).astype(np.uint8)

        # Create a PIL image from the NumPy array
        gradient = Image.fromarray(gradient_array, mode='L')

        # Apply a Gaussian blur for smoothness
        blurred_gradient = gradient.filter(ImageFilter.GaussianBlur(radius=30))

        # Create an ImageStim with the blurred gradient
        img_stim = ImageStim(self.window, image=blurred_gradient)

        # Set the blurred gradient as the background image
        self.window.backgroundImage = img_stim
    
    def MakeLog(self):
        """Creates and returns a logfile. Each logfile is named with a
        subject number followed by the stimuli set choice. Also, writes 
        some initial info about the task at the start of the logfile. If
        a given logfile already exists with the same subject and stimset,
        the current one is renamed to an "old" version, timestamped with
        the time it was previously ran.
        """
        sub = int(self.subID)
        imgSet = self.imgDir[-1:]
        logLoc = (self.logDir + "/%d_%s_log.txt" %(sub, imgSet))
        logPath = os.path.normpath(logLoc)

        if (os.path.isfile(logPath)):
            oldLog = open(logPath, 'r')
            line1 =  oldLog.read(32)
            oldLog.close()
            oldTime = line1[12:14] + line1[15:17] + line1[18:20]
            day = line1[24:26] + line1[27:29] + line1[30:32]
            date = day + "_" + oldTime
            oldLogLoc = (self.logDir + "/%d_%s_%s_old.txt" %(sub, imgSet, date))
            oldLogPath = os.path.normpath(oldLogLoc)
            os.rename(logPath, oldLogPath)

        log = open(logPath, 'w')
        logTime = time.strftime("%H:%M:%S on %m-%d-%y", time.localtime())
        log.write("EmoDT Task: %s" %(logTime))
        log.write("\nSubject ID: %d" %(sub))
        log.write("\nUsing set %s" %(imgSet))
        log.write("\nTrial Duration (Study): %.2f" %(self.tdStudy))
        log.write("\nTrial Duration (Test): %.2f" %(self.tdTest))
        log.write("\nITI: %.2f\n\n" %(self.ITI))

        return log

        
    def GetIndicators(self):
        """Creates 5 indicators circles (3 study: neg, neu, pos || 2 test: old,
        new) that will be used as a visual cue for the subject to see which
        response they have chosen. Additionally creates the text inside the
        circles.

        Returns:
            -circles: list of [[circSt1,circSt2,circSt3],[circT1,circT2]]
            -indText: list of [[textSt1,textSt2,textSt3],[textT1,textT2]]
            Note: all element in returned lists are psychopy elements to be drawn
        """
        win = self.window
        hScalar = 0.8
        vScalar = 0.2
        r = 50
        textHeight = 3*r/5

        #Determine the vert/horz positions based on screen size and shrink factor
        horzPosS = hScalar*(win.size[0])
        horzPosT = hScalar*(win.size[1]/4)
        vertPos = -vScalar*(win.size[0]/2)
        posL = (-horzPosT, vertPos)
        posR = (horzPosT, vertPos)
        posC = (0, vertPos)

        #Make the circle and text objects for study (3 choices)
        circS1 = Circle(win, r, lineColor='White', lineWidth=6, pos=posL)
        circS2 = Circle(win, r, lineColor='White', lineWidth=6, pos=posC)
        circS3 = Circle(win, r, lineColor='White', lineWidth=6, pos=posR)
        textS1 = TextStim(win, "Neg", color='White', height=textHeight, pos=posL)
        textS2 = TextStim(win, "Neu", color='White', height=textHeight, pos=posC)
        textS3 = TextStim(win, "Pos", color='White', height=textHeight, pos=posR)

        #Make the circle and text objects for test (2 choices)
        circT1 = Circle(win, r, lineColor='White', lineWidth=6, pos=posL)
        circT2 = Circle(win, r, lineColor='White', lineWidth=6, pos=posR)
        textT1 = TextStim(win, "Old", color='White', height=textHeight, pos=posL)
        textT2 = TextStim(win, "New", color='White', height=textHeight, pos=posR)

        indCircS = [circS1, circS2, circS3]
        indCircT = [circT1, circT2]
        indTextS = [textS1, textS2, textS3]
        indTextT = [textT1, textT2]

        return [indCircS, indCircT], [indTextS, indTextT]

    def GetStudyImgs(self):
        """Creates and returns a list of images to display for the study
        phase of the task. Relevant study images are "a" lures, and repeats,
        which start with 4,5, and 6
        """
        imgDir = self.imgDir
        imgs = []
        for file in os.listdir(imgDir):
            if file.endswith(".jpg"):
                imgs.append(file)

        studyNums = ["4", "5", "6"]
        studyImgs = []
        for img in imgs:
            if ((img[5] == "a") or (img[0] in studyNums)):
                studyImgs.append(img)

        return studyImgs

    def GetTestImgs(self):
        """Creates and returns a list of images to display for the test
        phase of the task. Relevant test images are b,c,d, and e lures as 
        well as repeats (4,5,6) and foils (7,8,9). In other words, any 
        image that is not an "a" lure.
        """
        imgDir = self.imgDir
        imgs = []
        for file in os.listdir(imgDir):
            if file.endswith(".jpg"):
                imgs.append(file)

        testImgs = []
        for img in imgs:
            if ("a" not in img):
                testImgs.append(img)

        return testImgs

    def GetTrialType(self, img):
        """Gets and returns a trial type, for the purpose of writing to
        a logfile, in order to differentiate the different types of trials.
        """
        trialType = ""
        lures = ["a", "b", "c", "d", "e"]
        repeats = {"4":"R-Neg", "5":"R-Neu", "6":"R-Pos"}
        foils = {"7":"F-Neg", "8":"F-Neu", "9":"F-Pos"}
        name = img.split(".")[0]
        if (name[-1:] in lures):
            trialType = "Lure" + name[-1:].upper()
        elif (name[0] in repeats):
            trialType = repeats[name[0]]
        elif (name[0] in foils):
            trialType = foils[name[0]]

        return trialType

    def Pause(self):
        """Pauses the task, and displays a message waiting for a spacebar
        input from the user before continuing to proceed.
        """
        pauseMsg = "Experiment Paused\n\nPress space to continue"
        pauseText = TextStim(self.window, text=pauseMsg, color='White', height=40)
        pauseText.draw(self.window)
        self.window.flip()
        waitKeys(keyList=['space'])
        clearEvents()

    def ScaleImage(self, image):
        """Scales the size of the image to fit as largely as it can within the 
        window of the defined maxSize, while preserving its aspect ratio.

        Args:
            -image: the filename of the image to be scaled
        Return: 
            -scaledSize: maximum scaling of image
        """
        maxSize = self.imgScale
        im = Image.open(image)
        larger = im.size[0]
        if (im.size[0] < im.size[1]):
            larger = im.size[1]
        scale = larger / maxSize
        scale = scale * 2.5
        scaledSize = (im.size[0]/scale, im.size[1]/scale)
        return scaledSize

    def ResetIndicators(self, taskPhase):
        """Resets the all circle indicators to default white state.

        Args:
            -phase:
                0 > resets 3 circles in study phase (neg, neu, pos)
                1 or 2 > reset 2 circles in test phase (old, new)
        """
        phase = 0 if taskPhase == 'Study' else 1
        for circ in self.circles[phase]:
            circ.fillColor = 'Black'
            
    def RunTrial(self, img, trialDur,validKeys):
        """Runs a single trial of the task. This includes displaying an image
        to the screen for a given amount of time, grabbing keypresses and the
        corresponding reaction times, displaying a fixation cross for ITI amount
        of time, then returning the keypress information. If the keypress is 
        space, the experiment is paused. If it is escape, then quit the program.

        Args:
            -img: filename of the image to display
            -trialDur: length of time image stays on screen
        Returns:
            -keyPresses: response and reaction time of the keypress
        """
        phase =  0 if self.phase == "Study" else 1
        circs = self.circles[phase]
        texts = self.circText[phase]        
        imgPath = os.path.normpath(self.imgDir + "/" + img)
        imgSize = self.ScaleImage(imgPath)
        theImage = ImageStim(self.window)
        theImage.setImage(imgPath)
        theImage.setSize(imgSize)
        self.clock.reset()
        clearEvents()
        keyPresses = []

        while self.clock.getTime() < trialDur:
            theImage.draw(self.window)        
            for i in range(len(circs)):
                circs[i].draw(self.window)
                texts[i].draw(self.window)
            self.window.flip()
            key = getKeys(keyList=validKeys, timeStamped=self.clock)    
            if not key:
                continue
            if key[0][0] == 'escape':
                return key[0][0], key[0][1]
            elif key[0][0] == 'space':
                self.Pause()
                return 'P',0
            else:
                self.ResetIndicators(self.phase)
                circs[int(key[0][0])-1].fillColor = 'Green'
                keyPresses.append((key[0][0], key[0][1]))
        self.window.flip()
        self.fixCrs.draw(self.window)
        self.window.flip()
        wait(self.ITI, self.ITI)

        if (not keyPresses):
            return '', 0
        else:
            return keyPresses[0][0], keyPresses[0][1]

    def RunStudy(self):
        """Runs the study phase of the task. During this phase, a trial is 
        run for each of the study images in random order, and for each trial,
        a line of information regarding that trial is written to the logfile.
        """
        log = self.log
        studyMsg = ("%s1%s2%s3\n\nNegative%sNeutral%sPositive"
                    "\n\n\n%sPress space to begin"
                    %(" "*5, " "*18, " "*17, " "*7, " "*7, " "*10))
        studyText = TextStim(self.window, studyMsg, color='White', height=40,
                            wrapWidth=0.8*self.window.size[0])
        studyText.draw(self.window)
        self.window.flip()
        continueKey = waitKeys(keyList=['space', 'escape'])
        if (continueKey[0] == 'escape'):
            log.write("\n\n\n#### Study Not Run ####\n\n\n")
            return
        log.write("\n\nBegin Study\n\n")
        log.write("TrialNum,Image,TrialType,Keypress,RT\n")
        
        studyImgs = self.studyImgs
        trialDur = self.tdStudy
        random.shuffle(studyImgs)
        validKeys = ["1", "2", "3", "escape", "space"]
        for i in range(0, len(studyImgs)):
            img = studyImgs[i]
            tType = self.GetTrialType(img)
            self.ResetIndicators(self.phase)
            (resp, RT) = self.RunTrial(img, trialDur,validKeys)
            if (resp == "escape"):
                log.write("\n### Study Terminated Early ###\n")
                return
            log.write("%d,%s,%s,%s,%.2f\n" %(i+1, img, tType, resp, RT))


    def SetScore(self, trialType, response, valence):
        """Sets 
        """
        resp = int(response)
        i = (int(valence) + 2) % 3
        sim = 0
        if (trialType in ["LureB", "LureD"]):
            sim = 1
        elif (trialType in ["LureC", "LureE"]):
            sim = 2
            
        if (("Lure" in trialType) and ((sim == 1) or (sim == 2))):
            if ((resp == 1) or (resp ==2)):
                self.scoreList[i][sim-1][resp-1] += 1
        elif ("R-" in trialType):
            self.scoreList[i][2][resp-1] += 1
        elif ("F-" in trialType):
            self.scoreList[i][3][resp-1] += 1

    def RunTest(self):
        """Runs the test phase of the task. During this phase, a trial is 
        run for each of the test images in random order, and for each trial,
        a line of information regarding that trial is written to the logfile.
        Additionally, a score (correct/incorrect) is tallied for each type
        of trial to a list of scores by called SetScore()
        """
        log = self.log
        testMsg = ("Have you seen this EXACT image before?\n\n"
                    "%s1%s2\n\n%sYes%sNo\n\n\n\n%sPress space to begin"
                    %(" "*20," "*20," "*20," "*15, " "*15))
        testText = TextStim(self.window, testMsg, color='White', height=40,
                            wrapWidth=0.8*self.window.size[0])
        testText.draw(self.window)
        self.window.flip()
        continueKey = waitKeys(keyList=['space', 'escape'])
        if (continueKey[0] == 'escape'):
            log.write("\n\n\n#### Test Not Run ####\n\n\n")
            return
        log.write("\n\nBegin Test\n\n")
        log.write("TrialNum,Image,TrialType,Valence,Keypress,RT\n")

        testImgs = self.testImgs
        trialDur = self.tdTest
        random.shuffle(testImgs)
        validKeys = ["1", "2", "escape", "space"]
        for i in range(0, len(testImgs)):
            img = testImgs[i]
            val = img[0]
            tType = self.GetTrialType(img)
            self.ResetIndicators(self.phase)
            (resp, RT) = self.RunTrial(img, trialDur,validKeys)
            #resp = str(random.randint(1,2))
            if (resp == "escape"):
                log.write("\n### Test Terminated Early ###\n")
                return
            log.write("%d,%s,%s,%s,%s,%.2f\n" %(i+1, img, tType, val, resp, RT))
            if (resp == "1" or resp == "2"):
                self.SetScore(tType, resp, val)

    def WriteScores(self):
        """Performs a number of simple calculations based on the accrued
        scorelist, and writes them to the logfile. 
        """
        scores = self.scoreList

        def GetProps(cat, cor):
            props = []
            for i in range(0, 3):
                valResp = scores[i][cat][0] + scores[i][cat][1]
                if (valResp == 0):
                    props.append(0)
                else:
                    props.append(scores[i][cat][cor-1] / valResp)
            return props

        propLowFAs = GetProps(0, 1)
        propHighFAs = GetProps(1, 1)
        propLowCRs = GetProps(0, 2)
        propHighCRs = GetProps(1, 2)
        propHits = GetProps(2, 1)
        propMisses = GetProps(2, 2)
        propOldFoils = GetProps(3, 1)
        
        LDI_negLow = propLowCRs[0] - propMisses[0]
        LDI_negHi = propHighCRs[0] - propMisses[0]
        LDI_neuLow = propLowCRs[1] - propMisses[1]
        LDI_neuHi = propHighCRs[1] - propMisses[1]
        LDI_posLow = propLowCRs[2] - propMisses[2]
        LDI_posHi = propHighCRs[2] - propMisses[2]

        LDI_negCol = ((propLowCRs[0] + propHighCRs[0]) / 2) - propMisses[0]
        LDI_neuCol = ((propLowCRs[1] + propHighCRs[1]) / 2) - propMisses[1]
        LDI_posCol = ((propLowCRs[2] + propHighCRs[2]) / 2) - propMisses[2]
        
        self.log.write("\n\n\nScores:\n\n")
        self.log.write("\nLDI-Negative Low Sim: %.2f" %(LDI_negLow))
        self.log.write("\nLDI-Negative High Sim: %.2f" %(LDI_negHi))
        self.log.write("\nLDI-Neutral Low Sim: %.2f" %(LDI_neuLow))
        self.log.write("\nLDI-Neutral High Sim: %.2f" %(LDI_neuHi))
        self.log.write("\nLDI-Positive Low Sim: %.2f" %(LDI_posLow))
        self.log.write("\nLDI-Positive High Sim: %.2f\n\n" %(LDI_posHi))
        self.log.write("\nLDI-Negative Collapsed: %.2f" %(LDI_negCol))
        self.log.write("\nLDI-Neutral Collapsed: %.2f" %(LDI_neuCol))
        self.log.write("\nLDI-Positive Collapsed: %.2f\n\n" %(LDI_posCol))
        
        textRecMem = ['RecMem-Neg','RecMem-Neu','RecMem-Pos']
        for i in range(0, 3):
            propHitVal  = propHits[i] - propOldFoils[i]
            self.log.write("\n%s: %.2f" %(textRecMem[i], propHitVal))

    def EndExp(self):
        """Ends the experiment. Prompts user to press escape, then closes
        the window and logfile.
        """
        exitMsg = "Thanks for participating!\n\nPress Esc to finish"
        exitText = TextStim(self.window, exitMsg, color='White', height=40)
        exitText.draw(self.window)
        self.window.flip()
        waitKeys(keyList=['escape'])
        self.window.close()
        self.log.close()

    def RunTask(self):
        """Runs the task. First runs the study phase, then the test phase.
        After the phases are over, scores are written to the logfile, and
        finally the task finishes.
        """
        self.phase = "Study"
        self.RunStudy()
        self.phase = "Test"
        self.RunTest()
        self.WriteScores()
        self.EndExp()

taskEmoDT = EmoDT(subID, logDir, imgDir, TD_STUDY, TD_TEST, ITI, IMG_FILL)
taskEmoDT.RunTask()