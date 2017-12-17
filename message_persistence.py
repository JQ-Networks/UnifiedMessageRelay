from shelve import DbfilenameShelf
import datetime
import time
from bot_constant import FORWARD_LIST

class AutoSyncShelf(DbfilenameShelf):
    # default to newer pickle protocol and writeback=True
    def __init__(self, filename, protocol=2, writeback=True):
        DbfilenameShelf.__init__(self, filename, protocol=protocol, writeback=writeback)

    def __setitem__(self, key, value):
        DbfilenameShelf.__setitem__(self, key, value)
        self.sync()

    def __delitem__(self, key):
        DbfilenameShelf.__delitem__(self, key)
        self.sync()


class MessageDB:
    def __init__(self, db_name: str):
        self.db = AutoSyncShelf(db_name, writeback=True)
        for idx, forward in enumerate(FORWARD_LIST):
            if str(idx) not in self.db:
                self.db[str(idx)] = dict()

    def append_message(self, qq_message_id: int,
                       tg_message_id: int,
                       forward_index: int,
                       qq_number: int):
        """
        append qq message list to database
        :param qq_message_id: QQ message id
        :param tg_message_id: Telegram message id
        :param forward_index: forward index
        :param qq_number: If from QQ, then QQ sender's number. If from Telegram, then 0 (used for recall)
        :return:
        """
        self.db[str(forward_index)][str(tg_message_id)] = [int(time.mktime(datetime.datetime.now().timetuple())),
                                                           qq_message_id,
                                                           qq_number]
        self.db.sync()

    def retrieve_message(self, tg_message_id: int,
                         forward_index: int):
        if str(tg_message_id) in self.db[str(forward_index)]:
            return self.db[str(forward_index)][str(tg_message_id)][1:]
        else:
            return None

    def purge_message(self):
        for outer_key, forward in self.db.items():
            for key, value in forward.items():
                timestamp = datetime.datetime.utcfromtimestamp(value[0])
                if datetime.datetime.now() - timestamp > datetime.timedelta(weeks=2):
                    del self.db[outer_key][key]
        self.db.sync()

    def __del__(self):
        self.db.close()
