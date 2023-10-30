import pyodbc
from pypika import Query, Table
from typing import Any


class Database():
    """This class enables high level job queue CRUD̶ operations.
    Each row represents a single job, as defined by the sql schema in config.CREATE_TABLE_QUERY.
    Create: Bulk insert data to the job queue with insert_rows().
    Read: Get a new job/row with get_new_job().
    Update: set job status with update_row().
    """

    def __init__(self, table_name: str, connection_string: str):
        self.connection = pyodbc.connect(connection_string)
        self.table = Table(table_name)

    def _commit(self, query:Query) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(query.get_sql())
            cursor.commit()

    def _fetch_all(self, query: Query) -> list:
        with self.connection.cursor() as cursor:
            return cursor.execute(query.get_sql()).fetchall()

    def _fetch_one(self, query: Query) -> list:
        with self.connection.cursor() as cursor:
            return cursor.execute(query.get_sql()).fetchone()

    def insert_rows(self, data: tuple[tuple[str]]) -> None:
        """
        Insert data. Notice the arbitrary limit on MSSQL of 1000 rows. For large inserts, use insert_many_rows() instead.
        Args:
            data: nested tuple arranged as (('aftale', 'fp', 'bilag'),...)

        Returns: None

        """
        query = (Query
                 .into(self.table).columns('aftale', 'fp', 'bilag')
                 .insert(*data))
        self._commit(query)

    def insert_many_rows(self, data: list[tuple[str]]) -> None:
        """
        Insert data. Recommended only for use with ODBC and Microsoft SQL.
        Args:
            data: nested tuple arranged as (('aftale', 'bilag', 'fp'),...)

        Returns:None

        """
        with self.connection.cursor() as cursor:
            cursor.fast_executemany = True
            sql = f"INSERT INTO {self.table.get_table_name()} (aftale, bilag, fp) VALUES (?,?,?)"
            cursor.executemany(sql, data)

    def update_row(self, row_id: int, column_data: dict[str:Any]) -> None:
        """
        Update a job status with a new status text.
        Args:
            row_id: the PK identifyer for the row
            column_data: column name and data to be inserted. E.g. {'Status': 'completed',}

        Returns: None
        """
        query = (Query
                 .update(self.table)
                 .where(self.table.id == row_id))

        for key in column_data:
            query = query.set(key, column_data[key])
        self._commit(query)

    def get_new_row(self) -> pyodbc.Row | None:
        """
        Get a new job, change its status from 'new' to 'in progress'
        Returns: a single Row object with status 'new'. If no 'new' rows are available, the method returns empty list.
        """
        query = (Query
                 .from_(self.table)
                 .where(self.table.status == 'new')
                 .select('*')
                 )

        row = self._fetch_one(query)

        if row:
            self.update_row(row_id=row[0], column_data={'status':'in progress'})
        return row
