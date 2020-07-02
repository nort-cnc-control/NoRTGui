#!/usr/bin/env python3

import sys
import getopt
import abc
import os
import socket
import json

import common
import common.jsonwait

import gi
from gi.repository import GLib

from ui_wx import gui

def usage():
    pass

class Controller(object):

    def __init__(self, sock):
        self.sock = sock
        self.control = gui.Interface()
        
        self.control.newfile += self.__new_file
        self.control.loadfile += self.__load_file 
        self.control.savefile += self.__save_file

        self.control.stop_clicked += self.__stop
        self.control.start_clicked += self.__start
        self.control.continue_clicked += self.__continue
        
        self.control.home_clicked += self.__home
        self.control.probe_clicked += self.__probe
        
        self.control.command_entered += self.__command

        self.sock.settimeout(0)
        self.control.Switch2InitialMode()

    def __send_command(self, command):
        msg = {
            "type" : "command",
            "command" : command,
        }
        self.msg_sender.send_message(msg)

    def __continue(self):
        self.__send_command("continue")

    def __start(self):
        cmds = [line.strip() for line in self.control.GetGCode().splitlines()]
        r = {
            "type" : "command",
            "command" : "load",
            "program" : cmds
        }
        self.msg_sender.send_message(r)
        self.__send_command("start")

    def __reset(self):
        self.__send_command("reset")

    def __stop(self):
        self.__send_command("stop")

    def __command(self, cmd):
        r = {
            "type" : "command",
            "command" : "execute",
            "program" : cmd
        }
        self.msg_sender.send_message(r)

    def __home(self):
        r = {
            "type" : "command",
            "command" : "execute",
            "program" : "G28"
        }
        self.msg_sender.send_message(r)

    def __probe(self):
        r = {
            "type" : "command",
            "command" : "execute",
            "program" : "G30",
        }
        self.msg_sender.send_message(r)

    def __new_file(self):
        self.control.DisplayGCode("")

    def __load_file(self, filename):
        file = open(filename, encoding="utf-8")
        code = file.read()
        file.close()
        self.control.DisplayGCode(code)

    def __save_file(self, filename, text):
        file = open(filename, "w", encoding="utf-8")
        file.write(text)
        file.close()

    def __process_event(self, msg):
        type = msg["type"]
        if type == "line":
            line = msg["line"]
            self.control.SelectActiveLine(line)

        elif type == "coordinates":
            hw = msg["hardware"]
            glob = msg["global"]
            loc = msg["local"]
            cs = msg["cs"]
            self.control.SetCoordinates(hw, glob, loc, cs)

        elif type == "state":
            state = msg["state"]
            message = msg["message"]
            if state == "init":
                self.control.Switch2InitialMode()
            elif state == "running":
                self.control.Switch2RunningMode()
            elif state == "paused":
                self.control.Switch2PausedMode()
                if message != "":
                    self.control.ShowOk(message)
            elif state == "completed":
                self.control.Switch2InitialMode()
                if msg["display"]:
                    if msg["message"] == "":
                        self.control.ShowOk("Finished")
                    else:
                        self.control.ShowOk(msg["message"])

        elif type == "message":
            self.control.ShowOk(msg["message"])

    def __on_receive_event(self, sock, cond):
        
        while True:
            try:
                msg, dis = self.msg_receiver.receive_message(wait=False)
                if dis:
                    print("Disconnect")
                    return False
                if msg is None:
                    return True
            except:
                return True
            print(msg)
            self.__process_event(msg)
        return True

    def run(self):
        self.msg_receiver = common.jsonwait.JsonReceiver(self.sock)
        self.msg_sender = common.jsonwait.JsonSender(self.sock)

        GLib.io_add_watch(self.sock, GLib.IO_IN, self.__on_receive_event)
        self.__reset()
        self.control.run()

if __name__ == "__main__":

    infile = None

    try:
        optlist, _ = getopt.getopt(sys.argv[1:], "i:p:b:h")
    except getopt.GetoptError as err:
        print(err)
        sys.exit(1)
    
    raddr = "127.0.0.1"
    rport = 8888

    for o, a in optlist:
        if o == "-i":
            infile = a
        elif o == "-h":
            usage()
            sys.exit(0)
        elif o == "-r":
            raddr = a
        elif o == "-p":
            rport = int(a)

    remote = ("127.0.0.1", 8888)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(remote)

    ctl = Controller(sock)
    ctl.run()
    sys.exit(0)
