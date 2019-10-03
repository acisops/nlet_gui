#!/usr/bin/python
################################################################################
#
# Class LTCTI - CLass of attributes and functions that acquires associated 
#             parameters, makes necessary calculations and creates an entry
#             for the Non-Load Event Tracker
#
################################################################################
import gtk
import os
import subprocess

class LTCTI:

    # The Constructor
    def __init__(self):
        """
        This is the constructor for the LTCTI Window manager. Not a whole
        lot happens here. We define the LTCTI RTS file names and the 
        default current folder that Contains the Tracking Files to be
        written to. 


        NonLoadTrackedEventsHeader.txt is the official for-score file

        TEST_NonLoadTrackedEvents.txt is a play pen file used for testing and What-if
        runs

        """
        # Widgets
        self.DATE_entry = gtk.Entry(max=0)

        self.start_date = ""
        self.stop_date = ""
        self.start_time = 0.0
        self.stop_time = 0.0
        self.default_current_folder = "/data/acis/LoadReviews/"

        self.number_of_chips = 6
        self.LTCTI_RTS_4 = '1_4_CTI'
        self.LTCTI_RTS_5 = '1_5_CTI'
        self.LTCTI_RTS_6 = '1_CTI06'
        self.LTCTI_selected = self.LTCTI_RTS_6  # Default to 6 chips
        self.LTCTI_duration = '000:01:00:00'    # Default to one hour

        self.cap_number = None

        # Initialize the Command to be recorded.
        self.RNLE_command_list = [ '/proj/sot/ska3/flight/bin/python', '/data/acis/LoadReviews/script/NONLOADEVENTTRACKER/RecordNonLoadEvent.py', 'LTCTI', '--source', 'NLET']

#-----------------------------------------------------------------------
#
# LTCTIcallback - call back function when TEST, CANCEL or SCORE buttons
#                 are pressed
#
#-----------------------------------------------------------------------
    def LTCTIcallback(self, widget, string):
        """
        LTCTIcallback is the callback that is called when the user pushes either 
        the SCORE, CANCEL or TEST pushbottons at the bottom of the screen. 

        If CANCEL was pushed the callback exits immediately with no effects.

        If either TEST or SCORE buttons were pushed, then the user-supplied data
        is obtained from the GUI and a call is made to RecordNonLoadEvent.py which
        writes an event entry in the specified Tracking File.  If SCORE was
        pressed then the event is written to the official NLT file:

        NonLoadTrackedEventsHeader.txt

        If TEST was selected then the user is prompted to select a destination
        file via a File Chooser pop-up. An extra switch (-t) and the file path
        is appended to the NLET command being built.

        When all data has been collected the NLET command is complete.  That 
        command issues a call to RecordNonLoadEvent.py which records the event
        in the appropriate file.

        When the SCORE, CANCEL or TEST button has been clicked, the LTCTI pop-up
        is destroyed.
        """
        # CAP execution start time
        self.start_date = self.DATE_entry.get_text()
        # CAP number
        self.cap_number = self.CAP_Number_entry.get_text()
        # Duration of the CAP if it ran to completion
        self.LTCTI_duration = self.LTCTI_Duration_entry.get_text()

        # Now get whatever the user put in the comment field if anything
        user_comments_buffer = self.UserComment_entry.get_buffer()
        tstart = user_comments_buffer.get_start_iter()
        tend = user_comments_buffer.get_end_iter()
          
        user_comment = user_comments_buffer.get_text(tstart, tend)

        # CANCEL was pressed so do nothing and destroy the window destroy the window
        if (string != "CANCEL"):
            self.BuildLTCTIWindow.destroy()

            # Either SCORE or TEST was pressed so process accordingly
            # Set up the output file depending upon whether this is for score
            # or just a test run
            if (string == 'TEST'):
                # STRING == TEST so this is for TEST PURPOSES and a test 
                # file will be written to a user-selected file
   
                # Pop up a file chooser for the user so that they can select the file
                # to write to
                # Here are the file filters used with the filechoosers
                TEST_NLET_file_filter=gtk.FileFilter()
                TEST_NLET_file_filter.set_name(".txt files")
                TEST_NLET_file_filter.add_pattern("*.txt")
                all_filter=gtk.FileFilter()
                all_filter.set_name("All files")
                all_filter.add_pattern("*")
        
                # Create the dialog but do not show it yet
                self.TEST_NLET_FILESelectordialog = gtk.FileChooserDialog(title="Select the TXT File",
                                                                 action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                                                 buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                                                          gtk.STOCK_OPEN, gtk.RESPONSE_OK))
         
                # Capture the name of the file selected
                # Set the default folder
                self.TEST_NLET_FILESelectordialog.set_current_folder(self.default_current_folder)
                self.TEST_NLET_FILESelectordialog.add_filter(TEST_NLET_file_filter)
                self.TEST_NLET_FILESelectordialog.add_filter(all_filter)
         
                # Run the dialog and get the response
                response = self.TEST_NLET_FILESelectordialog.run()
        
                if response == gtk.RESPONSE_OK:
                    # User specified a file; capture it's name
                    self.TEST_NLET_file_filespec = self.TEST_NLET_FILESelectordialog.get_filename()
        
                elif response == gtk.RESPONSE_CANCEL:
                    print 'Cancel Clicked'
        
                # Done with the file chooser - get rid of it
                self.TEST_NLET_FILESelectordialog.destroy()
        
                # Now tack the -t switch and the path to the TEST file
                # Onto the command.
                self.RNLE_command_list.extend(['-t', self.TEST_NLET_file_filespec])
    
            # Now form the rest of the RecordNonLoadEvent.py command using the
            # data extracted from the GUI page
            if (string == "SCORE") or (string == "TEST"):
    
                # --------------- DATE ------------------------------------------    
                if self.start_date == "":
                    print "NO START TIME SPECIFIED!!!"
                else:
                    # Concatenate the  time of the event
                    self.RNLE_command_list.extend(['--event_time', self.start_date])
    
                # --------------- CAP NUMBER -----------------------------------
                # Next append the CAP number. NOTE that it is a string at 
                # point and concatenate it to the command
                self.RNLE_command_list.extend(['--cap_num', self.cap_number])
    
                # --------------- NUMBER OF CHIPS -------------------------------
                # Determine which chip count radio button was selected and
                # set the self.LTCTI_selected variable to the appropriate
                # RTS file name
                if self.radio_button_6.get_active():
                    self.LTCTI_selected = self.LTCTI_RTS_6
                    
                elif self.radio_button_5.get_active():
                    self.LTCTI_selected = self.LTCTI_RTS_5

                else:
                    self.LTCTI_selected = self.LTCTI_RTS_4
    
                # Now append the switch and the selected RTS file name to the 
                # RecordNonLoadEvent command arg list
                self.RNLE_command_list.extend(['--RTS_file', self.LTCTI_selected])

                # Now tack on the LTCTI duration
                # Put the number of hours in the RTS FOT Request format of:
                # DDD:HH:MM:SS
                # Convert the hours to seconds
                secs = float(self.LTCTI_duration)*3600.
                # Obtain the minutes and seconds divmod
                m,s = divmod(secs, 60)
                # Now obtain the hours and minutes divmod
                h, m = divmod(m, 60)
                # And finally days and hours
                days, h = divmod(h, 24)
                # Now form the string in FOT Request format
                duration = str(int(days)).zfill(3)+':'+str(int(h)).zfill(2)+":%02d:%02d" % (  m, s)
                # And then tack it on to the end of the NLET command
                self.RNLE_command_list.extend(['--LTCTI_duration', duration])
    
    
                # -------------- COMMENT -----------------------------------------
                # If the user did not supply a command, create one
                if user_comment == "":
                    print "USER SUPPLIED NO COMMENT"
                    user_comment = "No Comment"
    

                # Now append the comment  to the argument list
                self.RNLE_command_list.extend(['--desc', user_comment])
    
            # Now that you have the command line built - execute it
            try:
                print('\nRecording the LTCTI event:')
                x = subprocess.Popen(self.RNLE_command_list)
                # Now reset the command list to the base command
                self.RNLE_command_list = [ '/proj/sot/ska3/flight/bin/python', '/data/acis/LoadReviews/script/NONLOADEVENTTRACKER/RecordNonLoadEvent.py', 'LTCTI', '--source', 'NLET']

            except:
                print('\n PROBLEM: Writing the LTCTI event to the Non Load Event Tracking File failed.')

            print('\nLTCTI_window: Finished the NLET file update')
    
        # Done with the window so destroy it
        self.BuildLTCTIWindow.destroy()
        return False


    def Pop_UP_LTCTI_Window(self):


        """
        This method builds the LTCTI popup when the user has selected that
        option from the Main Menu. Data that is necessary for an entry in
        the NLET system is supplied by the user after the pop-up appears.
        
        """

        # 1111 -  Create the Basic window
        self.BuildLTCTIWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # set the title and size of the window.
        self.BuildLTCTIWindow.set_title("Long Term CTI Run")
        self.BuildLTCTIWindow.set_size_request(1000,700)
        self.BuildLTCTIWindow.set_border_width(10)

        # 2222 VBOX Create Vertical box to hold the toolbar and the plot
        # The first row will hold the toolbar
        # The second row item will contain the plotting area
        self.LTCTI_VBox = gtk.VBox(False, 20)

        # 3333 - Create a TABLE for textual entries and buttons
        self.TextEntry_Table = gtk.Table(15,15, True)

        start_row = 0
        start_col = 0

        # ------------------------------- DATE --------------------------------------
        # 4444 - LABEL - DATE
        row_len = 1
        col_len = 5
        self.DATE_label = gtk.Label("CAP Execution Date (2018:071:17:32:00): ")
        self.TextEntry_Table.attach(self.DATE_label, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        start_col += col_len

        row_len = 1
        col_len = 5
        # 4444a -  TEXT ENTRY - DATE
#        self.DATE_entry = gtk.Entry(max=0)
        self.DATE_entry.set_text("")
        self.TextEntry_Table.attach(self.DATE_entry,
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)


        # -------------------------- CAP Number  --------------------------------------
        # 5555b - LABEL - CAP number
        start_row += row_len
        start_col = 1
        row_len = 1
        col_len = 2
        self.CAPNumber_label = gtk.Label("CAP Number: ")
        self.TextEntry_Table.attach(self.CAPNumber_label, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        start_col += col_len
        row_len = 1
        col_len = 1
        # 5555b -  TEXT ENTRY - CAP Number Text Entry Field
        self.CAP_Number_entry = gtk.Entry(max=0)
        self.CAP_Number_entry.set_text("")
        self.TextEntry_Table.attach(self.CAP_Number_entry,
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        # -------------------- NUMBER OF CHIPS  -------------------------
        # 5555c - LABEL - 
        start_row += row_len
        start_col = 0
        row_len = 1
        col_len = 3
        self.CLDFileName_label = gtk.Label("Select the number of chips: ")
        self.TextEntry_Table.attach(self.CLDFileName_label, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)
        start_col += col_len
        row_len = 1
        col_len = 2
        # 5555c -  RADIO BUTTON 6 CHIPS -
        self.radio_button_6 = gtk.RadioButton(group=None, label='6 chips')
        self.radio_button_6.set_active(True)
        self.TextEntry_Table.attach(self.radio_button_6, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        start_col += col_len
        row_len = 1
        col_len = 2
 
        # 5555c -  RADIO BUTTON 5 CHIPS -
        self.radio_button_5 = gtk.RadioButton(group=self.radio_button_6, label='5 chips')
        self.radio_button_5.set_active(False)
        self.TextEntry_Table.attach(self.radio_button_5, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        start_col += col_len
        row_len = 1
        col_len = 2
 
        # 5555c -  RADIO BUTTON 4 CHIPS -
        self.radio_button_4 = gtk.RadioButton(group=self.radio_button_6, label='4 chips')
        self.radio_button_4.set_active(False)
        self.TextEntry_Table.attach(self.radio_button_4, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)


        # 5555c -  LTCTI CAP DURATION
        start_row += row_len+1
        start_col = 0
        row_len = 1
        col_len = 4

        self.RTS_duration_label = gtk.Label("LTCTI Duration (WHOLE HOURS): ")
        self.TextEntry_Table.attach(self.RTS_duration_label, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        start_col =+ col_len
        row_len = 1
        col_len = 1
        # 5555d -  TEXT ENTRY - LTCTI DURATION
        self.LTCTI_Duration_entry = gtk.Entry(max=0)
        self.LTCTI_Duration_entry.set_text("")
        self.TextEntry_Table.attach(self.LTCTI_Duration_entry,
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        # -------------------- USER COMMENT -------------------------
        # 4444d - LABEL - User Comment Label
        start_row += row_len+1
        start_col = 0
        row_len = 1
        col_len = 3

        self.CLDFileName_label = gtk.Label("User Comment: ")
        self.TextEntry_Table.attach(self.CLDFileName_label, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        start_col =+ col_len
        row_len = 4
        col_len = 9
        # 4444d -  TEXT ENTRY - User Comment Text Entry field 
        self.UserComment_entry = gtk.TextView()
        self.TextEntry_Table.attach(self.UserComment_entry,
                                    start_col, start_col+col_len,
                                    start_row, start_row+1)


        # -------------------- SCORE BUTTON -------------------------
        start_row = 14
        start_col = 0
        # 4444c - BUTTON  For Real SCORE button
        self.SCOREbutton = gtk.Button("SCORE")
        self.SCOREbutton.connect("clicked", self.LTCTIcallback, "SCORE")
        self.TextEntry_Table.attach(self.SCOREbutton,
                                    start_col, start_col + 2,
                                    start_row, start_row + 1)

        # -------------------- CANCEL BUTTON -------------------------
        start_row = 14
        start_col = 11
        # 4444c - BUTTON  CANCEL button
        self.CANCELbutton = gtk.Button("CANCEL")
        self.CANCELbutton.connect("clicked", self.LTCTIcallback, "CANCEL")
        self.TextEntry_Table.attach(self.CANCELbutton,
                                    start_col, start_col + 2,
                                    start_row, start_row + 1)

        # -------------------- TEST BUTTON -------------------------
        start_row = 14
        start_col = 13
        # 4444c - BUTTON  TEST button
        self.TESTbutton = gtk.Button("TEST")
        self.TESTbutton.connect("clicked", self.LTCTIcallback, "TEST")
        self.TextEntry_Table.attach(self.TESTbutton,
                                    start_col, start_col + 1,
                                    start_row, start_row + 1)

        # 2222 - Add the table to the VBOX
        self.LTCTI_VBox.pack_start(self.TextEntry_Table)

        # Add the VBox to the window box
        self.BuildLTCTIWindow.add(self.LTCTI_VBox)


        # 1111 - Done creating the BuildEVENTTRACKER Window. Show it.
        self.BuildLTCTIWindow.show_all()
