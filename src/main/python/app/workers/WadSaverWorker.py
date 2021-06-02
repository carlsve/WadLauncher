import os, json

from PyQt5.QtCore import QThread, pyqtSignal

from app.workers.WorkerPool import *

def wad_saver_worker_wrapper(wad, progress_handlers=[], done_handlers=[]):
    worker = WadSaverWorker(wad)

    for handler in progress_handlers:
        worker.progress.connect(handler)

    for handler in done_handlers:
        worker.done.connect(handler)

    WorkerPool.Instance().start(worker)

class WadSaverWorker(QThread):
    done = pyqtSignal(object)
    progress = pyqtSignal(object)

    def __init__(self, wad):
        super(WadSaverWorker, self).__init__()
        self.wad = wad

    def run(self):
        metadata_file_path = os.path.join(self.wad['path'], 'metadata.json')
        with open(metadata_file_path, 'w+', encoding='utf-8') as f:
            json.dump(self.wad, f, ensure_ascii=False, indent=4)

        self.done.emit(None)



