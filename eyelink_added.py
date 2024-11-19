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
import os, sys
workingDir = os.getcwd()
from psychopy.core import quit
from psychopy import core, monitors, visual
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
from psychopy import gui , event
import platform
import pylink
from EmoDT import EmoDT
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
GAUSSIAN_EFFECT = True # Set to True to apply a Gaussian blur to the background
dummy_mode = True # Set to True to run in dummy mode
full_screen = True # Set to True to run in full screen mode



#Directory setup
logDir = os.path.join(workingDir, LOG_LOC)
setADir = os.path.join(workingDir, STIMULI_LOC, SET_A_LOC)
setBDir = os.path.join(workingDir, STIMULI_LOC, SET_B_LOC)
setCDir = os.path.join(workingDir, STIMULI_LOC, SET_C_LOC)


use_retina = True
# For macOS users check if they have a retina/H screen
if 'Darwin' in platform.system():
    dlg = gui.Dlg("Retina Screen?")
    dlg.addText("What type of screen will the experiment run on?")
    dlg.addField("Screen Type", choices=["High Resolution (Retina, 2k, 4k, 5k)", "Standard Resolution (HD or lower)"])
    # show dialog and wait for OK or Cancel
    ok_data = dlg.show()
    if dlg.OK:
        if dlg.data[0] == "High Resolution (Retina, 2k, 4k, 5k)":  
            use_retina = True
        else:
            use_retina = False
    else:
        print('user cancelled')
        quit()
        sys.exit()


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


# step 1: connect to the eyelink host pc
#
# the host ip address, by default, is "100.1.1.1".
# the "el_tracker" objected created here can be accessed through the pylink
# set the host pc address to "none" (without quotes) to run the script
# in "dummy mode"
if dummy_mode:
    el_tracker = pylink.eyelink(None)
else:
    try:
        el_tracker = pylink.eyelink("100.1.1.1")
    except RuntimeError as error:
        print('error:', error)
        core.quit()
        sys.exit()

# step 2: open an edf data file on the host pc
edf_file = subID + ".edf"
try:
    el_tracker.opendatafile(edf_file)
except RuntimeError as err:
    print('error:', err)
    # close the link if we have one open
    if el_tracker.isconnected():
        el_tracker.close()
    core.quit()
    sys.exit()

# add a header text to the edf file to identify the current experiment name
# this is optional. if your text starts with "recorded by " it will be
# available in dataviewer's inspector window by clicking
# the edf session node in the top panel and looking for the "recorded by:"
# field in the bottom panel of the inspector.
preamble_text = 'recorded by %s' % os.path.basename(__file__)
el_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)

# Step 3: Configure the tracker
#
# Put the tracker in offline mode before we change tracking parameters
el_tracker.setOfflineMode()

# Get the software version:  1-EyeLink I, 2-EyeLink II, 3/4-EyeLink 1000,
# 5-EyeLink 1000 Plus, 6-Portable DUO
eyelink_ver = 0  # set version to 0, in case running in Dummy mode
if not dummy_mode:
    vstr = el_tracker.getTrackerVersionString()
    eyelink_ver = int(vstr.split()[-1].split('.')[0])
    # print out some version info in the shell
    print('Running experiment on %s, version %d' % (vstr, eyelink_ver))

# File and Link data control
# what eye events to save in the EDF file, include everything by default
file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
# what eye events to make available over the link, include everything by default
link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
# what sample data to save in the EDF data file and to make available
# over the link, include the 'HTARGET' flag to save head target sticker
# data for supported eye trackers
if eyelink_ver > 3:
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
else:
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)

# Optional tracking parameters
# Sample rate, 250, 500, 1000, or 2000, check your tracker specification
# if eyelink_ver > 2:
#     el_tracker.sendCommand("sample_rate 1000")
# Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
el_tracker.sendCommand("calibration_type = HV9")
# Set a gamepad button to accept calibration/drift check target
# You need a supported gamepad/button box that is connected to the Host PC
el_tracker.sendCommand("button_function 5 'accept_target_fixation'")

# Step 4: set up a graphics environment for calibration
#
# Open a window, be sure to specify monitor parameters
mon = monitors.Monitor('myMonitor', width=53.0, distance=70.0)
win = visual.Window(fullscr=full_screen,
                    monitor=mon,
                    winType='pyglet',
                    units='pix')

# get the native screen resolution used by PsychoPy
scn_width, scn_height = win.size
# resolution fix for Mac retina displays
if 'Darwin' in platform.system():
    if use_retina:
        scn_width = int(scn_width/2.0)
        scn_height = int(scn_height/2.0)

# Pass the display pixel coordinates (left, top, right, bottom) to the tracker
# see the EyeLink Installation Guide, "Customizing Screen Settings"
el_coords = "screen_pixel_coords = 0 0 %d %d" % (scn_width - 1, scn_height - 1)
el_tracker.sendCommand(el_coords)

# Write a DISPLAY_COORDS message to the EDF file
# Data Viewer needs this piece of info for proper visualization, see Data
# Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
dv_coords = "DISPLAY_COORDS  0 0 %d %d" % (scn_width - 1, scn_height - 1)
el_tracker.sendMessage(dv_coords)

# Configure a graphics environment (genv) for tracker calibration
genv = EyeLinkCoreGraphicsPsychoPy(el_tracker, win)
print(genv)  # print out the version number of the CoreGraphics library

# Set background and foreground colors for the calibration target
# in PsychoPy, (-1, -1, -1)=black, (1, 1, 1)=white, (0, 0, 0)=mid-gray
foreground_color = (-1, -1, -1)
background_color = win.color
genv.setCalibrationColors(foreground_color, background_color)

# Set up the calibration target
#
# The target could be a "circle" (default), a "picture", a "movie" clip,
# or a rotating "spiral". To configure the type of calibration target, set
# genv.setTargetType to "circle", "picture", "movie", or "spiral", e.g.,
# genv.setTargetType('picture')
#
# Use gen.setPictureTarget() to set a "picture" target
# genv.setPictureTarget(os.path.join('images', 'fixTarget.bmp'))
#
# Use genv.setMovieTarget() to set a "movie" target
# genv.setMovieTarget(os.path.join('videos', 'calibVid.mov'))

# Use a picture as the calibration target
genv.setTargetType('picture')
genv.setPictureTarget(os.path.join('images', 'fixTarget.bmp'))

# Configure the size of the calibration target (in pixels)
# this option applies only to "circle", "spiral", and "movie" targets
# genv.setTargetSize(24)

# Beeps to play during calibration, validation and drift correction
# parameters: target, good, error
#     target -- sound to play when target moves
#     good -- sound to play on successful operation
#     error -- sound to play on failure or interruption
# Each parameter could be ''--default sound, 'off'--no sound, or a wav file
genv.setCalibrationSounds('', '', '')

# resolution fix for macOS retina display issues
if use_retina:
    genv.fixMacRetinaDisplay()

# Request Pylink to use the PsychoPy window we opened above for calibration
pylink.openGraphicsEx(genv)

def clear_screen(win):
    """ clear up the PsychoPy window"""

    win.fillColor = genv.getBackgroundColor()
    win.flip()

def show_msg(win, text, wait_for_keypress=True):
    """ Show task instructions on screen"""

    msg = visual.TextStim(win, text,
                          color=genv.getForegroundColor(),
                          wrapWidth=scn_width/2)
    clear_screen(win)
    msg.draw()
    win.flip()

    # wait indefinitely, terminates upon any key press
    if wait_for_keypress:
        event.waitKeys()
        clear_screen(win)


# Step 5: Set up the camera and calibrate the tracker

# Show the task instructions
task_msg = 'In the task, you may press the SPACEBAR to end a trial\n' + \
    '\nPress Ctrl-C to if you need to quit the task early\n'
if dummy_mode:
    task_msg = task_msg + '\nNow, press ENTER to start the task'
else:
    task_msg = task_msg + '\nNow, press ENTER twice to calibrate tracker'
show_msg(win, task_msg)

# skip this step if running the script in Dummy Mode
if not dummy_mode:
    try:
        el_tracker.doTrackerSetup()
    except RuntimeError as err:
        print('ERROR:', err)
        el_tracker.exitCalibration()

# Step 6: Run the experimental trials


setDict = {'A': setADir, 'B': setBDir, 'C': setCDir}
imgDir = setDict[stimSetSelection]


taskEmoDT = EmoDT(subID, logDir, imgDir, TD_STUDY, TD_TEST, ITI, IMG_FILL,GAUSSIAN_EFFECT)
taskEmoDT.RunTask()