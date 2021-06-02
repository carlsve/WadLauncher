import sys

from core.base.Model import Model

from app.workers.IwadLoaderWorker import iwad_loader_worker_wrapper
from app.schemas.Iwad import Iwad

class Iwads(Model):
    LOADED = 'IWAD_LOADED'
    LOADED_ALL = 'IWAD_LOADED_ALL'

    def __init__(self):
        Model.__init__(self, schema=Iwad)
        iwad_loader_worker_wrapper([self.loaded], [self.loaded_all])

    def loaded(self, obj):
        id = self.create(**obj)
        self.broadcast((self.LOADED, self.find(id)))

    def loaded_all(self):
        self.broadcast((self.LOADED_ALL,None))

sys.modules[__name__] = Iwads()