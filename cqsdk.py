#!/usr/bin/env python3

import re
import socket
import socketserver
import sys
import threading
import time
import traceback
from base64 import b64encode, b64decode
from collections import namedtuple


ClientHello = namedtuple("ClientHello", ("port"))
ServerHello = namedtuple("ServerHello", ("client_timeout", "prefix_size", "playload_size", "frame_size"))

RcvdPrivateMessage = namedtuple("RcvdPrivateMessage", ("qq", "text"))
SendPrivateMessage = namedtuple("SendPrivateMessage", ("qq", "text"))

RcvdGroupMessage = namedtuple("RcvdGroupMessage", ("num", "group", "qq", "text"))
SendGroupMessage = namedtuple("SendGroupMessage", ("group", "text"))

RcvdDiscussMessage = namedtuple("RcvdDiscussMessage",
                                ("discuss", "qq", "text"))
SendDiscussMessage = namedtuple("SendDiscussMessage",
                                ("discuss", "text"))

GroupMemberDecrease = namedtuple("GroupMemberDecrease",
                                 ("group", "qq", "operatedQQ"))
GroupMemberIncrease = namedtuple("GroupMemberIncrease",
                                 ("group", "qq", "operatedQQ"))
GroupBan = namedtuple("GroupBan", ("group", "qq", "duration"))

Fatal = namedtuple("Fatal", ("text"))

FrameType = namedtuple("FrameType", ("prefix", "rcvd", "send"))
FRAME_TYPES = (
    FrameType("ClientHello", (), ClientHello),
    FrameType("ServerHello", ServerHello, ()),
    FrameType("PrivateMessage", RcvdPrivateMessage, SendPrivateMessage),
    FrameType("DiscussMessage", RcvdDiscussMessage, SendDiscussMessage),
    FrameType("GroupMessage", RcvdGroupMessage, SendGroupMessage),
    FrameType("GroupMemberDecrease", GroupMemberDecrease, ()),
    FrameType("GroupMemberIncrease", GroupMemberIncrease, ()),
    FrameType("GroupBan", (), GroupBan),
    FrameType("Fatal", (), Fatal),
)

RE_CQ_SPECIAL = re.compile(r'\[CQ:\w+(,.+?)?\]')


class CQAt:
    PATTERN = re.compile(r'\[CQ:at,qq=(\d+?)\]')

    def __init__(self, qq):
        self.qq = qq

    def __str__(self):
        return "[CQ:at,qq={}]".format(self.qq)


class CQImage:
    PATTERN = re.compile(r'\[CQ:image,file=(.+?)\]')

    def __init__(self, file):
        self.file = file

    def __str__(self):
        return "[CQ:image,file={}]".format(self.file)


def load_frame(data):
    if isinstance(data, str):
        parts = data.split()
    elif isinstance(data, list):
        parts = data
    else:
        raise TypeError()

    frame = None
    (prefix, *payload) = parts
    for type_ in FRAME_TYPES:
        if prefix == type_.prefix:
            frame = type_.rcvd(*payload)
    
    # decode text
    if isinstance(frame, (
            RcvdPrivateMessage, RcvdGroupMessage, RcvdDiscussMessage)):
        payload[-1] = b64decode(payload[-1]).decode('gbk')
        frame = type(frame)(*payload)
    return frame


def dump_frame(frame):
    if not isinstance(frame, (tuple, list)):
        raise TypeError()

    # Cast all payload fields to string
    payload = list(map(lambda x: str(x), frame))

    # encode text
    if isinstance(frame, (
            SendPrivateMessage, SendGroupMessage, SendDiscussMessage, Fatal)):
        payload[-1] = b64encode(payload[-1].encode('gbk', 'ignore')).decode()

    data = None
    for type_ in FRAME_TYPES:
        if isinstance(frame, type_.send):
            data = " ".join((type_.prefix, *payload))
    return data


class FrameListener():
    def __init__(self, handler, frame_type):
        self.handler = handler
        self.frame_type = frame_type


class APIRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].decode()
        parts = data.split()

        try:
            message = load_frame(parts)
        except:
            message = None
        if message is None:
            print("Unknown message", parts, file=sys.stderr)
            return

        for listener in self.server.listeners:
            try:
                if (isinstance(message, listener.frame_type) and
                        listener.handler(message)):
                    break
            except:
                traceback.print_exc()


class APIServer(socketserver.UDPServer):
    listeners = []


class CQBot():
    def __init__(self, server_port, client_port=0, online=True, debug=False):
        self.listeners = []

        self.remote_addr = ("127.0.0.1", server_port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.local_addr = ("127.0.0.1", client_port)
        self.server = APIServer(self.local_addr, APIRequestHandler)

        # Online mode
        #   True: Retrive message from socket API server
        #   False: Send message only
        self.online = online

        # Debug Mode
        #   True: print message instead of sending.
        self.debug = debug

    def __del__(self):
        self.client.close()
        self.server.shutdown()
        self.server.server_close()

    def start(self):
        if not self.online:
            return

        self.server.listeners = self.listeners
        threaded_server = threading.Thread(
            target=self.server.serve_forever,
            daemon=True)
        threaded_server.start()

        threaded_keepalive = threading.Thread(
            target=self.server_keepalive,
            daemon=True)
        threaded_keepalive.start()

    def server_keepalive(self):
        while True:
            host, port = self.server.server_address
            self.send(ClientHello(port))
            time.sleep(30)

    def listener(self, frame_type):
        def decorator(handler):
            self.listeners.append(FrameListener(handler, frame_type))
        return decorator

    def send(self, message):
        if self.debug:
            print(message)
            return
        data = dump_frame(message).encode()
        self.client.sendto(data, self.remote_addr)


if __name__ == '__main__':
    try:
        qqbot = CQBot(11235)

        @qqbot.listener((RcvdPrivateMessage, ))
        def log(message):
            print(message)

        qqbot.start()
        print("QQBot is running...")
        input()
    except KeyboardInterrupt:
        pass
