import sys
import time
import lmdb

from helper.logger import Logger


class TimestampDB:
    DB_NAME = "tsdb"

    def __init__(self, path):
        self.initialized: bool = False
        try:
            self._imdb_env = lmdb.open(
                path, create=True, map_size=250 * 1024 * 1024, max_dbs=2
            )
            self.tsdb = self._imdb_env.open_db(
                TimestampDB.DB_NAME.encode(), dupsort=True
            )
        except Exception as ex:
            print(ex, file=sys.stderr)
            raise ex

        self.initialized = True

    def close(self):
        self._imdb_env.close()

    # TODO: convert the wrapout code
    def check_database_initialized(self):
        if not self.initialized:
            raise Exception("Database is not initialized.")

    @staticmethod
    def convert_type(indata):
        return indata.encode() if type(indata) == str else str(indata).encode()

    def put(self, tstamp, tdata):
        self.check_database_initialized()
        # convert input key & value data to bytearray
        tstamp = TimestampDB.convert_type(tstamp)
        tdata = TimestampDB.convert_type(tdata)
        with self._imdb_env.begin(db=self.tsdb, write=True) as txn:
            txn.put(tstamp, tdata, db=self.tsdb)

    def pop(self, key):
        self.check_database_initialized()
        value = None
        with self._imdb_env.begin(db=self.tsdb, write=True) as txn:
            cursor = txn.cursor()
            value = cursor.pop(key)
        return value

    def get_key_list(self):
        self.check_database_initialized()
        with self._imdb_env.begin(db=self.tsdb) as txn:
            key_list = [key for key, _ in txn.cursor()]
        return key_list

    def trigger_events(self):
        self.check_database_initialized()

        event_data = None
        with self._imdb_env.begin(db=self.tsdb, write=True) as txn:
            curr_tstamp = time.time_ns()
            cursor = txn.cursor()
            for key, value in cursor.iternext():
                if int(key) <= curr_tstamp:
                    event_data = cursor.pop(key)

        return event_data
