#!/usr/bin/python

import string
import glob
import os
import subprocess
import time

from pickle import dump, load

# Import GTK stuff
import pygtk
import gobject
pygtk.require('2.0')
import gtk

import numpy as np

import LTCTI_Window
import PITCHMAN_Window

class TrackEventsGUI:


    #================== Other Class Methods ================================


    #======================CALLBACKS========================================
    

    #-----------------------------------------------------------------------
    #
    # call back function when the window is closed or when quit button is
    # pressed.
    #
    #-----------------------------------------------------------------------

    def QuitButtonCallback(self, widget,string):
        gtk.main_quit()
        return False

#-------------------------------------------------------------------------------
#
#   GObuttoncallback - Captures all text entry fields.
#                      Determines if this is a test run or for real run;
#                      then determines which event to process
#                      and then calls the appropriate method to process the events.
#
#-------------------------------------------------------------------------------
    def GOButtonCallback(self, widget, data = None):

        # Figure out which radio button the user had clicked upon and bring up
        # the appropriate window.  Or, in the case of "Cancel" do nothing.

        # ---- PITCH CHANGE MANEUVER
        if self.ECbuttonPITCHMAN.get_active() == True:
            PITCHMAN.Pop_UP_MAN_Window()

        # ---- LONG TERM CTI RUN
        elif self.ECbuttonLTCTICAP.get_active() == True:
            LTCTI.Pop_UP_LTCTI_Window()
  
        # ---- SOME OTHER CAP
        #elif self.ECbuttonOTHERCAP.get_active() == True:
        #    OTHERCLD.Pop_UP_OTHERCLD_Window()

        # ----  Some weirdo ANOMALOUS EVENT
#        elif self.ECbuttonANOMALOUSEVENT.get_active() == True:
#            self.ProcessNonCTI(self.Event_Tracking_output_filespec, "Anomaly", date, '---', description, "Final")

    #=======================MAIN=============================================

    def __init__(self):
        self.CLDfile_filespec = ""
        self.CAP_Number = 0
        self.Event_Tracking_output_filespec = "/data/acis/LoadReviews/EventsTrack.txt"

        # 
        # 1111 WINDOW Basic Window Creation - Create a new window
        self.BuildEVENTTRACKERWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # set the title and size of the window.
        self.BuildEVENTTRACKERWindow.set_title("Event Tracker V1.0")
        self.BuildEVENTTRACKERWindow.set_size_request(1000,500)
        self.BuildEVENTTRACKERWindow.set_border_width(10)
        # set a handler for delete event that immediately exits GTK.
        self.BuildEVENTTRACKERWindow.connect("delete_event", self.QuitButtonCallback)

        # 2222 VBOX Create Vertical box to hold the toolbar and the plot
        # The first row will hold the toolbar
        # The second row item will contain the plotting area
        self.BuildEVENTTRACKERWindowBox = gtk.VBox(False, 20)

        # 3333 - EVENT CHOICE RADIO GROUP - create the event choice radio
        #        button group that allows the user to select the event
        # Long Term CTI CAP
        self.ECbuttonLTCTICAP = gtk.RadioButton(None, "Long Term CTI Cap")
        self.ECbuttonLTCTICAP.set_active(False)
        self.BuildEVENTTRACKERWindowBox.pack_start(self.ECbuttonLTCTICAP, False, False, 0)

        # Other CAP
        self.ECbuttonOTHERCAP = gtk.RadioButton(self.ECbuttonLTCTICAP, "Other Cap")
        self.ECbuttonOTHERCAP.set_active(False)
        self.BuildEVENTTRACKERWindowBox.pack_start(self.ECbuttonOTHERCAP, False, False, 0)

        # Pitch Maneuver
        self.ECbuttonPITCHMAN = gtk.RadioButton(self.ECbuttonLTCTICAP, "Maneuver")
        self.ECbuttonPITCHMAN.set_active(False)
        self.BuildEVENTTRACKERWindowBox.pack_start(self.ECbuttonPITCHMAN, False, False, 0)

        # Anomalous Event
        self.ECbuttonANOMALOUSEVENT = gtk.RadioButton(self.ECbuttonPITCHMAN, "Anomalous Event")
        self.ECbuttonANOMALOUSEVENT.set_active(False)
        self.BuildEVENTTRACKERWindowBox.pack_start(self.ECbuttonANOMALOUSEVENT, False, False, 0)
         
        # 5555 - TABLE for Text Entries 
        self.TextEntry_Table = gtk.Table(10,3, True)

        start_row = 0
        start_col = 0

        # -------------------- FOR REAL CANCEL BUTTON -------------------------

        # 5555c - BUTTON  For Real Cancel button
        self.CANCELbutton = gtk.Button("Cancel")
        self.CANCELbutton.connect("clicked", self.QuitButtonCallback, "CANCEL")
        self.TextEntry_Table.attach(self.CANCELbutton,
                                    start_col, start_col + 1,
                                    start_row, start_row + 1)

        # -------------------- SELECT GO BUTTON -------------------------
        start_col = 14
        # 5555c - BUTTON  Go button
        self.GObutton = gtk.Button("Select")
        self.GObutton.connect("clicked", self.GOButtonCallback, "SELECT")
        self.TextEntry_Table.attach(self.GObutton,
                                    start_col, start_col + 1,
                                    start_row, start_row + 1)

        # 5555 - Add the table to the VBOX
        self.BuildEVENTTRACKERWindowBox.pack_start(self.TextEntry_Table)

        # Add the VBox to the window box
        self.BuildEVENTTRACKERWindow.add(self.BuildEVENTTRACKERWindowBox)

        # 1111 Done creating the BuildEVENTTRACKER Window. Show it.
        self.BuildEVENTTRACKERWindow.show_all()



def main():
    #
    # Drop into the GTK infinite loop
    #
    gtk.main()



if __name__ == "__main__":

    # Initialize a number of characteristics

    # Create the GUI

    EVENTTRACKERGUI = TrackEventsGUI()

    # Instance of the Long Term CTI Handler class
    LTCTI = LTCTI_Window.LTCTI()

    # Instance of the "Other" CLD Handler class
#    OTHERCLD = OTHERCLD_Window.OTHERCLD()

    # Instance of the Manueuver Handler class
    PITCHMAN = PITCHMAN_Window.PITCHMAN()

    main()
