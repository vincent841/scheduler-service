import time
from unittest import TestCase, main

from localqueue.local_queue import LocalQueue


class TimestampDBTest(TestCase):
    DB_NAME = "../db/unittest_lmdb"

    def test_timestamp_1(self):
        tdb = LocalQueue(TimestampDBTest.DB_NAME)

        tstamp = time.time_ns() + 5000000000
        event_data = {"name": "test1", "tstamp": tstamp, "type": "absolute", "data": 1}
        tdb.put(tstamp, event_data)

        tstamp = time.time_ns() + 10000000000
        event_data = {"name": "test2", "tstamp": tstamp, "type": "absolute", "data": 1}
        tdb.put(tstamp, event_data)
        print(tdb.get_key_list())

    def test_timestamp_2(self):
        tdb = LocalQueue(TimestampDBTest.DB_NAME)
        key_list = tdb.get_key_list()

        for key in key_list:
            print(tdb.pop(key))

        print(f"final: {tdb.get_key_list()}")

    def test_timestamp_3(self):
        tdb = LocalQueue(TimestampDBTest.DB_NAME)

        tstamp = time.time_ns() + 5000000000
        event_data = {"name": "test1", "tstamp": tstamp, "type": "absolute", "data": 1}
        tdb.put(tstamp, event_data)

        time.sleep(2)

        while True:
            found_event = tdb.trigger_events()
            if found_event:
                print(f"Found event: {found_event}")
                break
            time.sleep(1)


if __name__ == "__main__":
    main()
