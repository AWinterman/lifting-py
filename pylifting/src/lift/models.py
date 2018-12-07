from datetime import date, datetime


class Session:
    NAMES = [
        ('exercise', 'Exercise'),
        ('effort',  'PerceivedEffort'),
        ('reps', 'Repetitions'),
        ('sets',  'SetsCompleted'),
        ('weight', 'Weight'),
        ('duration', 'Time'),
        ('session_date',  'Date'),
    ]

    def __init__(
            self,
            exercise=None,
            effort=None,
            reps=None,
            sets=None,
            weight=None,
            duration=None,
            session_date=None):
        self.exercise = exercise
        self.effort = effort
        self.reps = reps
        self.weight = weight
        self.duration = duration
        self.session_date = session_date
        self.sets = sets

    def to_sql(self):
        return {
                "exercise": self.exercise,
                "effort": self.effort,
                "reps": self.reps,
                "sets": self.sets,
                "weight": self.weight,
                "duration": self.duration,
                "session_date": self.session_date,
        }

    def to_dict(self):
        return {
                "exercise": self.exercise,
                "effort": self.effort,
                "reps": self.reps,
                "sets": self.sets,
                "weight": self.weight,
                "duration": str(self.duration),
                "session_date": str(self.session_date),
        }

    def _check_and_strip(key, line):
        return key in line and line[key] and line[key].strip()

    def toTsvDict(self):
        d = self.toDict()
        return {tsv: d[comp] for comp, tsv in self.NAMES}

    def fromTsvDict(line):
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
                    datetime.strptime(line['Time'], '%H:%M:%S')
            except ValueError:
                try:
                    session['duration'] =\
                        datetime.strptime(line['Time'], '%M:%S')
                except ValueError:
                    pass

        return Session(**session)

    def __str__(self):
        return "Session" + \
                str({k: v for k, v in self.to_dict().items() if v is not None})
