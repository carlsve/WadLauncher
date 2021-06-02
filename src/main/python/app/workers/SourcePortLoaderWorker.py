import os

from PyQt5.QtCore import QThread, pyqtSignal

from app.config import Config
from configparser import ConfigParser
from app.workers.WorkerPool import *

def source_port_loader_worker_wrapper(progress_handlers=[], done_handlers=[]):
    worker = SourcePortLoaderWorker()

    for handler in progress_handlers:
        worker.progress.connect(handler)

    for handler in done_handlers:
        worker.done.connect(handler)

    WorkerPool.Instance().start(worker)

class SourcePortLoaderWorker(QThread):
    done = pyqtSignal(object)
    progress = pyqtSignal(object)

    def __init__(self):
        super(SourcePortLoaderWorker, self).__init__()
        config = Config.Instance()
        config = Config.Instance()
        base_path = os.path.expanduser(config['PATHS']['BASE_PATH'])
        self.path = os.path.join(base_path, 'source_ports.ini')

    def run(self):
        cfg = ConfigParser(allow_no_value=True)
        cfg.read(self.path)
        sections = cfg.sections()

        for section in sections:
            self.progress.emit(cfg[section])

        self.done.emit(None)
