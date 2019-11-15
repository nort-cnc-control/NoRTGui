#!/usr/bin/python3

import json
import re

class JsonReceiver(object):

    def __init__(self, sock):
        self.sock = sock
        self.buf = bytes()
        self.relen = re.compile(r"Length: (\d+)")

    def __acquire_msg(self):
        try:
            start = self.buf.find(b";")
            if start < 0:
                return None
            len = int(self.buf[:start])
            self.buf = self.buf[start+1:]
            msgbuf = self.buf[len]
            self.buf = self.buf[1:]

            #print("msgbuf = ", msgbuf)
            msg = json.loads(msgbuf)
            self.buf = self.buf[end + 1:]
            return msg
        except:
            return None

    def receive_message(self, wait=True):
        msg = self.__acquire_msg()
        if msg != None:
            return msg, False
        while True:
            try:
                ser = self.sock.recv(1024)
            except BlockingIOError:
                return None, False
            except OSError as e:
                print("OS error", type(e), e)
                return None, True
            self.buf += ser
            msg = self.__acquire_msg()
            if msg != None or wait == False:
                return msg, False
        return None, True

class JsonSender(object):

    def __init__(self, sock):
        self.sock = sock

    def send_message(self, message):
        ser = json.dumps(message)
        slen = len(ser)
        msg = bytes(str(slen), "utf-8")
        msg += b";"
        msg += bytes(ser, "utf-8")
        msg += b";"
        print("Sending: ", msg)
        self.sock.send(msg)
