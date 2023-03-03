import sys
import time
import lmdb
import json

# from helper.logger import Logger
# from helper.util import print_elasped_time


class TimestampQueue:
    TSDB_NAME = "tsdb"
    DLQDB_NAME = "dlqdb"
    DB_MAP_SIZE = 250 * 1024 * 1024  # default map isze : 250M

    def __init__(self, path):
        self.initialized: bool = False
        try:
            self._imdb_env = lmdb.open(
                path, create=True, map_size=TimestampQueue.DB_MAP_SIZE, max_dbs=2
            )
            self.tsdb = self._imdb_env.open_db(
                TimestampQueue.TSDB_NAME.encode(), dupsort=True
            )
            self.dlqdb = self._imdb_env.open_db(
                TimestampQueue.DLQDB_NAME.encode(), dupsort=True
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
    def convert_to_bin(indata):
        return (
            indata.encode()
            if type(indata) == str
            else json.dumps(indata).encode()
            if type(indata) == dict
            else str(indata).encode()
        )

    @staticmethod
    def convert_to_dict(indata):
        return json.loads(indata.decode("utf-8"))

    def put(self, tstamp, tdata):
        self.check_database_initialized()
        # convert input key & value data to bytearray
        tstamp = TimestampQueue.convert_to_bin(tstamp)
        tdata = TimestampQueue.convert_to_bin(tdata)
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
        key_list = list()
        with self._imdb_env.begin(db=self.tsdb) as txn:
            key_list = [key for key, _ in txn.cursor()]
        return key_list

    def get_key_value_list(self):
        self.check_database_initialized()
        key_value_list = list()
        with self._imdb_env.begin(db=self.tsdb) as txn:
            key_value_list = [(key, value) for key, value in txn.cursor()]
        return key_value_list

    def trigger_events(self) -> list:
        try:
            self.check_database_initialized()
            event_data_list = list()
            with self._imdb_env.begin(db=self.tsdb, write=True) as txn:
                curr_tstamp = time.time_ns()
                cursor = txn.cursor()
                for key, value in cursor.iternext():
                    if int(key) <= curr_tstamp:
                        event_data = cursor.pop(key)
                        event_data_list.append(TimestampQueue.convert_to_dict(event_data))
                        break
        except Exception as ex:
            print("trigger event error: ", ex)
            event_data_list = []

        return event_data_list
