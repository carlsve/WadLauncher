import sys, json, os, uuid
from configparser import ConfigParser

from PyQt5.QtCore import QThread, pyqtSignal

from app.config import Config
from app.workers.WorkerPool import *

def category_saver_worker_wrapper(items, progress_handlers=[], done_handlers=[]):
    worker = CategorySaverWorker(items)

    for handler in progress_handlers:
        worker.progress.connect(handler)

    for handler in done_handlers:
        worker.done.connect(handler)

    WorkerPool.Instance().start(worker)

class CategorySaverWorker(QThread):
    done = pyqtSignal(object)
    progress = pyqtSignal(object)

    def __init__(self, items):
        super(CategorySaverWorker, self).__init__()
        config = Config.Instance()
        base_path = os.path.expanduser(config['PATHS']['BASE_PATH'])
        self.path = os.path.join(base_path, 'user_categories.ini')
        self.items = items

    def run(self):
        cfg = ConfigParser(allow_no_value=True)
        for item in self.items:
            id = item['id']
            if not cfg.has_section(id):
                cfg.add_section(id)
            cfg.set(id, 'id', id)
            cfg.set(id, 'is_root', item.get('is_root', 'False'))
            cfg.set(id, 'name', item['name'])
            cfg.set(id, 'children', json.dumps(item['children']))

        with open(os.path.abspath(self.path), 'w+') as config_file:
            cfg.write(config_file)

        self.done.emit(None)
