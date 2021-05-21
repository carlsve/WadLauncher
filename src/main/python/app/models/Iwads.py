import glob, os, functools, sys

from core.base.Model import Model
from app.config import Config
from app.workers.IwadLoaderWorker import iwad_loader_worker_wrapper

class Iwads(Model):
    IWAD_LOADED = 'IWAD_LOADED'
    IWAD_LOADED_ALL = 'IWAD_LOADED_ALL'

    def __init__(self):
        Model.__init__(self)
        iwad_loader_worker_wrapper([self.iwad_loaded], [self.iwad_loaded_all])

    def iwad_loaded(self, obj):
        id = self.create(**obj)
        self.broadcast((self.IWAD_LOADED, self.find(id)))

    def iwad_loaded_all(self):
        self.broadcast((self.IWAD_LOADED_ALL,None))

sys.modules[__name__] = Iwads()