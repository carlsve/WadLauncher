import os, json

from PyQt5.QtCore import QThread, pyqtSignal

from app.config import Config
from app.workers.WorkerPool import *

def wad_importer_worker_wrapper(dir, progress_handlers=[], done_handlers=[]):
    worker = WadImporterWorker(dir)

    for handler in progress_handlers:
        worker.progress.connect(handler)

    for handler in done_handlers:
        worker.done.connect(handler)

    WorkerPool.Instance().start(worker)

class WadImporterWorker(QThread):
    done = pyqtSignal(object)
    progress = pyqtSignal(object)

    def __init__(self, dir):
        super(WadImporterWorker, self).__init__()
        config = Config.Instance()
        self.path = os.path.expanduser(config['PATHS']['WADS_PATH'])
        self.exts = ['.wad', '.pk3', '.deh', '.bex']
        self.dir = dir

    def run(self):
        dir = self.dir
        file_paths = []
        for (root, _, files) in os.walk(dir):
            file_paths.extend(
                [os.path.join(root, file) for file in files if any(file.lower().endswith(ext) for ext in self.exts)]
            )
        loaded_wad = {
            'name': os.path.basename(dir),
            'path': dir,
            'file_paths': file_paths
        }
        if 'metadata.json' in os.listdir(dir):
            with open(os.path.join(dir, 'metadata.json'), 'r') as json_file:
                loaded_wad.update(json.load(json_file))
        try:
            loaded_wad.update(file_path=loaded_wad['file_paths'][0])
        except IndexError:
            loaded_wad.update(file_path=None, error='No mod file found (.wad or .pk3)')
        self.done.emit(loaded_wad)
