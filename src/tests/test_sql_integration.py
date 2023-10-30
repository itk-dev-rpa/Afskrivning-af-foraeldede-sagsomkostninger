import datetime
import unittest
import pyodbc
from src import config

TABLE_NAME = "test_fosa_job_queue"
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
    "DATABASE=TestFosa;"
    "UID=NewUser;"
    "PWD=rf6zgV5H"
)

class DatabaseInteraction(unittest.TestCase):
    """
    Test job queue logic. Requies a running database. E.g. in docker.
    """
    @classmethod
    def setUpClass(self):
        """
        Drop table in case tearDown() was not called.
        """
        try:
            connection = pyodbc.connect(CONNECTION_STRING)
            with connection.cursor() as cursor:
                cursor.execute(f"DROP TABLE {TABLE_NAME}")
                cursor.commit()
        except:
            pass # nothing to drop

    def setUp(self) -> None:
        """
        Create table
        """
        connection = pyodbc.connect(CONNECTION_STRING)
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE TABLE {TABLE_NAME} "+config.CREATE_TABLE_QUERY)
            cursor.commit()

    def tearDown(self) -> None:
        """
        Drop table
        """
        connection = pyodbc.connect(CONNECTION_STRING)
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE {TABLE_NAME}")
            cursor.commit()


    def test_insert(self):
        from pypika import MSSQLQuery, Table
        from src.queue import Database
        """
        Insert data into the database, then validate that data was inserted.
        """
        db = Database(TABLE_NAME, CONNECTION_STRING)
        data = (('foo1', 'bar', 'baz'),
                ('foo2', 'bar', 'baz'),
                ('foo3', 'bar', 'baz'))

        db.insert_rows(data=data)

        # assert insert was successful
        table = Table(TABLE_NAME)
        query = MSSQLQuery.from_(table).select("*")

        rows = db._fetch_all(query)


        self.assertEqual((1,'foo1', 'bar'), rows[0][:3])
        self.assertEqual(3, len(rows))  # only three row should exist

    def test_insert_many(self):
        from pypika import MSSQLQuery, Table
        from src.queue import Database
        """
        Insert more than 1000 rows of data into the database, then validate that data was inserted.
        """
        db = Database(TABLE_NAME, CONNECTION_STRING)

        long_data = []
        for x in range(1001):
            long_data.append(('foo', 'bar', 'baz'))

        db.insert_many_rows(long_data)

        # assert insert was successful
        table = Table(TABLE_NAME)
        query = MSSQLQuery.from_(table).select("*")

        rows = db._fetch_all(query)

        self.assertEqual((1,'foo', 'baz'), rows[0][:3])
        self.assertEqual(1001, len(rows))  # more than 1000 rows should be returned


    def test_update(self):
        from pypika import MSSQLQuery, Table
        from src.queue import Database
        """
        Given a job or row id, the status must be updated. 
        """
        # setup by inserting some data
        db = Database(TABLE_NAME, CONNECTION_STRING)
        data = (('foo1', 'bar', 'baz'))

        db.insert_rows(data=data)
        # perform update
        now = datetime.datetime.now()
        db.update_row(row_id=1,
                      column_data={'status':"completed",
                      'date_completed': datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)})

        # assert insert was successful
        table = Table(TABLE_NAME)
        query = MSSQLQuery.from_(table).select("*")
        rows = db._fetch_all(query)

        self.assertEqual(("completed"), rows[0][4])
        self.assertEqual(datetime.datetime, type(rows[0][6]))

    def test_get_new_job(self):
        from src.queue import Database
        """
        Get a new job from the queue. 
        """
        # setup by inserting some data
        db = Database(TABLE_NAME, CONNECTION_STRING)
        data = (('foo1', 'bar', 'baz'),('foo2', 'bar', 'baz'))
        db.insert_rows(data=data)

        # get a new jobs
        first = db.get_new_task()
        second = db.get_new_task()
        empty = db.get_new_task()

        self.assertEqual("foo1", first.aftale)
        self.assertEqual("foo2", second.aftale)
        self.assertEqual(None, empty)

    def test_exception_to_db_status(self):
        from pypika import MSSQLQuery, Table
        from src.queue import Database
        """
        Show that exception messages are inserted into database status.
        """
        class BusinessError(Exception):
            pass

        # setup by inserting some data
        db = Database(TABLE_NAME, CONNECTION_STRING)
        data = (('foo1', 'bar', 'baz'),('foo2', 'bar', 'baz'))
        db.insert_rows(data=data)

        # update job status
        try:
            raise BusinessError("unittest")
        except Exception as error:
            db.update_row(row_id=1, column_data={'status': f"{type(error).__name__}: {error}"})

        try:
            raise ValueError("unittest")
        except Exception as error:
            db.update_row(row_id=2, column_data={'status': f"{type(error).__name__}: {error}"})

        # get rows
        table = Table(TABLE_NAME)
        query = MSSQLQuery.from_(table).select("*")
        rows = db._fetch_all(query)

        self.assertEqual("BusinessError: unittest", rows[0][4])
        self.assertEqual("ValueError: unittest", rows[1][4])


if __name__ == '__main__':
    unittest.main()
