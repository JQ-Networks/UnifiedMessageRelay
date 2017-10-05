import base64
from CQPack import CQUnpack


class CQAnonymousInfo(object):
    Identifier = None
    AnonymousName = None
    Token = None

    def __init__(self, data, is_base64=True):
        data = base64.decodebytes(data.encode()) if is_base64 else data
        info = CQUnpack(data)
        self.Identifier = info.get_long()
        self.AnonymousName = info.get_length_str().decode('gb18030')
        self.Token = info.get_length_str().decode('gb18030')

    def __str__(self):
        t = {
            '匿名标识号': self.Identifier,
            '匿名名称': self.AnonymousName,
            'Token': self.Token,
        }
        lines = []
        for (k, v) in t.items():
            lines.append('{0}:{1}'.format(k, v))
        return '\n'.join(lines)