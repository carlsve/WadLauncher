import glob, os, functools, sys

from core.base.Model import Model
from app.config import Config
from app.workers.IwadLoaderWorker import iwad_loader_worker_wrapper

class Iwads(Model):
    LOADED = 'IWAD_LOADED'
    LOADED_ALL = 'IWAD_LOADED_ALL'

    def __init__(self):
        Model.__init__(self)
        iwad_loader_worker_wrapper([self.loaded], [self.loaded_all])

    def loaded(self, obj):
        id = self.create(**obj)
        self.broadcast((self.LOADED, self.find(id)))

    def loaded_all(self):
        self.broadcast((self.LOADED_ALL,None))

sys.modules[__name__] = Iwads()