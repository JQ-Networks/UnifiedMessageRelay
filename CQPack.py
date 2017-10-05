import struct


class CQUnpack(object):
    def __init__(self, data):
        self._data = data
        self._length = len(data)
        self._location = 0

    def _get_(self, fmt, length):
        ret = struct.unpack(fmt, self._data[self._location:self._location + length])[0]
        self._location += length
        return ret

    def get_byte(self):
        return self._get_('B', 1)

    def get_short(self):
        return self._get_('!H', 2)

    def get_int(self):
        return self._get_('!I', 4)

    def get_long(self):
        return self._get_('!Q', 8)

    def get_length_str(self) -> str:
        length = self.get_short()
        ret = self._data[self._location:self._location + length]
        self._location += length
        return '{0}'.format(ret)

    def length(self):
        return self._length - self._location
