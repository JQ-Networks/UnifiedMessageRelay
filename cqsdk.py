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


# Socket API 通讯消息
ClientHello = namedtuple("ClientHello", ("port",))
ServerHello = namedtuple("ServerHello", ("client_timeout", "prefix_size", "playload_size", "frame_size"))

# 聊天部分

## 私聊消息
RcvdPrivateMessage = namedtuple("RcvdPrivateMessage", ("subtype", "qq", "text"))
SendPrivateMessage = namedtuple("SendPrivateMessage", ("qq", "text"))

## 群消息
RcvdGroupMessage = namedtuple("RcvdGroupMessage", ("subtype", "group", "qq", "text"))
SendGroupMessage = namedtuple("SendGroupMessage", ("group", "text"))

## 讨论组消息
RcvdDiscussMessage = namedtuple("RcvdDiscussMessage", ("subtype", "discuss", "qq", "text"))
SendDiscussMessage = namedtuple("SendDiscussMessage", ("discuss", "text"))

# 其它消息-接收

## 管理员变动
## subtype = 1 -> 取消管理员
## subtype = 2 -> 任命管理员
GroupAdminChange = namedtuple("GroupAdminChange", ("subtype", "from_group", "operated_qq"))

## 群成员减少
GroupMemberDecrease = namedtuple("GroupMemberDecrease", ("subtype", "group", "qq", "operated_qq"))

## 群成员增加
GroupMemberIncrease = namedtuple("GroupMemberIncrease", ("subtype", "group", "qq", "operated_qq"))

## 好友已添加(broken)
FriendAdded = namedtuple("FriendAdded", ("subtype", "from_qq"))

## 请求添加好友
RequestAddFriend = namedtuple("RequestAddFriend", ("subtype", "from_qq", "text", "flag"))

## 邀请进群
RequestAddGroup = namedtuple("RequestAddGroup", ("subtype", "from_group", "from_qq", "flag"))

## 群文件上传(broken)
GroupUpload = namedtuple("GroupUpload", ("subtype", "from_group", "from_qq", "file"))

# 其它消息-发送

## 点赞(Coolq Pro)
SendLike = namedtuple("SendLike", ("qq", "times"))

## 屏蔽加群请求
SetGroupKick = namedtuple("SetGroupKick", ("group", "qq", "reject_add_request"))

## 群成员禁言
## duration 单位为秒
SetGroupBan = namedtuple("GroupBan", ("group", "qq", "duration"))

## 任命群管理员(broken)
SetGroupAdmin = namedtuple("SetGroupAdmin", ("group", "qq", "set_admin"))

## 全群组禁言
## enable_ban = 0 -> 取消全群组禁言
## enable_ban = 1 -> 开启全群组禁言
SetGroupWholeBan = namedtuple("SetGroupWholeBan", ("group", "enable_ban"))

## 禁言匿名者(unknown)
SetGroupAnonymousBan = namedtuple("SetGroupAnonymousBan", ("group", "anonymous", "duration"))

## 开关群匿名发言
## enable_anonymous = 0 -> 关闭匿名功能
## enable_anonymous = 1 -> 启用匿名功能
SetGroupAnonymous = namedtuple("SetGroupAnonymous", ("group", "enable_anonymous"))

## 设置群名片
SetGroupCard = namedtuple("SetGroupCard", ("group", "qq", "new_card"))

## 解散群
## 需要身份是群主
SetGroupLeave = namedtuple("SetGroupLeave", ("group", "is_dismiss"))

## 设置特殊头衔
## duration的数值好像不起作用
SetGroupSpecialTitle = namedtuple("SetGroupSpecialTitle", ("group", "qq", "new_special_title", "duration"))

## 离开讨论组
SetDiscussLeave = namedtuple("SetDiscussLeave", ("discuss_id",))

## 发送添加好友请求(Unknown)
FriendAddRequest = namedtuple("FriendAddRequest", ("response_flag", "response_operation", "remark"))

## 发送进群请求(Unknown)
GroupAddRequest = namedtuple("GroupAddRequest", ("response_flag", "request_type", "response_operation", "reason"))

# 信息获取

## 获取群成员信息
GetGroupMemberInfo = namedtuple("GetGroupMemberInfo", ("group", "qq", "nocache"))
RcvGroupMemberInfo = namedtuple("RcvGroupMemberInfo", ("info",))

## 获取群成员列表
GetGroupMemberList = namedtuple("GetGroupMemberList", ("group",))
RcvGroupMemberList = namedtuple("RcvGroupMemberList", ("path",))

## 获取陌生人信息
GetStrangerInfo = namedtuple("GetStrangerInfo", ("qq", "nocache"))
RcvStrangerInfo = namedtuple("RcvStrangerInfo", ("info",))

## 获取Cookies
GetCookies = namedtuple("GetCookies", ())
RcvCookies = namedtuple("RcvCookies", ("cookies",))

## 获取csrf token 
GetCsrfToken = namedtuple("GetCsrfToken", ())
RcvCsrfToken = namedtuple("RcvCsrfToken", ("token",))

## 获取当前登录QQ
GetLoginQQ = namedtuple("GetLoginQQ", ())
RcvLoginQQ = namedtuple("RcvLoginQQ", ("qq",))

## 获取当前用户昵称
GetLoginNickname = namedtuple("GetLoginNickname", ())
RcvLoginNickname = namedtuple("RcvLoginNickname", ("nickname",))

## 获取酷q应用目录
GetAppDirectory = namedtuple("GetAppDirectory", ())
RcvAppDirectory = namedtuple("RcvAppDirectory", ("app_dir",))

Fatal = namedtuple("Fatal", ("text",))

FrameType = namedtuple("FrameType", ("prefix", "rcvd", "send"))
FRAME_TYPES = (
    FrameType("ClientHello", (), ClientHello),
    FrameType("ServerHello", ServerHello, ()),
    FrameType("PrivateMessage", RcvdPrivateMessage, SendPrivateMessage),
    FrameType("DiscussMessage", RcvdDiscussMessage, SendDiscussMessage),
    FrameType("GroupMessage", RcvdGroupMessage, SendGroupMessage),
    FrameType("GroupAdmin", GroupAdminChange, SetGroupAdmin),
    FrameType("GroupMemberDecrease", GroupMemberDecrease, ()),
    FrameType("GroupMemberIncrease", GroupMemberIncrease, ()),
    FrameType("FriendAdded", FriendAdded, ()),
    FrameType("RequestAddFriend", RequestAddFriend, ()),
    FrameType("RequestAddGroup", RequestAddGroup, ()),
    FrameType("GroupUpload", GroupUpload, ()),
    FrameType("Like", (), SendLike),
    FrameType("GroupKick", (), SetGroupKick),
    FrameType("GroupBan", (), SetGroupBan),
    FrameType("GroupWholeBan", (), SetGroupWholeBan),
    FrameType("GroupAnonymousBan", (), SetGroupAnonymousBan),
    FrameType("GroupAnonymous", (), SetGroupAnonymous),
    FrameType("GroupCard", (), SetGroupCard),
    FrameType("GroupLeave", (), SetGroupLeave),
    FrameType("GroupSpecialTitle", (), SetGroupSpecialTitle),
    FrameType("DiscussLeave", (), SetDiscussLeave),
    FrameType("FriendAddRequest", (), FriendAddRequest),
    FrameType("GroupAddRequest", (), GroupAddRequest),
    FrameType("GroupMemberInfo", (), GetGroupMemberInfo),
    FrameType("SrvGroupMemberInfo", RcvGroupMemberInfo, ()),
    FrameType("GroupMemberList", (), GetGroupMemberList),
    FrameType("SrvGroupMemberList", RcvGroupMemberList, ()),
    FrameType("StrangerInfo", (), GetStrangerInfo),
    FrameType("SrvStrangerInfo", RcvStrangerInfo, ()),
    FrameType("Cookies", (), GetCookies),
    FrameType("SrvCookies", RcvCookies, ()),
    FrameType("CsrfToken", (), GetCsrfToken),
    FrameType("SrvCsrfToken", RcvCsrfToken, ()),
    FrameType("LoginQQ", (), GetLoginQQ),
    FrameType("SrvLoginQQ", RcvLoginQQ, ()),
    FrameType("LoginNick", (), GetLoginNickname),
    FrameType("SrvLoginNickname", RcvLoginNickname, ()),
    FrameType("AppDirectory", (), GetAppDirectory),
    FrameType("SrvAppDirectory", RcvAppDirectory, ()),
    FrameType("Fatal", (), Fatal)
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
            break

    # decode text
    if isinstance(frame, (
            RcvdPrivateMessage, RcvdGroupMessage, RcvdDiscussMessage)):
        payload[-1] = b64decode(payload[-1]).decode('gb18030')
        frame = type(frame)(*payload)
    elif isinstance(frame, (RequestAddFriend)):
        payload[-1] = b64decode(payload[-1]).decode('gb18030')
        payload[-2] = b64decode(payload[-2]).decode('gb18030')
        frame = type(frame)(*payload)
    elif isinstance(frame, (RcvGroupMemberList, RcvStrangerInfo, RcvCookies, RcvLoginNickname, RcvAppDirectory)):
        payload[-1] = b64decode(payload[-1]).decode('gb18030')
        frame = type(frame)(*payload)
    return frame


def dump_frame(frame):
    if not isinstance(frame, (tuple, list)):
        raise TypeError()

    # Cast all payload fields to string
    payload = list(map(lambda x: str(x), frame))

    # encode text
    if isinstance(frame, (SendPrivateMessage, SendGroupMessage, SendDiscussMessage, SetGroupCard, Fatal)):
        payload[-1] = b64encode(payload[-1].encode('gb18030', 'ignore')).decode()
    elif isinstance(frame, (SetGroupAnonymousBan, SetGroupSpecialTitle)):
        payload[-2] = b64encode(payload[-2].encode('gb18030', 'ignore')).decode() + '\n'
    elif isinstance(frame, (FriendAddRequest, GroupAddRequest)):
        payload[0] = b64encode(payload[0].encode('gb18030', 'ignore')).decode() + '\n'
        payload[-1] = b64encode(payload[-1].encode('gb18030', 'ignore')).decode() + '\n'

    data = None
    for type_ in FRAME_TYPES:
        if isinstance(frame, type_.send):
            data = " ".join((type_.prefix, *payload))
    return data


class FrameListener():
    def __init__(self, handler, frame_type):
        self.handler = handler
        self.frame_type = frame_type

cqbot = None


class APIRequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        global cqbot
        self.cqbot = cqbot
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)

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

        move_next = True
        for group in self.cqbot.groups:
            for listener in self.server.listeners[group]:
                try:
                    if (isinstance(message, listener.frame_type) and
                            listener.handler(message)):
                        move_next = False
                        break
                except:
                    traceback.print_exc()
            if not move_next:
                break


class APIServer(socketserver.UDPServer):
    listeners = []


class CQBot():
    def __init__(self, server_port, client_port=0, online=True, debug=False):
        self.listeners = {}
        """Dict[:obj:`int`, List[:class:`FrameListener`]]: Holds the handlers per group."""

        self.remote_addr = ("127.0.0.1", server_port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.local_addr = ("127.0.0.1", client_port)
        self.server = APIServer(self.local_addr, APIRequestHandler)
        self.groups = []

        # Online mode
        #   True: Retrive message from socket API server
        #   False: Send message only
        self.online = online

        # Debug Mode
        #   True: print message instead of sending.
        self.debug = debug
        global cqbot
        cqbot = self

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

        # wait for socket thread to init
        time.sleep(1)

    def server_keepalive(self):
        while True:
            host, port = self.server.server_address
            self.send(ClientHello(port))
            time.sleep(30)

    def listener(self, frame_type, group=0):
        if group not in self.listeners:
            self.listeners[group] = list()
            self.groups.append(group)
            self.groups = sorted(self.groups)

        def decorator(handler):
            self.listeners[group].append(FrameListener(handler, frame_type))
        return decorator

    def send(self, message):
        if self.debug:
            print(message)
            return
        data = dump_frame(message).encode()
        self.client.sendto(data, self.remote_addr)


if __name__ == '__main__':
    import utils
    try:
        qqbot = CQBot(11235)

        @qqbot.listener(RcvGroupMemberInfo)
        def log(message):
            info_bytes = b64decode(message.info)
            member_info = utils.parse_member_info(info_bytes)

        qqbot.start()
        print("QQBot is running...")
        qqbot.send(GetGroupMemberInfo('GROUP_NUMBER_HERE', 'QQ_NUMBER_HERE', '1'))
        input()
    except KeyboardInterrupt:
        pass
