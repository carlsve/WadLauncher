import os, glob

from PyQt5.QtCore import QThread, pyqtSignal

from app.config import Config
from app.workers.WorkerPool import *

def iwad_loader_worker_wrapper(progress_handlers=[], done_handlers=[]):
    worker = IwadLoaderWorker()

    for handler in progress_handlers:
        worker.progress.connect(handler)

    for handler in done_handlers:
        worker.done.connect(handler)

    WorkerPool.Instance().start(worker)

class IwadLoaderWorker(QThread):
    done = pyqtSignal(object)
    progress = pyqtSignal(object)

    def __init__(self):
        super(IwadLoaderWorker, self).__init__()
        config = Config.Instance()
        self.path = os.path.expanduser(config['PATHS']['IWADS_PATH'])

    def run(self):
        files = glob.glob(os.path.join(os.path.abspath(self.path), '*.wad'))

        for file in files:
            with open(file, 'rb') as fd:
                wad_type = fd.read(4).decode("utf-8")
                if wad_type == 'IWAD':
                    self.progress.emit({ 'name': os.path.basename(file), 'path': file })

        self.done.emit(None)
