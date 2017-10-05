import base64
from CQPack import CQUnpack


class CQStrangerInfo(object):
    QQID = None
    Nickname = None
    Sex = None
    Age = None

    def __init__(self, data, is_base64=True):
        data = base64.decodebytes(data.encode()) if is_base64 else data
        info = CQUnpack(data)
        self.QQID = info.get_long()
        self.Nickname = info.get_length_str().decode('gb18030')
        self.Sex = info.get_int()
        self.Age = info.get_int()

    def __str__(self):
        t = {
            'QQºÅ': self.QQID,
            'êÇ³Æ': self.Nickname,
            'ÐÔ±ð': self.Sex,
            'ÄêÁä': self.Age,
        }
        lines = []
        for (k, v) in t.items():
            lines.append('{0}:{1}'.format(k, v))
        return '\n'.join(lines)

'''
EXAMPLE:

from CQStrangerInfo import CQStrangerInfo
info = CQStrangerInfo(CQSDK.GetStrangerInfo(fromQQ))
'''