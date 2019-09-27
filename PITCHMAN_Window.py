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

class PITCHMAN:

    # The Constructor
    def __init__(self):
        self.start_date = "1900:000:00:01:00.00"
        self.stop_date = "1900:001:00:01:00.00"
        self.start_time = '0.0'
        self.stop_time = '0.0'
        self.default_current_folder = "/data/acis/LoadReviews/"

        self.pitch = '1000'
        self.roll = '2000'
        self.q1 = '-1000'
        self.q2 = '-2000'
        self.q3 = '-3000'
        self.q4 = '-4000'

        # Initialize the Command to be recorded.
#        self.RNLE_command_list = [ '/proj/sot/ska3/flight/bin/python', '/data/acis/LoadReviews/script/NONLOADEVENTTRACKER/RecordNonLoadEvent.py', 'MAN', '--source', 'NLET']

        self.RNLE_command_list = [ '/proj/sot/ska3/flight/bin/python', '/home/gregg/GIT_NLET_GUI/nlet_gui/RecordNonLoadEvent.py', 'MAN', '--source', 'NLET']

    #-----------------------------------------------------------------------
    #
    # check_q - Check to see if the quaternion specified is a float
    #
    #-----------------------------------------------------------------------
    def check_q(self, q):
        """
        Given a value from any of the 4 Quaternion test entry boxes in the
        PITCHMAN GUI popup, test to see if it's a float. if it is, return
        the string value otherwise return None. The result is concatenated
        to the NLET_cmd string
        """
        try:
            float(q)
            return(q)
        except ValueError:
            return(None)
    
#-----------------------------------------------------------------------
#
# MANcallback - call back function when TEST, CANCEL or SCORE buttons
#               are pressed
#
#-----------------------------------------------------------------------
    def MANcallback(self, widget, string):
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

        When the SCORE, CANCEL or TEST button has been clicked, the MANEUVER
        pop-up is destroyed.
        """
        # First thing we are going to do is gather all the data from the 
        # pop-up window.
        
        # Execution start time of the Maneuver CAP 
        self.start_date = self.DATE_entry.get_text()
        self.q1 = self.Q1_entry.get_text()
        self.q2 = self.Q2_entry.get_text()
        self.q3 = self.Q3_entry.get_text()
        self.q4 = self.Q4_entry.get_text()
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

                # User must have clicked on TEST
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
                    print "NO START DATE SPECIFIED!!!"
                else:
                    # Concatenate the  time of the event
                    self.RNLE_command_list.extend(['--event_time', self.start_date])
    
    
                # ---------------- QUATERNIONs Q1 through Q4 --------------------
                # Next tack on the switches and values for all 4 Quaternions.

                # Check to see if this is a valid Q
                q_use = self.check_q(self.q1)
                # Append whatever value check_q returned
                self.RNLE_command_list.extend(['--q1', str(q_use) ])
    
                # ---------------- QUATERNIONs Q2 --------------------
                # Check to see if this is a valid Q
                q_use = self.check_q(self.q2)
                # Append whatever value check_q returned    
                self.RNLE_command_list.extend(['--q2', str(q_use) ])
    
                # ---------------- QUATERNIONs Q3 --------------------
                # Check to see if this is a valid Q
                q_use = self.check_q(self.q3)
                # Append whatever value check_q returned    
                self.RNLE_command_list.extend(['--q3', str(q_use) ])
    
    
                # ---------------- QUATERNIONs Q4 --------------------
                # Check to see if this is a valid Q    
                q_use = self.check_q(self.q4)
                # Append whatever value check_q returned        
                self.RNLE_command_list.extend(['--q4', str(q_use) ])
     
                 # -------------- COMMENT -----------------------------------------
                # Now get wheatever the user put in the comment field if anything
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
                self.RNLE_command_list = [ '/proj/sot/ska3/flight/bin/python', '/home/gregg/GIT_NLET_GUI/nlet_gui/RecordNonLoadEvent.py', 'MAN', '--source', 'NLET']
            except:
                print('\n PROBLEM: Writing the MANEUVER event to the Non Load Event Tracking File failed.')

            print('\nFinished the NLET file update')
  



        # Done with the window so destroy it
        self.BuildMANWindow.destroy()
        return False


    def Pop_UP_MAN_Window(self):
        # 1111 -  Create the Basic window
        self.BuildMANWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # set the title and size of the window.
        self.BuildMANWindow.set_title("MAN")
        self.BuildMANWindow.set_size_request(700,700)
        self.BuildMANWindow.set_border_width(10)

        # 2222 VBOX Create Vertical box to hold the toolbar and the plot
        # The first row will hold the toolbar
        # The second row item will contain the plotting area
        self.MAN_VBox = gtk.VBox(False, 20)

        # 3333 - Create a TABLE for textual entries and buttons
        self.TextEntry_Table = gtk.Table(15,15, True)

        start_row = 0
        start_col = 0

        # ------------------------------- DATE ------------------------
        # 4444 - LABEL - DATE
        row_len = 1
        col_len = 5
        self.DATE_label = gtk.Label("MAN Date (2018:071:17:32:00): ")
        self.TextEntry_Table.attach(self.DATE_label, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        start_col += col_len

#        row_len = 1
        col_len = 5
        # 4444a -  TEXT ENTRY - DATE
        self.DATE_entry = gtk.Entry(max=0)
        self.DATE_entry.set_text("")
        self.TextEntry_Table.attach(self.DATE_entry,
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)



        # ------------------------------- QUATERNIONS ------------------------
        #
        # ------------------------------------------ Q1
        start_row += row_len
        # Shift this over the text box
        start_col = 0

        # 4444 - LABEL - Q1 QUATERNION
        row_len = 1
        col_len = 3
        self.QUATERNION_label = gtk.Label("Q1: ")
        self.TextEntry_Table.attach(self.QUATERNION_label, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        start_col += col_len

        col_len = 5
        # 4444a -  TEXT ENTRY - QUATERNION
        self.Q1_entry = gtk.Entry(max=0)
        self.Q1_entry.set_text("")
        self.TextEntry_Table.attach(self.Q1_entry,
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        # ---------------------------------------  Q2
        start_row += row_len
        # Shift this over the text box
        start_col = 0

        # 4444 - LABEL - Q2 Q2
        row_len = 1
        col_len = 3
        self.Q2_label = gtk.Label("Q2: ")
        self.TextEntry_Table.attach(self.Q2_label, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        start_col += col_len

        col_len = 5
        # 4444a -  TEXT ENTRY - Q2
        self.Q2_entry = gtk.Entry(max=0)
        self.Q2_entry.set_text("")
        self.TextEntry_Table.attach(self.Q2_entry,
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)


        # ---------------------------------------  Q3
        start_row += row_len
        # Shift this over the text box
        start_col = 0
        # 4444 - LABEL - QUATERNION

        # 4444 - LABEL - Q3 Q3
        row_len = 1
        col_len = 3
        self.Q3_label = gtk.Label("Q3: ")
        self.TextEntry_Table.attach(self.Q3_label, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        start_col += col_len

        col_len = 5
        # 4444a -  TEXT ENTRY - Q3
        self.Q3_entry = gtk.Entry(max=0)
        self.Q3_entry.set_text("")
        self.TextEntry_Table.attach(self.Q3_entry,
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)



        # ---------------------------------------  Q4
        start_row += row_len
        # Shift this over the text box
        start_col = 0

        # 4444 - LABEL - Q4 Q4
        row_len = 1
        col_len = 3
        self.Q4_label = gtk.Label("Q4: ")
        self.TextEntry_Table.attach(self.Q4_label, 
                                    start_col, start_col + col_len,
                                    start_row, start_row + row_len)

        start_col += col_len

        col_len = 5
        # 4444a -  TEXT ENTRY - Q4
        self.Q4_entry = gtk.Entry(max=0)
        self.Q4_entry.set_text("")
        self.TextEntry_Table.attach(self.Q4_entry,
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


        # -------------------- SCORE BUTTON -------------------------
        start_row = 14
        start_col = 0
        # 4444c - BUTTON  For Real SCORE button
        self.SCOREbutton = gtk.Button("SCORE")
        self.SCOREbutton.connect("clicked", self.MANcallback, "SCORE")
        self.TextEntry_Table.attach(self.SCOREbutton,
                                    start_col, start_col + 2,
                                    start_row, start_row + 1)

        # -------------------- CANCEL BUTTON -------------------------
        start_row = 14
        start_col = 11
        # 4444c - BUTTON  CANCEL button
        self.CANCELbutton = gtk.Button("CANCEL")
        self.CANCELbutton.connect("clicked", self.MANcallback, "CANCEL")
        self.TextEntry_Table.attach(self.CANCELbutton,
                                    start_col, start_col + 2,
                                    start_row, start_row + 1)

        # -------------------- TEST BUTTON -------------------------
        start_row = 14
        start_col = 13
        # 4444c - BUTTON  TEST button
        self.TESTbutton = gtk.Button("TEST")
        self.TESTbutton.connect("clicked", self.MANcallback, "TEST")
        self.TextEntry_Table.attach(self.TESTbutton,
                                    start_col, start_col + 1,
                                    start_row, start_row + 1)

        # 2222 - Add the table to the VBOX
        self.MAN_VBox.pack_start(self.TextEntry_Table)

        # Add the VBox to the window box
        self.BuildMANWindow.add(self.MAN_VBox)


        # 1111 - Done creating the BuildEVENTTRACKER Window. Show it.
        self.BuildMANWindow.show_all()
