import sqlite3
import datetime
import time
from bot_constant import FORWARD_LIST
import logging

logger = logging.getLogger("CTB." + __name__)


class MessageDB:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        for idx, forward in enumerate(FORWARD_LIST):
            table_name = '_' + str(idx)
            self.cursor.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            result = self.cursor.fetchall()
            if result[0][0]:
                pass
            else:
                self.cursor.execute(f"create table {table_name} (tg_message_id int primary key,"
                                    f"qq_message_id int, qq_number int, timestamp int)")
                self.conn.commit()

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
        table_name = '_' + str(forward_index)
        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        logger.debug(f'append tg_msg_id:{tg_message_id}, qq_msg_id:{qq_message_id}, '
                     f'qq_num:{qq_number}, time:{timestamp} to {table_name}')

        # find if already exists
        self.cursor.execute(f"select * from '{table_name}' where tg_message_id = ?", (tg_message_id,))
        result = self.cursor.fetchall()
        if len(result):  # if exists, update record
            self.cursor.execute(
                f"update '{table_name}' set qq_message_id=?, qq_number=?, timestamp=? where tg_message_id=?;",
                (qq_message_id, qq_number, timestamp, tg_message_id))
        else:  # if not, create record
            self.cursor.execute(f"insert into '{table_name}' (tg_message_id, qq_message_id, qq_number, timestamp)"
                                f"values (?, ?, ?, ?)",
                                (tg_message_id, qq_message_id, qq_number, timestamp))
        self.conn.commit()

    def retrieve_message(self, tg_message_id: int,
                         forward_index: int):
        """
        get specific record
        :param tg_message_id:
        :param forward_index:
        :return:
        """
        table_name = '_' + str(forward_index)
        self.cursor.execute(f"select * from '{table_name}' where tg_message_id = ?", (tg_message_id,))
        result = self.cursor.fetchall()
        if len(result):
            return result[0]
        else:
            return None

    def delete_message(self, tg_message_id: int,
                       forward_index: int):
        """
        delete record
        :param tg_message_id:
        :param forward_index:
        :return:
        """
        table_name = '_' + str(forward_index)
        self.cursor.execute(f"delete from {table_name} where tg_message_id=?;", (tg_message_id,))
        self.conn.commit()

    def purge_message(self):
        """
        delete outdated records
        :return:
        """
        for idx, forward in enumerate(FORWARD_LIST):
            table_name = '_' + str(idx)
            purge_time = int(time.mktime((datetime.datetime.now() - datetime.timedelta(weeks=2)).timetuple()))
            self.cursor.execute(f"delete from {table_name} where timestamp < ?;", (purge_time,))
            self.conn.commit()

    def __del__(self):
        self.conn.close()
