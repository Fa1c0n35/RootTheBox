#!/usr/bin/env python
'''
Created on Apr 23, 2012

@author: moloch

 Copyright [2012] [Redacted Labs]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
---------

Linux only (well anything with curses really)
Small program used by teams to monitor their flags
For the sake of portability everything is in one file

'''

###################
# > Imports
###################
import os
import sys
import time
import socket
import random
import threading

try:
    import curses
    import curses.panel
except ImportError:
    print("Error: Failed to import curses, platform not supported")
    os._exit(2)

###################
# > Constants
###################
BUFFER_SIZE = 64
MIN_Y = 24
MIN_X = 80

###################
# > Simple Box
###################
class Box(object):
    ''' Simple box object for storing info '''

    def __init__(self, name, ip_address, port):
        self.name = name
        self.ip_address = ip_address
        self.port = port
        self.state = None
        self.capture_time = None

###################
# > Flag Monitor
###################
class FlagMonitor(object):
    ''' Manages all flags and state changes '''

    def __init__(self):
        self.boxes = []
        self.display_name = None
        self.team_members = []
        self.load_file = None
        self.load_url = None
        self.beep = False

    def start(self):
        ''' Initializes the screen '''
        self.screen = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        self.__colors__()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.max_y, self.max_x = self.screen.getmaxyx()
        self.screen.clear()
        self.screen.border(0)
        self.screen.refresh()
        self.__load__()
        self.__interface__()

    def __load__(self):
        ''' Loads all required data '''
        self.load_message = " Loading, please wait ... "
        self.loading_bar = curses.newwin(3, len(self.load_message) + 2, (self.max_y / 2) - 1, ((self.max_x - len(self.load_message)) / 2))
        self.loading_bar.border(0)
        self.loading_bar.addstr(1, 1, self.load_message, curses.A_BOLD)
        self.loading_bar.refresh()
        time.sleep(0.5)
        self.__boxes__()
        self.__agent__()
        self.loading_bar.clear()

    def __interface__(self):
        ''' Main interface loop '''
        self.__redraw__()
        while True:
            self.screen.nodelay(1)
            self.__title__()
            self.__grid__()
            self.screen.refresh()
            for box in self.boxes:
                self.__box__(box, self.boxes.index(box))
                self.screen.refresh()
            select = self.screen.getch()
            if select == ord("q"):
                break
            elif select == ord("m"):
                self.__menu__()
            else:
                time.sleep(0.01)
        self.stop()
    
    def __title__(self):
        ''' Create title and footer '''
        title = " Root the Box - Flag Monitor "
        version = "[ v0.1 ]"
        agent = "[ "+self.display_name+" ]"
        self.screen.addstr(0, ((self.max_x - len(title)) / 2), title, curses.A_BOLD)
        self.screen.addstr(self.max_y - 1, (self.max_x - len(version)) - 3, version)
        self.screen.addstr(self.max_y - 1, 3, agent)

    def __grid__(self):
        ''' Draws the grid layout '''
        pos_x = 3
        self.screen.hline(3, 1, curses.ACS_HLINE, self.max_x - 2)
        self.ip_title = "   IP  Address   "
        self.screen.vline(2, pos_x + len(self.ip_title), curses.ACS_VLINE, self.max_y - 3)
        self.screen.addstr(2, 2, self.ip_title)
        pos_x += len(self.ip_title)
        self.name_title = "       Box  Name       "
        self.screen.vline(2,  pos_x + len(self.name_title) + 1, curses.ACS_VLINE, self.max_y - 3)
        self.screen.addstr(2, pos_x + 1, self.name_title)
        pos_x += len(self.name_title)
        self.flag_title = "   Flag Status   "
        self.screen.vline(2,  pos_x + len(self.flag_title) + 2, curses.ACS_VLINE, self.max_y - 3)
        self.screen.addstr(2, pos_x + 2, self.flag_title)
        pos_x += len(self.flag_title)
        self.ping_title = "  Ping  "
        self.screen.addstr(2, pos_x + 3, self.ping_title)
        self.__positions__()

    def __positions__(self):
        ''' Sets default x position for each col '''
        self.start_ip_pos = 2
        self.start_name_pos = self.start_ip_pos + len(self.ip_title) + 3
        self.start_flag_pos = self.start_name_pos + len(self.name_title) + 2
        self.start_ping_pos = self.start_flag_pos + len(self.flag_title) + 1

    def __menu__(self):
        ''' Draws the main menu '''
        menu_title = " *** Main Menu *** "
        menu_entries = { "Exit": self.stop }
        self.main_menu = curses.newwin(len(menu_entries) + 3, len(menu_title) + 2, (self.max_y / 2) - 1, ((self.max_x - len(menu_title)) / 2))
        self.main_menu.border(0)
        self.main_menu.addstr(1, 1, menu_title, curses.A_BOLD)
        pos_x = 2
        pos_y = 2
        for entry in menu_entries:
            display_entry = str(menu_entries.index(entry) + 1)+str(". %s" % (entry,))
            self.main_menu.addstr(pos_y, pos_x, display_entry)
            pos_y += 1
        self.main_menu.refresh()
        self.main_menu.nodelay(0)
        select = self.main_menu.getch()
        self.main_menu.clear()

    def __box__(self, box, index):
        ''' Draws a box on the screen '''
        pos_y = 4 + index
        self.screen.addstr(pos_y, self.start_ip_pos, box.ip_address)
        self.screen.addstr(pos_y, self.start_name_pos, box.name[:len(self.name_title)])
        if box.state == None:
            self.screen.addstr(pos_y, self.start_flag_pos, "Not Captured")
    
    def ping_box(self, ip_address, port):
        ''' Pings a box (not ICMP) '''
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip_address, port))
            sock.sendall('ping')
            pong = sock.recv(BUFFER_SIZE)
            sock.close()
            return pong
        except:
            return None

    def load_from_file(self, path):
        ''' Reads a file at path returns the file contents or None '''
        path = os.path.abspath(path)
        if os.path.exists(path) and os.path.isfile(path):
            box_file = open(path, 'r')
            for line in box_file.readlines():
                if len(line) == 0 or line[0] == "#":
                    continue
                plain_text = line.strip()
                name, ip_address, port = line.split(";")
                self.boxes.append(Box(name, ip_address, port))
            box_file.close()
        else:
            sys.stdout.write("[!] Error: File does not exist (%s)\n" % (os.path.abspath(path),))
            sys.stdout.flush()
            os._exit(1)

    def load_from_url(self):
        ''' Load boxes from scoring engine '''
        pass

    def __agent__(self):
        ''' Get display name from user '''
        if self.display_name == None:
            self.stop_thread = False
            thread = threading.Thread(target=self.__matrix__)
            self.loading_bar.clear()
            prompt = "Agent: "
            self.agent_prompt = curses.newwin(3, len(self.load_message) + 2, (self.max_y / 2) - 1, ((self.max_x - len(self.load_message)) / 2))
            self.agent_prompt.border(0)
            self.agent_prompt.addstr(1, 1, prompt, curses.A_BOLD)
            curses.echo()
            thread.start()
            self.display_name = self.agent_prompt.getstr(1, len(prompt) + 1, len(self.load_message) - len(prompt) - 1)
            self.stop_thread = True
            thread.join()
        curses.noecho()

    def __boxes__(self):
        ''' Load boxes from url and/or file '''
        if self.load_file != None:
            self.load_from_file(self.load_file)
        if self.load_url != None:
            self.load_from_url(self.load_url)

    def __colors__(self):
        ''' Setup all color pairs '''
        self.PING = 1
        curses.init_pair(self.PING, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self.IS_CAPTURED = 2
        curses.init_pair(self.IS_CAPTURED, -1, curses.COLOR_GREEN)
        self.TEAM_CAPTURED = 3
        curses.init_pair(self.TEAM_CAPTURED, -1, curses.COLOR_CYAN) 
        self.WAS_CAPTURED = 4
        curses.init_pair(self.WAS_CAPTURED, curses.COLOR_WHITE, curses.COLOR_RED)
        self.NEVER_CAPTURED = 5
        curses.init_pair(self.WAS_CAPTURED, -1, -1)

    def __redraw__(self):
        ''' Redraw the entire window '''
        self.screen.clear()
        self.screen.border(0)
        self.screen.refresh()

    def __clear__(self):
        ''' Clears the screen '''
        self.screen.clear()

    def stop(self):
        ''' Gracefully exits the program '''
        curses.endwin()
        os._exit(0)

    def __matrix__(self):
        ''' Displays really cool, pointless matrix like animation in the background '''
        # (2) Sat com animation
        sat_com = " > Initializing sat com unit, please wait ... "
        progress = ["|", "/","-", "\\"]
        for index in range(0, random.randint(0, 100)):
            self.screen.addstr(2, 2, sat_com + progress[index % 4])
            self.screen.refresh()
            time.sleep(0.1)
            if self.stop_thread:
                return
        self.screen.addstr(2, 2, sat_com + "success")
        self.screen.refresh()
        # (3) Uplink animation
        download = " > Establishing satalite uplink: "
        for index in range(0, 100, 10):
            self.screen.addstr(3, 2, download+str(index)+"%")
            self.screen.refresh()
            time.sleep(0.2)
            if self.stop_thread:
                return
        self.screen.addstr(3, 2, download + "complete")
        self.screen.refresh()
        # (4) Downloading animation
        download = " > Downloading noki telcodes: "
        for index in range(0, 100):
            self.screen.addstr(4, 2, download+str(index)+"%")
            self.screen.refresh()
            time.sleep(0.1)
            if self.stop_thread:
                return
        self.screen.addstr(4, 2, download + "complete")
        self.screen.refresh()
        # (5) Matrix animation
        matrix = " > The matrix has you ... follow the white rabbit "
        for index in range(0, len(matrix)):
            time.sleep(0.2)
            self.screen.addstr(5, 2, matrix[:index])
            self.screen.refresh()
            if self.stop_thread:
                return

###################
# > Main Entry
###################
def help():
    ''' Displays a helpful message '''
    sys.stdout.write("Root the Box - Flag Manager\n")
    sys.stdout.write("Usage:\n")
    sys.stdout.write("\tFileManager.py <options>\n")
    sys.stdout.write("Options:\n")
    sys.stdout.write("\t-f, --file <path>...........................Load boxes from file\n")
    sys.stdout.write("\t-a, --agent <name>..........................Define agent name\n")
    sys.stdout.write("\t-u, --url <url>.............................Scoring engine URL\n")
    sys.stdout.write("\t-b, --beep..................................Beep upon event\n")
    sys.stdout.flush()

def parse_argv(flag_monitor):
    ''' Parses command line arguments '''
    for arg in sys.argv:
        if arg == "-f" or arg == "--file":
            flag_monitor.load_file = get_value(arg)
        elif arg == "-a" or arg == "--agent":
            flag_monitor.display_name = get_value(arg)
        elif arg == "-u" or arg == "--url":
            flag_monitor.load_url = get_value(arg)
        elif  arg == "-b" or arg == "--beep":
            flag_monitor.beep = True

def get_value(token):
    ''' Gets a value based on a command line parameter '''
    try:
        index = sys.argv.index(token)
        if index + 1 < len(sys.argv):
            return sys.argv[index + 1]
        else:
            raise ValueError
    except ValueError:
        sys.stdout.write("[!] Error: No value for parameter (%s)\n" % (token,))
        sys.stdout.flush()
        os._exit(1)

if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        help()
    else:
        flag_monitor = FlagMonitor()
        if 1 < len(sys.argv):
            parse_argv(flag_monitor)
        flag_monitor.start()