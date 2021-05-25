import os, json, uuid

from PyQt5.QtCore import QThread, pyqtSignal

from app.config import Config
from app.workers.WorkerPool import *

def wad_loader_worker_wrapper(progress_handlers=[], done_handlers=[], **params):
    worker = WadLoaderWorker(**params)

    for handler in progress_handlers:
        worker.progress.connect(handler)

    for handler in done_handlers:
        worker.done.connect(handler)

    WorkerPool.Instance().start(worker)

class WadLoaderWorker(QThread):
    done = pyqtSignal(object)
    progress = pyqtSignal(object)

    def __init__(self, **params):
        super(WadLoaderWorker, self).__init__()
        config = Config.Instance()
        self.path = os.path.expanduser(config['PATHS']['WADS_PATH'])
        self.exts = ['.wad', '.pk3', '.deh', '.bex']

    def run(self):
        for base_dir in os.listdir(self.path):
            dir = os.path.join(self.path, base_dir)
            if os.path.isdir(os.path.join(self.path, dir)):
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
                has_metadata = 'metadata.json' in os.listdir(dir)
                with open(os.path.join(dir, 'metadata.json'), 'r' if has_metadata else 'w') as metadata_file:
                    if has_metadata:
                        loaded_wad.update(json.load(metadata_file))
                    else:
                        loaded_wad.update({ 'id': str(uuid.uuid1()) })
                        json.dump(loaded_wad, metadata_file, ensure_ascii=False, indent=4)
                try:
                    loaded_wad.update(file_path=loaded_wad['file_paths'][0])
                except IndexError:
                    loaded_wad.update(file_path=None, error='No mod file found (.wad or .pk3)')
                self.progress.emit(loaded_wad)

        self.done.emit(None)



