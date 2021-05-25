import sys, os

from core.base.Model import Model
from app.workers.SourcePortLoaderWorker import source_port_loader_worker_wrapper

class SourcePorts(Model):
    LOADED = 'SOURCE_PORTS_LOADED'
    LOADED_ALL = 'SOURCE_PORTS_LOADED_ALL'

    def __init__(self):
        Model.__init__(self)
        source_port_loader_worker_wrapper([self.loaded], [self.loaded_all])
    
    def loaded(self, obj):
        id = self.create(**obj)
        self.broadcast((self.LOADED, self.find(id)))

    def loaded_all(self):
        self.broadcast((self.LOADED_ALL, None))

sys.modules[__name__] = SourcePorts()