import sys, os

from core.base.Model import Model
from app.workers.SourcePortLoaderWorker import source_port_loader_worker_wrapper

class SourcePorts(Model):
    SOURCE_PORTS_LOADED = 'SOURCE_PORTS_LOADED'
    SOURCE_PORTS_LOADED_ALL = 'SOURCE_PORTS_LOADED_ALL'

    def __init__(self):
        Model.__init__(self)
        source_port_loader_worker_wrapper([self.source_port_loaded], [self.source_port_loaded_all])
    
    def source_port_loaded(self, obj):
        id = self.create(**obj)
        self.broadcast((self.SOURCE_PORTS_LOADED, self.find(id)))

    def source_port_loaded_all(self):
        self.broadcast((self.SOURCE_PORTS_LOADED_ALL, None))

sys.modules[__name__] = SourcePorts()