from unittest import TestCase, main

from uuid import uuid4

from schedule_queue.pg_schedule_queue import PGScheduleQueue


class PGScheduleQueueTest(TestCase):
    def test_localqueue_simple(self):
        db_config = {
            "user": "postgres",
            "password": "abcd1234",
            "host": "127.0.0.1",
            "port": 55432,
            "database": "scheduler",
        }

        pg_schedule_queue = PGScheduleQueue(db_config)

        test_payload = dict()
        test_payload["test"] = "test"

        pg_schedule_queue.put(str(uuid4()), "test1", 1234567890, test_payload)
        test_payload["test"] = "test44444"
        pg_schedule_queue.put(str(uuid4()), "test1", 1234567880, test_payload)

        pg_schedule_queue.put(str(uuid4()), "test2", 1234565000, test_payload)

        print(pg_schedule_queue.pop())

        # self.assertEqual(len(tdb.get_key_value_list()), 0)
        # self.assertEqual(len(tdb.get_key_value_list(True)), 0)

        pg_schedule_queue.close()


if __name__ == "__main__":
    main()
