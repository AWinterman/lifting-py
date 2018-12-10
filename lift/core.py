from lift.storage import Storage
from lift.exporter import GDocsExporter
from lift.config import Config


from os import environ


class Core(Storage, GDocsExporter):
    def __init__(self, config):
        Storage.__init__(self, config)
        GDocsExporter.__init__(self, self, config)


def create():
    config = Config(environ)
    return Core(config)
