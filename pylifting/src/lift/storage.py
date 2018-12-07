import psycopg2 as pg
from datetime import datetime, MAXYEAR, MINYEAR
from psycopg2 import extras as pg_extras

from models import Session


class Storage:
    SCHEMA = """
        CREATE TABLE IF NOT EXISTS sessions (
           exercise varchar,
           effort decimal,
           reps int,
           sets int,
           weight decimal,
           duration interval,
           session_date date
        );
    """

    INSERT = """
        INSERT INTO sessions (
           exercise,
           effort,
           reps,
           sets,
           weight,
           duration,
           session_date
        ) VALUES (
            %(exercise)s,
            %(effort)s,
            %(reps)s,
            %(sets)s,
            %(weight)s,
            %(duration)s,
            %(session_date)s
        )
    """

    SELECT_ALL_BY_DATE = """
        SELECT * FROM SESSIONS WHERE session_date BETWEEN %s and %s ORDER BY session_date;
    """

    EXERCISES = """
        SELECT DISTINCT exercise from sessions;
    """

    def __init__(self, environ):
        dbname = environ['PG_DB_NAME']
        user = environ['PG_USER']
        password = environ['PG_PASSWORD']
        host = environ['PG_HOST']
        port = environ['PG_PORT']

        self.connection = pg.connect(
                dbname=dbname,
                user=user,
                password=password,
                hostaddr=host,
                port=port,
                sslmode='verify-ca',
                sslrootcert=environ['PG_ROOT_CERT_PATH'],
                sslcert=environ['PG_SSL_CERT'],
                sslkey=environ['PG_SSL_CLIENT_KEY']
        )

        self.schema()

    def all_exercises(self):
        cursor = self.connection.cursor()
        cursor.execute(self.EXERCISES)
        return {e[0] for e in cursor}

    def schema(self):
        cursor = self.connection.cursor()
        cursor.execute(self.SCHEMA)
        self.connection.commit()

    def insert(self, session):
        cursor = self.connection.cursor()
        print(session.to_sql())
        cursor.execute(self.INSERT, session.to_sql())
        self.connection.commit()

    def iterate(self, start_date=datetime(year=MINYEAR, month=1, day=1), end_date=datetime(year=MAXYEAR, month=1, day=1)):
        cursor = self.connection.cursor(cursor_factory=pg_extras.DictCursor)
        cursor.execute(self.SELECT_ALL_BY_DATE, (start_date, end_date,))
        return (Session(**k) for k in cursor)
