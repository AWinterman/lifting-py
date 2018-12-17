from datetime import datetime, MAXYEAR, MINYEAR

from psycopg2 import extras as pg_extras
from psycopg2 import pool

from lift.models import Session

from contextlib import contextmanager

cursor_factory = pg_extras.DictCursor


class Storage:
    def __init__(self, config):
        c = {}
        if config.dbname:
            c['dbname'] = config.dbname
        if config.user:
            c['user'] = config.user
        if config.password:
            c['password'] = config.password
        if config.host:
            c['host'] = config.host
        if config.port:
            c['port'] = config.port

        if config.socket:
            c['query'] = {'unix_socket': config.socket}

        if config.sslrootcert and config.sslcert and config.sslkey:
            c['sslmode'] = 'verify-ca'
            c['sslrootcert'] = config.sslrootcert
            c['sslcert'] = config.sslcert
            c['sslkey'] = config.sslkey

        c['cursor_factory'] = cursor_factory

        self.pool = pool.ThreadedConnectionPool(1, 10, **c)

    @contextmanager
    def cursor(self):
        conn = self.pool.getconn()
        yield conn.cursor()
        conn.commit()
        self.pool.putconn(conn)

    def init_db(self):
        self.schema()

    DROP = """
        DROP TABLE IF EXISTS sessions;
        DROP TABLE IF EXISTS users;
    """

    def drop(self):
        with self.cursor() as cursor:
            cursor.execute(self.DROP)

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
           user_id varchar
        );
    """

    def schema(self):
        with self.cursor() as cursor:
            cursor.execute(self.SCHEMA)

    INSERT = """
        INSERT INTO sessions (
           exercise,
           effort,
           reps,
           weight,
           duration,
           session_date,
           failure,
           user_id
        ) VALUES (
            %(exercise)s,
            %(effort)s,
            %(reps)s,
            %(weight)s,
            %(duration)s,
            %(session_date)s,
            %(failure)s
            %(user_id)s
        ) RETURNING *
    """

    def insert(self, user_id, *sessions):
        with self.cursor() as cursor:
            for session in sessions:
                for sql in session.to_sql():
                    sql['user_id'] = user_id
                    cursor.execute(self.INSERT, sql)
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
        FROM SESSIONS WHERE session_date BETWEEN %s and %s and user_id = %s
        GROUP BY session_date, exercise, reps, weight, duration, failure
        ORDER BY session_date asc, exercise
    """

    def iterate(
            self,
            user,
            limit=None,
            start_date=None,
            end_date=None):
        start_date = start_date or datetime(year=MINYEAR, month=1, day=1)
        end_date = end_date or datetime(year=MAXYEAR, month=1, day=1)
        with self.cursor() as cursor:
            cursor.execute(
                self.SELECT_ALL_BY_DATE,
                (start_date, end_date, user,)
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
        FROM SESSIONS WHERE session_date = %s and user_id = %s
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
        FROM SESSIONS WHERE id = %s and user_id = %s
        ORDER BY exercise
    """

    def get(self, user_id, date=None, id=None):
        assert date or id
        with self.cursor() as cursor:
            if date:
                cursor = self.connection.cursor(cursor_factory=cursor_factory)
                cursor.execute(self.SESSION_BY_DATE, (date, user_id, ))
                for session_dict in cursor:
                    yield session_dict

            if id:
                cursor = self.connection.cursor()
                cursor.execute(self.SESSION_BY_ID, (date, user_id, ))
                for session_dict in cursor:
                    yield session_dict

    EXERCISES = """
        SELECT DISTINCT exercise from sessions where user_id = %s;
    """

    def all_exercises(self, user):
        with self.cursor() as cursor:
            cursor = self.connection.cursor()
            cursor.execute(self.EXERCISES, user)
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
        ) WHERE sessions.id = %{id}s and user_id = %{user_id} RETURNING *
    """

    def update(self, user_id, id, session):
        with self.cursor() as cursor:
            vals = {id: id}
            attrs = list(session.to_sql())
            if len(attrs) > 1:
                raise ValueError(
                        "cannot update session model with multiple sets"
                )
            vals.update(attrs[0])
            vals['user_id'] = user_id
            cursor.execute(self.UPDATE, vals)
            return cursor.fetchone()

    DELETE_BY_ID = """
        DELETE FROM sessions WHERE user_id = %{user}s AND id=%{id} RETURNING *
    """

    DELETE_BY_DATE = """
    DELETE FROM sessions WHERE
        user_id = %s AND
        session_date=%
        RETURNING *
    """

    DELETE_BY_DATE_AND_EXERCISE = """
        DELETE FROM sessions WHERE
        user_id = %s AND
        session_date=%s AND
        exercise=%s
        RETURNING *
    """

    def delete(self, user_id, id=None, session_date=None, exercise=None):
        assert id or session_date or exercise
        with self.cursor() as cursor:
            if id:
                cursor.execute(self.DELETE_BY_ID, (user_id, id,))
            elif exercise and session_date:
                cursor.execute(self.DELETE_BY_DATE_AND_EXERCISE,
                               (user_id, session_date, exercise))
            elif session_date:
                cursor.execute(self.DELETE_BY_DATE, user_id, session_date)
                return cursor.fetchone()
            return Session.from_sql(cursor)
