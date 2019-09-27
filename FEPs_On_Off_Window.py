################################################################################
#
# Class MAN - CLass of attributes and functions that acquires associated 
#             parameters, makes necessary calculations and creates an entry
#             for the Non-Load Event Tracker
#
#
# Update: October 11, 2017
#         Gregg Germain
#         - Removed Pitch and Roll GUI entries
#         - Replaced them with a calculation for pitch and roll (TB_DONE)
#
################################################################################
import gtk
import os
import subprocess

class FEPs_On_Off_Window_class:

    # The Constructor
    def __init__(self):

        self.default_current_folder = "/data/acis/LoadReviews/"

        self.exec_date = "1900:000:00:01:00.00"
        self.cap_number = None

        self.FEP_command = None

        # Initialize the Command to be recorded.
        self.RNLE_command_list = [ '/proj/sot/ska3/flight/bin/python', '/data/acis/LoadReviews/script/NONLOADEVENTTRACKER/RecordNonLoadEvent.py']

#-----------------------------------------------------------------------
#
# FEPs_ON_OFF_Callback - call back function when TEST, CANCEL or SCORE buttons
#               are pressed
#
#-----------------------------------------------------------------------
    def FEPs_ON_OFF_callback(self, widget, string):
        """
        FEPs_ON_OFF_callback is the callback that is called when the user pushes either 
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

        When the SCORE, CANCEL or TEST button has been clicked, the FEPs_ON_OFF
        pop-up is destroyed.

        RecordNonLoadEvent command format (for WSPOW0002A):

        RecordNonLoadEvent.py  WSPOW0002A  --source NLET  --event_time 2019:256:17:54:00  --cap_num 9875  --desc "some comment" 

        """
        # First thing we are going to do is gather all the data from the 
        # pop-up window.
        
        # Execution start time of the FEPs_ON_OFF CAP 
        self.start_date = self.DATE_entry.get_text()

        # CAP number
        self.cap_number = self.CAP_Number_entry.get_text()

        # Get the text fromthe User comment buffer
        user_comments_buffer = self.UserComment_entry.get_buffer()
        tstart = user_comments_buffer.get_start_iter()
        tend = user_comments_buffer.get_end_iter()
        user_comment = user_comments_buffer.get_text(tstart, tend)

        # CANCEL was pressed so do nothing and destroy the window destroy the window
        if (string != "CANCEL"):

            # Either SCORE or TEST was pressed so process accordingly
            # Set up the output file depending upon whether this is for score
            # or just a test run
            if (string == "TEST"):
                # Usere selection is neither CANCEL nor SCORE.
                #
                # User must have clicked on TEST
                # STRING == TEST so this is for TEST PURPOSES and the
                # output will be written to a user-selected file
   
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
    
                # --------------- COMMAND ---------------------------------
                # ---- First find out which of the command buttons was active
                if self.WSPOW00000_Button.get_active() == True:
                    self.FEP_command = 'WSPOW00000'

                # ---- And else would have worked here but other FEP commands
                #      may be added later so we will use an elif
                elif self.WSPOW0002A_Button.get_active() == True:
                    self.FEP_command = 'WSPOW0002A'

                # ---- And else would have worked here but other FEP commands
                #      may be added later so we will use an elif
                elif self.WSVIDALLDN_Button.get_active() == True:
                    self.FEP_command = 'WSVIDALLDN'

                # Now tack the command onto the string
                self.RNLE_command_list.extend([self.FEP_command])


                # ---------------- SOURCE ----------------------------------------
                self.RNLE_command_list.extend(['--source', 'NLET'])


                # --------------- DATE ------------------------------------------
                if self.start_date == "":
                    print 'NO START DATE SPECIFIED!!!'
                else:
                    # Concatenate the time of the event
#                    NLET_cmd += ' --event_time '+self.start_date+' '

                    self.RNLE_command_list.extend(['--event_time', self.start_date])

 
                # --------------- CAP NUMBER -----------------------------------
                # Next append the CAP number. NOTE that it is a string at 
                # point and concatenate it to the command
                self.RNLE_command_list.extend(['--cap_num', self.cap_number])

     
                 # -------------- COMMENT -----------------------------------------
                # Now get wheatever the user put in the comment field if anything
                if user_comment == '':
                    print 'USER SUPPLIED NO COMMENT'
                    user_comment = 'No Comment'
    
                # Now append the description switch and description text to the command list             
                self.RNLE_command_list.extend(['--desc', user_comment])

            # Execute the command
            try:
                print('\nRecording the event:')
                x = subprocess.Popen(self.RNLE_command_list)
                # Now reset the command list to the base command
                self.RNLE_command_list = [ '/proj/sot/ska3/flight/bin/python', '/home/gregg/GIT_NLET_GUI/nlet_gui/RecordNonLoadEvent.py']
            except:
                print('\n PROBLEM: Writing to the Non Load Event Tracking File failed.')

            print('\nFinished the NLET file update')

        # ENDIF  (string != "CANCEL"):

        # Done with the window so destroy it
        self.FEPs_ON_OFF_Window.destroy()
        return False


    def Pop_Up_Window(self):
        # 1111 -  Create the Basic window
        self.FEPs_ON_OFF_Window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # set the title and size of the window.
        self.FEPs_ON_OFF_Window.set_title("Power Command ")
        self.FEPs_ON_OFF_Window.set_size_request(700,700)
        self.FEPs_ON_OFF_Window.set_border_width(10)

        # 2222 VBOX Create Vertical box to hold the toolbar and the plot
        # The first row will hold the toolbar
        # The second row item will contain the plotting area
        self.MAN_VBox = gtk.VBox(False, 20)

        # 3333 - Create a TEXT ENTRY TABLE for textual entries and buttons
        self.TextEntry_Table = gtk.Table(15,15, True)

        start_row = 0
        start_col = 0

        # ------------------------------- DATE ------------------------
        # 4444 - LABEL - DATE
        row_len = 1
        col_len = 6
        self.DATE_label = gtk.Label("FEPs Change Date (2018:071:17:32:00):")
        self.TextEntry_Table.attach(self.DATE_label, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        start_col += col_len

        col_len = 5
        # 4444a -  TEXT ENTRY - DATE
        self.DATE_entry = gtk.Entry(max=0)
        self.DATE_entry.set_text("")
        self.TextEntry_Table.attach(self.DATE_entry,
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)



        # -------------------------- CAP Number  --------------------------------------
        # 5555b - LABEL - CAP number
        start_row += row_len
        start_col = 4
        row_len = 1
        col_len = 2
        self.CAP_Number_label = gtk.Label("CAP Number: ")
        self.TextEntry_Table.attach(self.CAP_Number_label, 
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

        # ---------------------------------------  WSPOW00000
        start_row += row_len
        # Shift this over the text box
        start_col = 0

        # 5555 - LABEL - WSPOW00000
        row_len = 1
        col_len = 3
        
        self.WSPOW00000_Button = gtk.RadioButton(None, "WSPOW00000")
        self.WSPOW00000_Button.set_active(False)
        self.TextEntry_Table.attach(self.WSPOW00000_Button,
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        # ---------------------------------------  WSPOW0002A
        start_row += row_len
        # Shift this over the text box
        start_col = 0

        # 6666 - WSPOW0002A
        row_len = 1
        col_len = 3
        
        self.WSPOW0002A_Button = gtk.RadioButton(self.WSPOW00000_Button, "WSPOW0002A")
        self.WSPOW0002A_Button.set_active(True)
        self.TextEntry_Table.attach(self.WSPOW0002A_Button,
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        # --------------------------------------- WSVIDALLDN
        start_row += row_len
        # Shift this over the text box
        start_col = 0

        # 7777 - WSVIDALLDN
        row_len = 1
        col_len = 3
        
        self.WSVIDALLDN_Button = gtk.RadioButton(self.WSPOW00000_Button, "WSVIDALLDN")
        self.WSVIDALLDN_Button.set_active(True)
        self.TextEntry_Table.attach(self.WSVIDALLDN_Button,
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        # -------------------- USER COMMENT -------------------------
        # 4444d - LABEL - User Comment Label
        start_row += row_len
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

        #-----------------------------------------------------------------------
        #              Buttons along the bottom
        #-----------------------------------------------------------------------
        # -------------------- SCORE BUTTON -------------------------
        start_row = 14
        start_col = 0
        # 4444c - BUTTON  For Real SCORE button
        self.SCOREbutton = gtk.Button("SCORE")
        self.SCOREbutton.connect("clicked", self.FEPs_ON_OFF_callback, "SCORE")
        self.TextEntry_Table.attach(self.SCOREbutton,
                                    start_col, start_col + 2,
                                    start_row, start_row + 1)

        # -------------------- CANCEL BUTTON -------------------------
        start_row = 14
        start_col = 11
        # 4444c - BUTTON  CANCEL button
        self.CANCELbutton = gtk.Button("CANCEL")
        self.CANCELbutton.connect("clicked", self.FEPs_ON_OFF_callback, "CANCEL")
        self.TextEntry_Table.attach(self.CANCELbutton,
                                    start_col, start_col + 2,
                                    start_row, start_row + 1)

        # -------------------- TEST BUTTON -------------------------
        start_row = 14
        start_col = 13
        # 4444c - BUTTON  TEST button
        self.TESTbutton = gtk.Button("TEST")
        self.TESTbutton.connect("clicked", self.FEPs_ON_OFF_callback, "TEST")
        self.TextEntry_Table.attach(self.TESTbutton,
                                    start_col, start_col + 1,
                                    start_row, start_row + 1)

        # 2222 - Add the table to the VBOX
        self.MAN_VBox.pack_start(self.TextEntry_Table)

        # Add the VBox to the window box
        self.FEPs_ON_OFF_Window.add(self.MAN_VBox)


        # 1111 - Done creating the BuildEVENTTRACKER Window. Show it.
        self.FEPs_ON_OFF_Window.show_all()
