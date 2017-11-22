import base64
from CQPack import CQUnpack

class CQGroupMemberInfo(object):
    GroupID                 = None
    QQID                    = None
    Nickname                = None
    Card                    = None
    Sex                     = None
    Age                     = None
    Address                 = None
    JoinGroupTime           = None
    LastSpeakTime           = None
    LevelName               = None
    Authority               = None
    IsBad                   = None
    SpecialTitle            = None
    SpecialTitleExpiredTime = None
    IsAllowedToModifyCard   = None

    def __init__(self, data, is_base64=True):
        data = base64.decodebytes(data.encode()) if is_base64 else data
        info = CQUnpack(data)
        self.GroupID                    = info.get_long()
        self.QQID                       = info.get_long()
        self.Nickname                   = info.get_length_str().decode('gb18030')
        self.Card                       = info.get_length_str().decode('gb18030')
        self.Sex                        = info.get_int()
        self.Age                        = info.get_int()
        self.Address                    = info.get_length_str().decode('gb18030')
        self.JoinGroupTime              = info.get_int()
        self.LastSpeakTime              = info.get_int()
        self.LevelName                  = info.get_length_str().decode('gb18030')
        self.Authority                  = info.get_int()
        self.IsGroupAdmin               = self.Authority in [2, 3]
        self.IsGroupOwner               = self.Authority in [3]
        self.IsBad                      = (info.get_int() == 1)
        self.SpecialTitle               = info.get_length_str().decode('gb18030')
        self.SpecialTitleExpiredTime    = info.get_int()
        self.IsAllowedToModifyCard      = (info.get_int() == 1)

    def __str__(self):
        t = {
            '群号' : self.GroupID,
            'QQ号' : self.QQID,
            '昵称' : self.Nickname,
            '名片' : self.Card,
            '性别' : self.Sex,
            '年龄' : self.Age,
            '地区' : self.Address,
            '加群时间' : self.JoinGroupTime,
            '最后发言时间' : self.LastSpeakTime,
            '等级名称' : self.LevelName,
            '管理权限' : self.Authority,
            '是否群管' : self.IsGroupAdmin,
            '是否群主' : self.IsGroupOwner,
            '是否不良成员' : self.IsBad,
            '专属头衔' : self.SpecialTitle,
            '专属头衔过期时间' : self.SpecialTitleExpiredTime,
            '是否允许修改名片' : self.IsAllowedToModifyCard,
        }
        lines = []
        for (k, v) in t.items():
            lines.append('{0}:{1}'.format(k, v))
        return '\n'.join(lines)

'''
EXAMPLE:

from CQGroupMemberInfo import CQGroupMemberInfo
info = CQGroupMemberInfo(CQSDK.GetGroupMemberInfoV2(fromGroup, fromQQ))
'''