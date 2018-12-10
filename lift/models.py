from datetime import date, datetime
from collections import OrderedDict


class Session:
    NAMES = (
        'exercise',
        'effort',
        'reps',
        'sets',
        'weight',
        'duration',
        'session_date',
        'failure',
    )

    def __init__(
            self,
            exercise=None,
            effort=None,
            reps=None,
            sets=None,
            weight=None,
            duration=None,
            session_date=None,
            failure=False):
        self.exercise = exercise
        self.effort = effort
        self.reps = reps
        self.weight = weight
        self.duration = duration
        self.session_date = session_date
        self.sets = sets
        self.failure = failure

    def to_sql(self):
        return (
            {
                "exercise": self.exercise,
                "effort": self.effort,
                "reps": self.reps,
                "weight": self.weight,
                "duration": self.duration,
                "session_date": self.session_date,
                "failure": self.failure,
            } for i in range(self.sets if self.sets else 1))

    def to_dict(self):
        d = OrderedDict({})

        if self.session_date:
            d["session_date"] = str(self.session_date)

        d.update({
                "exercise": self.exercise,
                "reps": self.reps,
                "sets": self.sets,
        })

        if self.effort:
            d["effort"] = float(self.effort)
        if self.weight:
            d["weight"] = float(self.weight)
        if self.duration:
            d["duration"] = str(self.duration)
        if self.failure:
            d["failure"] = self.failure
        return d

    @staticmethod
    def _check_and_strip(key, line):
        return key in line and line[key] and line[key].strip()

    @staticmethod
    def from_dict(line):
        session = {
                'exercise': None,
                'effort': None,
                'reps': None,
                'sets': None,
                'weight': None,
                'duration': None,
                'session_date': None,
        }
        date_elements = line['Date'].strip().split('/')
        month = int(date_elements[0])
        day = int(date_elements[1])
        year = int(date_elements[2])

        dt = date(year, month, day)

        if None in line:
            del line[None]

        session['session_date'] = dt
        session['exercise'] = line['Exercise'].strip()
        assert session['exercise']

        if Session._check_and_strip('PerceivedEffort', line):
            session['effort'] = line['PerceivedEffort'].strip()

        if Session._check_and_strip('Repetitions', line):
            session['reps'] = int(line['Repetitions'])

        if Session._check_and_strip('SetsCompleted', line):
            session['sets'] = int(line['SetsCompleted'])

        if Session._check_and_strip('Weight', line):
            session['weight'] = float(line['Weight'])

        if 'Time' in line and line['Time']:
            try:
                session['duration'] =\
                    datetime.strptime(
                            line['Time'],
                            '%H:%M:%S'
                        ) - datetime(year=1900, month=1, day=1)
            except ValueError:
                try:
                    session['duration'] =\
                        datetime.strptime(
                                line['Time'],
                                '%M:%S'
                        ) - datetime(year=1900, month=1, day=1)
                except ValueError:
                    pass

        return Session(**session)

    def __str__(self):
        return "Session" + \
                str({k: v for k, v in self.to_dict().items() if v is not None})
