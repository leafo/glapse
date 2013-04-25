#!/usr/bin/env python
# -*- coding: utf-8  -*-

###############################################################################
# This file is part of gLapse.                                                #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# any later version.                                                          #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
# Copyright (C) 2011, David Saltares Márquez, <david.saltares@gmail.com>      #
###############################################################################

import threading
import os
import time
import re

from gettext import gettext as _

# quote shell argument
def q(s):
    return "'" + s.replace("'", "'\\''") + "'"

class GlapseMain:
    def __init__(self):
        self.outputDir = os.getenv('HOME')
        self.quality = 80
        self.interval = 10
        self.numDigits = 9
        self.currentShot = 0
        self.done = True
        self.captureWebcam = True
    
    def startScreenshots(self, output, quality, interval):
        print 'Starting taking screenshots...'
        print 'Output folder: ' + output
        print 'Quality: ' + str(quality)
        print 'Interval: ' + str(interval)
        
        # Update attributes
        self.outputDir = output
        self.quality = quality
        self.interval = interval
        self.currentShot = 0
        
        # Start a thread to take screenshots
        self.done = False
        self.thread = threading.Thread(target = self._takeScreenshot)
        self.thread.start()
        
        
    def stopScreenshots(self):
        print 'Stopped taking screenshots.'
        self.done = True
        self.thread.join()
        
        
    def makeVideo(self, gui, inputFolder, outputFile, FPS):
        # Build ffmpeg command
        command = 'ffmpeg -y -r ' + str(FPS) + ' -f image2 -i ' + inputFolder + os.sep + '%0' + str(self.numDigits) + 'd.jpg ' + outputFile
        
        if len(outputFile) <= 4 or outputFile[-4:] != ".avi":
            command = command + '.avi'
        
        print command
        
        # Create thread to run command
        videoThread = threading.Thread(target = self._makeVideoThread, args = (command, gui))
        videoThread.start()
        
    
    def getPossibleOverwrite(self, output):
        regex = re.compile('[0-9]{' + str(self.numDigits) + '}.jpg')
        
        for f in os.listdir(output):
            match = regex.match(f)
            if match != None:
                return True
        
        return False

    def _filePath(self, name):
        return self.outputDir + os.sep + name

    def _takeScreenshot(self):
        # Run until were done
        while not self.done:
            # Build scrot command
            baseName = "%09d" % (self.currentShot)
            fileName = baseName + '.png'
            filePath = self._filePath(fileName)
            
            command = 'scrot -q ' + str(self.quality) + ' ' + q(filePath)
            
            print 'Taking screenshot: ' + command + '...'
            
            os.system(command)

            if self.captureWebcam:
                webcamFilePath = self._filePath(baseName + "_webcam.jpg")
                webcamCommand = "fswebcam --no-banner %s" % q(webcamFilePath)

                print 'Capturing webcam: ' + webcamCommand + '...'
                os.system(webcamCommand)

                combiendFilePath = self._filePath(baseName + "_combined.png")
                combineCommand = "composite -gravity SouthEast -geometry +10+10 \( %s -resize 600x330 \) %s %s" % (q(webcamFilePath), q(filePath), q(combiendFilePath))

                print "Combining webcam: " + combineCommand + "..."
                os.system(combineCommand)


            # Schedule next screenshot
            print 'Scheduling next screenshot...'
            self.currentShot = self.currentShot + 1
            time.sleep(self.interval)

    def _makeVideoThread(self, command, gui):
        # Make call system
        os.system(command)
        
        # Change GUI status
        gui.onMakeVideoFinished()
