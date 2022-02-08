#! /usr/bin/env python
#*******************************************************************************
#
# relayr Gateway Agent Installation Script
#
# Copyright (c) 2021 Relayr, Inc.
# All Rights Reserved
#
# ******************************************************************************

import getpass
import subprocess
import json
import sys
import os.path
import platform
import curses
import time
import threading
import signal
import io

try: input = raw_input
except NameError: pass

sys.tracebacklimit = 0

VERSION="2.1.0"
APT_URL="gwa.relayr.io"
CLOUD_DOMAIN="prd.az.relayr.io"

SECTION_NAME = "MAIN"

spinning = True


def prompt_sudo():
    ret = 0
    if os.geteuid() != 0:
        msg = "[sudo] password for %u:"
        try:
            ret = subprocess.check_call("sudo -v -p '%s'" % msg, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        except subprocess.CalledProcessError as e:
            print(e.output)
            return -1
    return ret


class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\':
                yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy and spinning==True:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        sys.stdout.write('\b')
        sys.stdout.write(' ')
        sys.stdout.flush()
        self.busy = False
        time.sleep(.5)
        sys.stdout.flush()
        time.sleep(.5)


spinner = Spinner()


def signal_handler(signal, frame):
        print('You pressed Ctrl+C - program interrupted!')
        spinner.stop()
        spinning = False
        sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

"""
The MIT License (MIT)
Copyright (c) 2016 Wang Dapeng
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__all__ = ['Picker', 'pick']
KEYS_ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
KEYS_UP = (curses.KEY_UP, ord('k'))
KEYS_DOWN = (curses.KEY_DOWN, ord('j'))
KEYS_SELECT = (curses.KEY_RIGHT, ord(' '))


class Picker(object):
    def __init__(self, options, title=None, indicator='*', default_index=0, multi_select=0, min_selection_count=2, stage=1):

        if len(options) == 0:
            raise ValueError('options should not be an empty list')

        self.options = options
        self.title = title
        self.indicator = indicator
        self.multi_select = multi_select
        self.min_selection_count = min_selection_count
        self.stage = stage
        if (self.stage > 2):
            self.all_selected = [0,1]
        else:
            self.all_selected = [0]

        if default_index >= len(options):
            raise ValueError('default_index should be less than the length of options')

        if multi_select > 0 and min_selection_count > len(options):
            raise ValueError('min_selection_count is bigger than the available options, you will not be able to make any selection')

        self.index = default_index
        self.custom_handlers = {}

    def register_custom_handler(self, key, func):
        self.custom_handlers[key] = func

    def move_up(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.options) - 1
        if self.multi_select == 0:
            for selected in self.all_selected:
                self.all_selected.remove(selected)


    def move_down(self):
        self.index += 1
        if self.index >= len(self.options):
            self.index = 0
        if self.multi_select == 0:
            for selected in self.all_selected:
                self.all_selected.remove(selected)

    def mark_index(self):

        if self.multi_select > 0:
            if self.index in self.all_selected:
                self.all_selected.remove(self.index)
            else:
                self.all_selected.append(self.index)
                if self.options[self.index] == "gwa-core-javase":
                    for selected in self.all_selected:
                        self.all_selected.remove(selected)
                    idx = 0
                    for selected in self.options:
                        self.all_selected.append(idx)
                        idx = idx + 1
        else:
            self.all_selected.append(self.index)

    def get_selected(self):
        if self.multi_select > 0:
            return_tuples = []
            for selected in self.all_selected:
                return_tuples.append((self.options[selected], selected))
            return return_tuples
        else:
            return self.options[self.index], self.index


    def get_title_lines(self):
        if self.title:
            return self.title.split('\n') + ['']
        return []

    def get_footer(self):
        return  ['\n\nTo proceed press enter key.'] + ['']

    def get_option_lines(self):
        lines = []
        for index, option in enumerate(self.options):
            if index == self.index:
                prefix = self.indicator
            else:
                prefix = len(self.indicator) * ' '
            if self.multi_select == 0 and index not in self.all_selected:
                line = '{0} {1}'.format(prefix, option)

            if self.multi_select >= 0 and index in self.all_selected:
                format = curses.color_pair(1)
                line = ('{0} {1}'.format(prefix, option), format)
            else:
                line = '{0} {1}'.format(prefix, option)
            lines.append(line)
        return lines

    def get_lines(self):
        title_lines = self.get_title_lines()
        option_lines = self.get_option_lines()
        footer_lines = self.get_footer()
        lines = title_lines + option_lines + footer_lines
        current_line = self.index + len(title_lines) + 1
        return lines, current_line

    def draw(self):
        self.screen.clear()
        x, y = 1, 1  # start point
        max_y, max_x = self.screen.getmaxyx()
        max_rows = max_y - y-2  # the max rows we can draw
        lines, current_line = self.get_lines()
        scroll_top = getattr(self, 'scroll_top', 0)
        if current_line <= scroll_top:
            scroll_top = 0
        elif current_line - scroll_top > max_rows:
            scroll_top = current_line - max_rows
        self.scroll_top = scroll_top
        lines_to_draw = lines[scroll_top:scroll_top+max_rows]
        for line in lines_to_draw:
            if type(line) is tuple:
                try:
                    if (max_x > 2) and (y <= max_y):
                        self.screen.addnstr(y, x, line[0], max_x-2, line[1])
                except curses.error:
                    pass
            else:
                try:
                    if (max_x > 2) and (y <= max_y):
                        self.screen.addnstr(y, x, line, max_x-2)
                except curses.error:
                    pass
            y += 1
        self.screen.refresh()

    def run_loop(self):
        while True:
            self.draw()
            c = self.screen.getch()
            if c in KEYS_UP:
                self.move_up()
                if self.multi_select == 0:
                    self.mark_index()
            elif c in KEYS_DOWN:
                self.move_down()
                if self.multi_select == 0:
                    self.mark_index()
            elif c in KEYS_ENTER:
                if self.multi_select > 0 and len(self.all_selected) < self.min_selection_count:
                    continue
                return self.get_selected()
            elif c in KEYS_SELECT and self.multi_select > 0:
                self.mark_index()
            elif c in self.custom_handlers:
                ret = self.custom_handlers[c](self)
                if ret:
                    return ret

    def config_curses(self):
        curses.use_default_colors()
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_YELLOW)

    def _start(self, screen):
        self.screen = screen
        self.config_curses()
        return self.run_loop()

    def start(self):
        return curses.wrapper(self._start)


def pick(options, title=None, indicator='*', default_index=0, multi_select=0, min_selection_count=0, stage=1):
    picker = Picker(options, title, indicator, default_index, multi_select, min_selection_count, stage)
    return picker.start()


def query_yes_no(question, default="no"):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = "[y/n] "
    elif default == "yes":
        prompt = "[Y/n] "
    elif default == "no":
        prompt = "[y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def get_user_name():
    in_user_name = input("Enter User Name: ").strip(" ")
    return  in_user_name


def get_user_password():
    in_user_password = getpass.getpass("Enter Password: ").strip(" ")
    return  in_user_password


def get_user_organization():
    in_user_organization = input("Enter Organization Name: ").strip(" ")
    return  in_user_organization


def run_cmd(cmd):
    std_out=""
    if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 7):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        std_out = p.communicate()[0]
    elif sys.version_info[0] == 3 and sys.version_info[1] >= 7:
        p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        std_out = p.stdout
    return std_out


def install_with_return(params):
    try:
        with open(os.devnull, 'w') as FNULL:
            subprocess.check_output(["sudo","apt-get","-y", "install", "-o", 'Dpkg::Options::=--force-confnew', "-o", 'Dpkg::Options::=--force-confmiss', params],stderr=subprocess.STDOUT,shell=False).decode('UTF-8')
            return 0
    except subprocess.CalledProcessError as e:
        spinner.stop()
        print("Installation error:")
        print(str(e.output.decode("utf-8")))
        return -1


def setup_prerequisites():
    print("Preparing prerequisites...")
    run_cmd("sudo apt-get install -y apt-transport-https")


def add_gpg_key(repo_user, repo_pass):
    cmd = "wget -q -O - https://{}:{}@{}/repository/relayr.gpg.key | sudo apt-key add -".format(repo_user, repo_pass, APT_URL)
    ret = run_cmd(cmd)
    if 'OK\n' in ret:
        print("OK")
        return 0
    else:
        print("ERROR")
        return 1


def add_repo_debian_stretch():
    run_cmd("echo \"deb https://{}/repository/debian stretch main contrib non-free\" | sudo tee /etc/apt/sources.list.d/relayr.list".format(APT_URL))
    run_cmd("sudo wget -q -O - http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key | sudo apt-key add -")
    run_cmd("sudo wget http://repo.mosquitto.org/debian/mosquitto-stretch.list -O /etc/apt/sources.list.d/mosquitto-stretch.list")
    run_cmd("sudo apt-get update")
    run_cmd("sudo apt-get install -y mosquitto mosquitto-clients libmosquitto-dev libmosquitto1")
    run_cmd("sudo chown -R mosquitto.mosquitto /var/log/mosquitto")


def add_repo_debian_buster():
    run_cmd("echo \"deb https://{}/repository/debian buster main contrib non-free\" | sudo tee /etc/apt/sources.list.d/relayr.list".format(APT_URL))

def add_repo_raspios():
    run_cmd("echo \"deb https://{}/repository/raspios raspios main contrib non-free\" | sudo tee /etc/apt/sources.list.d/relayr.list".format(APT_URL))

def add_repo_debian_jessie():
    run_cmd("echo \"deb https://{}/repository/debian jessie main contrib non-free\" | sudo tee /etc/apt/sources.list.d/relayr.list".format(APT_URL))
    run_cmd("sudo wget -q -O - http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key | sudo apt-key add -")
    run_cmd("sudo wget http://repo.mosquitto.org/debian/mosquitto-jessie.list -O /etc/apt/sources.list.d/mosquitto-jessie.list")
    run_cmd("echo \"deb http://http.debian.net/debian jessie-backports main\" | sudo tee /etc/apt/sources.list.d/jessie-backports.list")
    run_cmd("sudo apt-get update")
    run_cmd("sudo apt-get install -y -t jessie-backports openjdk-8-jre openjdk-8-jre-headless")
    run_cmd("sudo apt-get install -y mosquitto mosquitto-clients libmosquitto-dev libmosquitto1")
    run_cmd("sudo chown -R mosquitto.mosquitto /var/log/mosquitto")


def add_repo_ubuntu_xenial():
    run_cmd("echo \"deb https://{}/repository/ubuntu xenial main universe multiverse\" | sudo tee /etc/apt/sources.list.d/relayr.list".format(APT_URL))
    run_cmd("sudo apt-get install -y python-software-properties")
    run_cmd("sudo apt-add-repository -y ppa:mosquitto-dev/mosquitto-ppa")
    run_cmd("sudo apt-get update")
    run_cmd("sudo apt-get install -y mosquitto mosquitto-clients libmosquitto-dev libmosquitto1")
    run_cmd("sudo chown -R mosquitto.mosquitto /var/log/mosquitto")


def add_repo_ubuntu_artful():
    run_cmd("echo \"deb https://{}/repository/ubuntu artful main universe multiverse\" | sudo tee /etc/apt/sources.list.d/relayr.list".format(APT_URL))


def add_repo_ubuntu_bionic():
    run_cmd("echo \"deb https://{}/repository/ubuntu bionic main universe multiverse\" | sudo tee /etc/apt/sources.list.d/relayr.list".format(APT_URL))


def add_repo_ubuntu_focal():
    run_cmd("echo \"deb https://{}/repository/ubuntu focal main universe multiverse\" | sudo tee /etc/apt/sources.list.d/relayr.list".format(APT_URL))


def add_repo_auth_credentials(repo_user, repo_pass):
    run_cmd("echo \"machine {} login {} password {}\" | sudo tee  /etc/apt/auth.conf".format(APT_URL, repo_user, repo_pass))
    run_cmd("sudo chmod 600 /etc/apt/auth.conf")


def unsupported_system():
    print("Unsupported platform. Contact relayr Support Team for assistance.")
    quit()

def get_real_binary_name(pkg_name):
    if pkg_name.endswith("c") or pkg_name.endswith("cpp"):
            return  "-".join(pkg_name.split("-")[:-1])
    else:
       return pkg_name


def check_version(binary_name):
    if binary_name == "gwa-core-javase":
        cmd = "/usr/lib/relayr/gwa-core-javase/bin/gwa-core -v 2>&1 | grep 'Gateway Agent Core'"
        response = run_cmd(cmd)
        parts = response.split(",")
        #Gateway Agent Core, 1.8.0, b49, 2020-12-17 07:23:29
        if len(parts) == 4:
            version = parts[1].strip()
            return version
        else:
            return "Unknown"
    if binary_name.startswith("libgwa-utils"):
        return get_lib_version("utils")
    if binary_name.startswith("libgwa-azure"):
        return get_lib_version("azure")
    else:
        cmd = "/usr/bin/" + binary_name + " -v"
        response = run_cmd(cmd)
        return response.strip()

def get_lib_version(name):
    ret = run_cmd("sudo dpkg --list | grep ii | grep relayr | grep gwa | grep libgwa-" + name + " | awk '{print $3}'| awk -F- '{print $1}'").strip()
    return ret

def get_pkg_version_for_name(pkg_name):
    binary_name = get_real_binary_name(pkg_name)
    return check_version(binary_name)

def get_pkg_version_for_id(idx):
    binary_name = get_binary_name(idx)
    return check_version(binary_name)

def get_binary_name(idx):
   pkg_name = get_pkg_name(idx)
   return get_real_binary_name(pkg_name)

def get_pkg_name(idx):
    if idx == 0:
        return "gwa-relayr-cloud-v2-adapter-c"
    if idx == 1:
        return "gwa-azure-cloud-adapter-cpp"
    if idx == 2:
        return "gwa-modbus-adapter-c"
    if idx == 3:
        return "gwa-step7-adapter-c"
    if idx == 4:
        return "gwa-osisoft-adapter-c"
    if idx == 5:
        return "gwa-opc-ua-adapter-c"
    if idx == 6:
        return "gwa-eip-adapter-cpp"
    if idx == 7:
        return "gwa-bacnet-adapter-c"
    if idx == 8:
        return "gwa-canbus-adapter-c"
    if idx == 9:
        return "gwa-pico-agent-coap-adapter-c"
    if idx == 10:
        return "gwa-config-mgr-cpp"
    if idx == 11:
        return "gwa-rule-engine-cpp"
    if idx == 12:
        return "gwa-task-executor-cpp"
    if idx == 13:
        return "gwa-generic-protocol-adapter-cpp"
    if idx == 14:
        return "gwa-storage-service-cpp"
    if idx == 15:
        return "gwa-ethercat-adapter-cpp"
    if idx == 16:
        return "gwa-analytics"


def get_return_code(r):
    if r == 1:
        return "Package is already in newest version and has not been modified"
    if r == 2:
        return "Package installed successfully"
    return "Installation error"


def process_int_response(i, pkgname):
    if i < 0:
        print("*** [Installation error]")
        return 3
    if i == 0:
        print("*** [Package installed successfully]")
        return 2
    if i > 0:
        print("*** [ERROR: package has not ben found in relayr repository.]")
    return 3


def install(idx):
    try:
        print("Installing package: " + get_pkg_name(idx) + "...")
        spinner.start()
        result = install_with_return(get_pkg_name(idx))
        spinner.stop()
        return process_int_response(result, get_pkg_name(idx))
    except IOError:
        spinner.stop()
        return -1


def start_broker():
    return run_cmd("sudo /etc/init.d/mosquitto start")


def run_pkg(idx):
    return run_cmd("sudo systemctl enable --now {}".format(get_pkg_name(idx)))


def setup_sudo():
    result = run_cmd("which sudo | wc -l")
    if result[0] == '0':
        result = run_cmd("id | grep 'uid=0' | wc -l")
        if result[0] == '0':
            print("You don't have sudo configured.\nPlease login as root and install sudo")
            exit()
        else:
            run_cmd("apt-get install -y sudo")


def access_repo(sysid):
    setup_sudo()
    print("Access to the relayr Gateway Agent repository is restricted.\nContact relayr Support Team for access credentials.\n\n")
    repo_user = get_user_name()
    repo_pass = get_user_password()
    run_cmd("sudo apt-get install -y gnupg2")
    if add_gpg_key(repo_user, repo_pass) != 0:
        print("Login credentials do not match! Unable to continue")
        exit(-1)
    setup_prerequisites()
    spinner.start()
    if sysid == 1:
        add_repo_ubuntu_xenial()
    if sysid == 2:
        add_repo_ubuntu_artful()
    if sysid == 3:
        add_repo_debian_stretch()
    if sysid == 4:
        add_repo_debian_jessie()
    if sysid == 5:
        add_repo_debian_buster()
    if sysid == 6:
        add_repo_ubuntu_bionic()
    if sysid == 7:
        add_repo_ubuntu_focal()
    if sysid == 8:
        add_repo_raspios()

    add_repo_auth_credentials(repo_user, repo_pass)
    run_cmd("sudo apt-get update")
    spinner.stop()


def uninstall_prereq():
    spinner.start()
    ret = run_cmd("sudo dpkg --list | grep ii | grep relayr | grep gwa  |awk '{print $2}'").strip()
    pkgs_with_version = ""
    pkgs = ret.split('\n')
    for p in pkgs:
        ver = get_pkg_version_for_name(p)
        pkgs_with_version += '{:<35} {:>7}\n'.format(p, ver)
    spinner.stop()
    return pkgs_with_version.strip()


def uninstall(plist, purge):
    if len(plist) > 4:
        q = query_yes_no("\nAre you sure you want to uninstall these packages:\n" + plist + "\n")
        if q == False:
            print("Uninstall aborted")
            return -1
        print("Running uninstall...")
        spinner.start()
        if purge == 0:
            run_cmd("sudo dpkg --list | grep ii | grep relayr | grep gwa  |awk '{print $2}' | xargs sudo dpkg --force-conflicts --force-breaks -r")
        else:
            run_cmd("sudo dpkg --list | grep ii | grep relayr | grep gwa  |awk '{print $2}' | xargs sudo dpkg --force-conflicts --force-breaks --purge")
        spinner.stop()
        return 0
    else:
        print("Gateway Agent is not installed in this system!")
        print("Nothing to uninstall.")
        return -1


def uninstall_single_packet(p, purge):
        if purge == 0:
            run_cmd("sudo dpkg --force-conflicts --force-breaks -r "+p)
        else:
            run_cmd("sudo dpkg --force-conflicts --force-breaks --purge " +p)
        return 0


def remove_repo():
        repo = run_cmd("sudo cat /etc/apt/auth.conf | grep relayr.io | wc -l")
        if repo[0] == '1':
            q = query_yes_no("\nDo you want to remove relayr.io package repository from your system?\n", 'no')
            if q == False:
                print("relayr.io apt source repository left intact.")
                return -1
            run_cmd("sudo rm /etc/apt/sources.list.d/relayr.list")
            run_cmd("sudo sed -i '/machine {}/d' /etc/apt/auth.conf".format(APT_URL))
            run_cmd("sudo apt-key remove relayr.gpg.key")
            run_cmd("sudo apt-get update")


def remove_agent(sysid, option):
    print("Uninstalling Gateway Agent..")
    ret = uninstall_prereq()
    if len(ret) > 5:
        if uninstall(ret, 0) == 0:
            print("Removed packages:\n")
            print(ret)
            print("Uninstall finished.")
    remove_repo()


def purge_agent(sysid, option):
    print("Uninstalling Gateway Agent..")
    ret = uninstall_prereq()
    if len(ret) > 5:
        if uninstall(ret, 1) == 0:
            print("Removed packages with their configuration:\n")
            print(ret)
            print("Uninstall finished.")
    remove_repo()


def check_flags():
    if len(sys.argv) >= 2:
        if "-v" in sys.argv:
            print("GWA Installation Script [%s]" % VERSION)
            sys.exit(0)


def get_system_data():
    with open("/etc/os-release") as f:
        d = {}
        for line in f:
            k,v = line.rstrip().split("=")
            d[k] = v.strip('"') 
    return d


def detect_system_id():
    print("Detecting operating system...")
    if platform.system() != "Linux":
        print("This script runs only on Linux. Exiting...")
        quit()

    system = get_system_data()
    if not "ID" in system.keys() or not "VERSION_ID" in system.keys():
        unsupported_system()

    if "debian" in system["ID"].lower():
        if system["VERSION_ID"] == "10":
            print("Debian 10 (buster) detected")
            return 5
        elif system["VERSION_ID"] == "9":
            print("Debian 9 (stretch) detected")
            return 3
        elif system["VERSION_ID"] == "8":
            print ("Debian 8 (jessie) detected")
            print("Warning - unsupported or obsolete operating system")
            time.sleep(5)
            return 4
        else:
            unsupported_system()
    elif "raspbian" in system["ID"].lower():
        if system["VERSION_ID"] == "10":
            print("Raspbian 10 (buster) detected")
            return 8
    elif "ubuntu" in system["ID"].lower():
        if system["VERSION_ID"] == "16.04":
            print("Ubuntu 16.04 (Xenial) detected")
            print("Warning - unsupported or obsolete operating system")
            time.sleep(5)
            return 1
        elif system["VERSION_ID"] == "17.10":
            print("Ubuntu 17.10 (Artful) detected")
            print("Warning - unsupported or obsolete operating system")
            time.sleep(5)
            return 2
        elif system["VERSION_ID"] == "18.04":
            print("Ubuntu 18.04 (Bionic) detected")
            return 6
        elif system["VERSION_ID"] == "18.10":
            print("Ubuntu 18.10 (Cosmic) detected")
            return 6
        elif system["VERSION_ID"] == "20.04":
            print("Ubuntu 20.04 (Focal) detected")
            return 7
        else:
            unsupported_system()
    else:
        unsupported_system()
    return 0


def is_buster_x64(sysid):
    return sysid == 5 and "1" in run_cmd("echo $(file /bin/bash) | grep -oc 'x86-64'")


def is_buster_arm(sysid):
    return sysid == 5 and "1" in run_cmd("echo $(file /bin/bash) | grep -oc 'ARM'")


def is_focal_x64(sysid):
    return sysid == 7 and "1" in run_cmd("echo $(file /bin/bash) | grep -oc 'x86-64'")


def get_cloud_token(username, password, organization):
    token = run_cmd("curl --fail -d 'username={}&password={}&org={}' 'https://login.{}/oauth/token?client_id=api-client'".format(username, password, organization, CLOUD_DOMAIN))
    response = json.loads(token)
    return response['accessToken']


def get_cloud_devices(token):
    auth_header = "'Authorization: Bearer {}'".format(token)
    content_header = "'Content-Type: application/json'"
    search_data = "'{\"deviceName\":\"*\"}'"
    search_params = "/devices/search/basic?limit=10&offset=0"
    result = []

    while True:
        cmd = "curl -H {} -H {} -d {} 'https://cloud.{}{}'".format(auth_header, content_header, search_data, CLOUD_DOMAIN, search_params)
        response = json.loads(run_cmd(cmd))
        for device in response['data']:
            result.append((device['deviceName'], device['deviceId']))
        if 'next' in response:
            search_params = response['next']
        else:
            break
    return result


def get_cloud_device_groups(token):
    auth_header = "'Authorization: Bearer {}'".format(token)
    content_header = "'Content-Type: application/json'"
    search_data = "'{\"groupName\":\"*\"}'"
    search_params = "/device-groups/search/light?limit=10&offset=0"
    result = []

    while True:
        cmd = "curl -H {} -H {} -d {} 'https://cloud.{}{}'".format(auth_header, content_header, search_data, CLOUD_DOMAIN, search_params)
        response = json.loads(run_cmd(cmd))
        for device in response['data']:
            result.append((device['groupName'], device['groupId']))
        if 'next' in response:
            search_params = response['next']
        else:
            break
    return result


def get_cloud_credentials(token, did, group_credentials):
    auth_header = "'Authorization: Bearer {}'".format(token)
    endpoint = "device-groups" if group_credentials else "devices"

    cmd = "curl -H {} 'https://cloud.{}/{}/{}/mqtt-credentials'".format(auth_header, CLOUD_DOMAIN, endpoint, did)
    response = json.loads(run_cmd(cmd))
    return response['username'], response['password']


def configure_cloud_adapter_access_credentials():
    ca_cfg_file = "/etc/relayr/gwa-relayr-cloud-v2-adapter-c/gwa-relayr-cloud-v2-adapter-application-config.json"
    if not os.path.isfile(ca_cfg_file):
        print("Cloud adapter does not appear to be installed. Install valid Gateway Agent packages.")
        exit()

    run_cmd("sudo apt-get install curl")

    print("You need to supply your relayr Cloud login and password:")
    organization = get_user_organization()
    uname = get_user_name()
    pwd = get_user_password()

    token = get_cloud_token(uname, pwd, organization)

    if len(token) < 16:
        print("Unable to login with credentials given. Unable to continue.")
        exit()

    devs = []
    devices = get_cloud_devices(token)
    for deviceId, deviceName in devices:
        devs.append("{} - {}".format(deviceId, deviceName))

    device_groups = get_cloud_device_groups(token)
    for groupId, groupName in device_groups:
        devs.append("{} - {} [Device group]".format(groupId, groupName))

    picker_title = 'Please choose a device or device group: \n\n Press cursor keys to move up/down '
    device_index = pick(devs, picker_title, indicator='*', multi_select=0, default_index=0, stage=2)

    if device_index[1] < len(devices):
        use_group_credentials = False
        did = str(devices[device_index[1]][1])
    else:
        use_group_credentials = True
        did = str(device_groups[device_index[1] - len(devices)][1])

    q = query_yes_no(
        "\nDo you want to update relayr Cloud adapter configuration file with login credentials?:\n")

    if not q:
        print("Cloud adapter configuration aborted")
        exit()

    credentials = get_cloud_credentials(token, did, use_group_credentials)

    with open(ca_cfg_file, "r") as config_file:
        config = json.load(config_file)

    config["cloud_connection"] = {}
    config["cloud_connection"]["username"] = credentials[0]
    config["cloud_connection"]["password"] = credentials[1]
    config["cloud_connection"]["credentials_type"] = "group" if use_group_credentials else "device"

    run_cmd("sudo chmod o+w {}".format(ca_cfg_file))
    with io.open(ca_cfg_file, 'w', encoding='utf-8') as config_file:
        config_file.write(json.dumps(config, ensure_ascii=False, indent=4, sort_keys=True))
    run_cmd("sudo chmod o-w {}".format(ca_cfg_file))

    run_cmd("sudo /etc/init.d/gwa-relayr-cloud-v2-adapter-c restart")
    print("relayr Cloud adapter configuration has been updated")


if __name__ == "__main__":
    try:
        check_flags()
        print("************************************************")
        print("*   relayr Gateway Agent Installer [%s]" % VERSION)
        print("*")
        print("*   Copyright (c) 2021 Relayr, Inc.")
        print("*   All Rights Reserved")
        print("************************************************\n\n")
        title = 'Please choose Gateway Agent components to be installed: \n\n  Press space to select/deselect\n  Press cursor keys to move up/down '
        starttitle = 'Please choose which action you would like to perform: \n\n  Press cursor keys to move up/down '
        uninstalltitle = 'Please choose packages to be removed: \n\n  Press space to select/deselect\n  Press cursor keys to move up/down '

        sysid = detect_system_id()

        if prompt_sudo() != 0:
            exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo' or after logging in as root user.\nExiting.")

        startoptions = ['Install Gateway Agent', 'Configure relayr Cloud access credentials', 'Remove selected Gateway Agent components', 'Remove Gateway Agent and all its components']
        startindex = pick(startoptions, starttitle, indicator='*', multi_select=0, default_index=0, stage=1)

        if startindex[1] == 3:
            ret = uninstall_prereq()
            if len(ret) < 5:
                print("No Gateway Agent's components have been found, there's nothing to uninstall.")
                exit()
            q = query_yes_no("\nDo you want to remove Gateway Agent's configuration files?:\n")
            if not q:
                remove_agent(sysid, startindex[1])
            else:
                purge_agent(sysid, startindex[1])
            exit()
        elif startindex[1] == 2:
            ret = uninstall_prereq()
            if len(ret) > 4:
                uninstoptions = ret.split('\n')

            if len(ret) < 5 or len(uninstoptions) < 2:
                print("No Gateway Agent's components have been found, there's nothing to uninstall.")
                exit()
            uninstoptions = ret.split('\n')
            if len(uninstoptions) > 2 and uninstoptions[1][4] == 'c' and uninstoptions[0][4] < 'c':
                tmp = uninstoptions[0]
                uninstoptions[0] = uninstoptions[1]
                uninstoptions[1] = tmp
            uninstoptions[len(uninstoptions)-1] = uninstoptions[0]
            uninstoptions.pop(0)
            uninstindex = pick(uninstoptions, uninstalltitle, indicator='*', multi_select=1, default_index=0, stage=1)
            plist = ""
            if len(uninstindex) < 1:
                print("No component selected, there's nothing to uninstall.")
                exit()
            for x in range(0, len(uninstindex)):
                if uninstindex[x][0] not in plist:
                    plist = plist +uninstindex[x][0] + "\n"
            q = query_yes_no("\nAre you sure you want to uninstall these packages:\n" + plist + "\n")
            if not q:
                print("Uninstall aborted")
                exit()
            print("Running uninstall...")
            for x in range(0, len(uninstindex)):
                uninstall_single_packet(uninstindex[x][0], 0)
            print("Selected packages have been removed.")
            q = query_yes_no("\nDo you want to remove configuration for uninstalled modules?:\n" + plist + "\n")
            if not q:
                print("Configuration purge aborted")
            else:
                print("Removing configuration files...")
                for x in range(0, len(uninstindex)):
                    uninstall_single_packet(uninstindex[x][0], 1)
            print("done.")
            exit()
        elif startindex[1] == 1:
            configure_cloud_adapter_access_credentials()
            exit()

        access_repo(sysid)

        options = ['relayr Cloud Adapter',
                   'Azure Cloud Adapter',
                   'Modbus Protocol Adapter',
                   'Step7 Protocol Adapter',
                   'OSIsoft Protocol Adapter',
                   'OPC-UA Protocol Adapter',
                   'Ethernet/IP Protocol Adapter',
                   'BACnet Protocol Adapter',
                   'Canbus Protocol Adapter',
                   'Pico Agent CoAP Protocol Adapter',
                   'Configuration Manager',
                   'Rule Engine',
                   'Task Executor',
                   'Generic Protocol Adapter',
                   'Storage Service',
                   'EtherCAT Protocol Adapter' ]

        # GWA Analytics is not supported on 18.04, please verify platform before you add new item here.
        if is_buster_x64(sysid) or is_buster_arm(sysid) or is_focal_x64(sysid):
            options.append('GWA Analytics')

        index = pick(options, title, indicator='*', multi_select=1, default_index=0, stage=1)

        print("\n------------------------------------------------\n")

        arr = [0] * len(options)
        for x in range(0, len(index)):
            arr[index[x][1]] = install(index[x][1])

        print("\n------------------------------------------------\n")
        print("Operations summary:")
        for x in range(0, len(arr)):
            if arr[x] > 0:
                print('{: <35} {:>7} - {:>17}'.format(get_pkg_name(x), get_pkg_version_for_id(x), get_return_code(arr[x])))
        print("\n")
        if sysid == 4:
            print("Please make sure java 8 is the default version of java runtime in your system.")
        start_broker()
        for x in range(0, len(index)):
            arr[index[x][1]] = run_pkg(index[x][1])

    except KeyboardInterrupt:
        print("\n")
        spinner.stop()
        spinning = False
