import psycopg2 as pg
from datetime import datetime, MAXYEAR, MINYEAR
from psycopg2 import extras as pg_extras

from lift.models import Session
from lift.config import Config

cursor_factory = pg_extras.DictCursor


class Storage(Config):
    def __init__(self, config):
        c = {}
        if config.dbname:
            c['dbname'] = config.dbname
        if config.user:
            c['user'] = config.user
        if config.password:
            c['password'] = config.password
        if config.host:
            c['hostaddr'] = config.host
        if config.port:
            c['port'] = config.port

        if config.sslrootcert and config.sslcert and config.sslkey:
            c['sslmode'] = 'verify-ca'
            c['sslrootcert'] = config.sslrootcert
            c['sslcert'] = config.sslcert
            c['sslkey'] = config.sslkey

        self.connection = pg.connect(**c)
        self.exercises = self.all_exercises()

    def init_db(self):
        self.connection.execute("DROP TABLE IF EXISTS sessions")
        self.schema()

    DROP = """
        DROP TABLE IF EXISTS sessions;
        DROP TABLE IF EXISTS users;
    """

    def drop(self):
        cursor = self.connection.cursor()
        cursor.execute(self.DROP)
        self.connection.commit()

    SCHEMA = """
        CREATE TABLE IF NOT EXISTS sessions (
           id serial primary key,
           exercise varchar,
           effort decimal,
           reps int,
           weight decimal,
           duration interval,
           session_date date,
           failure boolean default false,
           user_id references users(id)
        );

        CREATE TABLE IF NOT EXISTS users (
           id serial primary key,
           name varchar,
           email varchar,
           birthday int,
        );
    """

    def schema(self):
        cursor = self.connection.cursor()
        cursor.execute(self.SCHEMA)
        self.connection.commit()

    INSERT = """
        INSERT INTO sessions (
           exercise,
           effort,
           reps,
           weight,
           duration,
           session_date,
           failure
        ) VALUES (
            %(exercise)s,
            %(effort)s,
            %(reps)s,
            %(weight)s,
            %(duration)s,
            %(session_date)s,
            %(failure)s
        ) RETURNING *
    """

    def insert(self, *sessions):
        cursor = self.connection.cursor(cursor_factory=cursor_factory)
        for session in sessions:
            for sql in session.to_sql():
                cursor.execute(self.INSERT, sql)
                self.exercises.add(session.exercise)
                self.connection.commit()
                result = cursor.fetchone()
                if result:
                    yield result

    SELECT_ALL_BY_DATE = """
        SELECT
            session_date,
            exercise,
            reps,
            weight,
            duration,
            failure,
            count(*) as sets
        FROM SESSIONS WHERE session_date BETWEEN %s and %s
        GROUP BY session_date, exercise, reps, weight, duration, failure
        ORDER BY session_date asc, exercise
    """

    def iterate(
            self,
            limit=None,
            start_date=None,
            end_date=None):
        start_date = start_date or datetime(year=MINYEAR, month=1, day=1)
        end_date = end_date or datetime(year=MAXYEAR, month=1, day=1)
        cursor = self.connection.cursor(cursor_factory=cursor_factory)
        cursor.execute(
            self.SELECT_ALL_BY_DATE,
            (start_date, end_date,)
        )
        return (
            Session(**session_dict)
            for i, session_dict in enumerate(cursor)
            if limit and i < limit
        )

    SESSION_BY_DATE = """
        SELECT
            id,
            session_date,
            exercise,
            reps,
            weight,
            duration,
            failure,
        FROM SESSIONS WHERE session_date = %s
        ORDER BY exercise
    """

    SESSION_BY_ID = """
        SELECT
            id,
            session_date,
            exercise,
            reps,
            weight,
            duration,
            failure,
        FROM SESSIONS WHERE id = %s
        ORDER BY exercise
    """

    def get(self, date=None, id=None):
        if date:
            cursor = self.connection.cursor(cursor_factory=cursor_factory)
            cursor.execute(self.SESSION_BY_DATE, (date,))
            for session_dict in cursor:
                yield session_dict

        if id:
            cursor = self.connection.cursor(cursor_factory=cursor_factory)
            cursor.execute(self.SESSION_BY_ID, (date,))
            for session_dict in cursor:
                yield session_dict

    EXERCISES = """
        SELECT DISTINCT exercise from sessions;
    """

    exercises = set()

    def all_exercises(self):
        cursor = self.connection.cursor()
        cursor.execute(self.EXERCISES)
        return {e[0] for e in cursor}

    UPDATE = """
        UPDATE sessions SET
           exercise = %(exercise)s,
           effort %(effort)s,
           reps %(reps)s
           weight %(weight)s,
           duration %(duration)s,
           session_date %(session_date)s,
           failure %(failure)s
        ) WHERE sessions.id = %{id}s RETURNING *
    """

    def update(self, id, session):
        cursor = self.connection.cursor(cursor_factory=pg_extras.DictCursor)
        vals = {id: id}
        attrs = list(session.to_sql())
        if len(attrs) > 1:
            raise ValueError("cannot update session model with multiple sets")
        vals.update(attrs[0])
        cursor.execute(self.UPDATE, vals)
        return cursor.fetchone()
