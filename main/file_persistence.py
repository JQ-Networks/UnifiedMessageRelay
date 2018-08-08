import sqlite3
import datetime
import time
import logging
import os
from bot_constant import CQ_ROOT

CQ_IMAGE_ROOT = os.path.join(CQ_ROOT, r'data/image')

logger = logging.getLogger("CTB." + __name__)


class FileDB:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.table_name = 'file_ids'

        self.cursor.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.table_name}';")
        result = self.cursor.fetchall()
        if result[0][0]:
            pass
        else:
            """
            FileDB contains:
             filename: str
             file_type: str
             file_md5: str
             fileid_tg: str
             size: str, bytes
             last_usage_date: int, unix timestamp
             usage_count: int
            """
            self.cursor.execute(f"create table {self.table_name} (download_date int primary key,"
                                f"filename text, file_type text, file_md5 text, fileid_tg text, file_size int,"
                                f" last_usage_date int, usage_count int)")
            # self.cursor.execute(f"create unique index md5_index on {self.table_name}(file_md5);")
            # self.cursor.execute(f"create unique index fileid_index on {self.table_name}(fileid_tg);")
            self.conn.commit()

    def add_qq_resource(self, filename: str, file_type: str, file_md5: str, size: int):
        """

        :param filename:
        :param file_type:
        :param file_md5:
        :param size:
        :return: successfully added
        """
        self.cursor.execute(f"select usage_count, fileid_tg, file_type from '{self.table_name}' where file_md5='{file_md5}'")
        result = self.cursor.fetchall()
        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        if result:
            self.cursor.execute(
                f"update '{self.table_name}' set last_usage_date=?, usage_count=? where file_md5=?;",
                (timestamp, result[0][0]+1, file_md5))
            self.conn.commit()
            return {'file_id': result[0][1], 'file_type': result[0][2]}
        else:

            self.cursor.execute(f"insert into '{self.table_name}' "
                                f"(download_date, filename, file_type, file_md5, fileid_tg, file_size,"
                                f" last_usage_date, usage_count)"
                                f"values (?, ?, ?, ?, ?, ?, ?, ?)",
                                (timestamp, filename, file_type, file_md5, '', size, timestamp, 1))
            self.conn.commit()
            return False

    def get_filename_by_fileid(self, fileid_tg: str):
        self.cursor.execute(f"select usage_count, filename from '{self.table_name}'"
                            f" where fileid_tg='{fileid_tg}'")
        result = self.cursor.fetchall()
        if result:
            timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
            self.cursor.execute(
                f"update '{self.table_name}' set last_usage_date=?, usage_count=? where fileid_tg=?;",
                (timestamp, result[0][0]+1, fileid_tg))
            self.conn.commit()
            return result[0][1]
        return False

    def get_fileid_by_md5(self, file_md5):
        self.cursor.execute(f"select usage_count, fileid_tg, file_type from '{self.table_name}' where file_md5='{file_md5}'")
        result = self.cursor.fetchall()
        if result:
            timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
            self.cursor.execute(
                f"update '{self.table_name}' set last_usage_date=?, usage_count=? where file_md5=?;",
                (timestamp, result[0][0]+1, file_md5))
            self.conn.commit()
            return {'file_id': result[0][1], 'file_type': result[0][2]}
        return False

    def qq_update_fields(self, filename: str, file_type: str, file_md5: str, file_size: int, fileid_tg):
        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        self.cursor.execute(f"insert into '{self.table_name}' "
                            f"(download_date, filename, file_type, file_md5, fileid_tg, file_size,"
                            f" last_usage_date, usage_count)"
                            f"values (?, ?, ?, ?, ?, ?, ?, ?)",
                            (timestamp, filename, file_type, file_md5, fileid_tg, file_size, timestamp, 1))
        self.conn.commit()

    def tg_add_resource(self, fileid_tg: str, filename: str, file_type: str, file_md5: str, file_size: int):
        """

        :param fileid_tg:
        :param filename:
        :param file_type:
        :param file_md5:
        :param file_size:
        :return:
        """
        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        self.cursor.execute(f"insert into '{self.table_name}' "
                            f"(download_date, filename, file_type, file_md5, fileid_tg, file_size,"
                            f" last_usage_date, usage_count)"
                            f"values (?, ?, ?, ?, ?, ?, ?, ?)",
                            (timestamp, filename, file_type, file_md5, fileid_tg, file_size, timestamp, 1))
        self.conn.commit()

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

    def __del__(self):
        self.conn.close()
