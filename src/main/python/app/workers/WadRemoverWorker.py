import os, json, uuid, shutil

from PyQt5.QtCore import QThread, pyqtSignal

from app.config import Config
from app.workers.WorkerPool import *

def wad_remover_worker_wrapper(dir, progress_handlers=[], done_handlers=[]):
    worker = WadRemoverWorker(dir)

    for handler in progress_handlers:
        worker.progress.connect(handler)

    for handler in done_handlers:
        worker.done.connect(handler)

    WorkerPool.Instance().start(worker)

class WadRemoverWorker(QThread):
    done = pyqtSignal(object)
    progress = pyqtSignal(object)

    def __init__(self, dir):
        super(WadRemoverWorker, self).__init__()
        self.dir = dir

    def run(self):
        shutil.rmtree(self.dir)
        self.done.emit(None)
