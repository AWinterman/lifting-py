
from os import environ

import logging
import csv

from lift.models import Session
from lift.storage import Storage

tsv_history = environ['HISTORY']

storage = Storage(environ)

with open(tsv_history) as history:
    reader = csv.DictReader(history, delimiter='\t')
    for line in reader:
        try:
            s = Session.from_dict(line)
            storage.insert(s)
        except (TypeError, ValueError):
            logging.error("error loading %s", line, exc_info=True)
