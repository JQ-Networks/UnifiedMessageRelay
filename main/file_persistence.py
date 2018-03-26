import sqlite3
import datetime
import time
import logging

logger = logging.getLogger("CTBMain." + __name__)


class FileDB:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        cursor = self.conn.cursor()
        table_name_list = ['jpg_files', 'png_files', 'gif_files']
        for table_name in table_name_list:
            cursor.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            result = cursor.fetchall()
            if result[0][0]:
                pass
            else:
                """
                FileDB contains:
                 filename_qq: str
                 filename_tg: str for gif, tg filename will be mp4 file instead
                 size: int
                 download_date: int
                 last_usage_date: int
                 usage_count: int
                """
                cursor.execute(f"create table {table_name} (download_date int primary key,"
                               f"filename_qq text, filename_tg text, size int, last_usage_date int, usage_count int)")
                self.conn.commit()
        cursor.close()

    def download_or_load_resource(self, url, file_name, file_type):

        pass

    def calculate_size(self):
        """
        calculate db size and real size
        db size is the sum of size in db
        real size is the size of the directory
        :return:
        """
        pass

    def purge_half(self):
        """
        use LRU cache policy
        :return:
        """
        pass

    def purge_one_time(self):
        """
        purge one time usage file
        :return:
        """
        pass

    def sync_cache(self):
        """
        sync cache status with db
        :return:
        """
        pass

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
        cursor = self.conn.cursor()
        table_name = '_' + str(forward_index)
        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        logger.debug(f'append tg_msg_id:{tg_message_id}, qq_msg_id:{qq_message_id}, '
                     f'qq_num:{qq_number}, time:{timestamp} to {table_name}')

        # find if already exists
        cursor.execute(f"select * from '{table_name}' where tg_message_id = ?", (tg_message_id,))
        result = cursor.fetchall()
        cursor.close()
        cursor = self.conn.cursor()
        if len(result):  # if exists, update record
            cursor.execute(f"update '{table_name}' set qq_message_id=?, qq_number=?, timestamp=? where tg_message_id=?;",
                           (qq_message_id, qq_number, timestamp, tg_message_id))
        else:  # if not, create record
            cursor.execute(f"insert into '{table_name}' (tg_message_id, qq_message_id, qq_number, timestamp)"
                           f"values (?, ?, ?, ?)",
                           (tg_message_id, qq_message_id, qq_number, timestamp))
        self.conn.commit()
        cursor.close()

    def retrieve_message(self, tg_message_id: int,
                         forward_index: int):
        """
        get specific record
        :param tg_message_id:
        :param forward_index:
        :return:
        """
        cursor = self.conn.cursor()
        table_name = '_' + str(forward_index)
        cursor.execute(f"select * from '{table_name}' where tg_message_id = ?", (tg_message_id,))
        result = cursor.fetchall()
        cursor.close()
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
        cursor = self.conn.cursor()
        table_name = '_' + str(forward_index)
        cursor.execute(f"delete from {table_name} where tg_message_id=?;", (tg_message_id,))
        self.conn.commit()
        cursor.close()

    def purge_message(self):
        """
        delete outdated records
        :return:
        """
        cursor = self.conn.cursor()
        for idx, forward in enumerate(FORWARD_LIST):
            table_name = '_' + str(idx)
            purge_time = int(time.mktime((datetime.datetime.now() - datetime.timedelta(weeks=2)).timetuple()))
            cursor.execute(f"delete from {table_name} where timestamp < ?;", (purge_time,))
            self.conn.commit()
        cursor.close()

    def __del__(self):
        self.conn.close()
