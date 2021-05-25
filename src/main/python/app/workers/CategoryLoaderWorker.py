import sys, json, os, uuid
from configparser import ConfigParser

from PyQt5.QtCore import QThread, pyqtSignal

from app.config import Config
from app.workers.WorkerPool import *

def category_loader_worker_wrapper(progress_handlers=[], done_handlers=[]):
    worker = CategoryLoaderWorker()

    for handler in progress_handlers:
        worker.progress.connect(handler)

    for handler in done_handlers:
        worker.done.connect(handler)

    WorkerPool.Instance().start(worker)

class CategoryLoaderWorker(QThread):
    done = pyqtSignal(object)
    progress = pyqtSignal(object)

    def __init__(self):
        super(CategoryLoaderWorker, self).__init__()
        config = Config.Instance()
        base_path = os.path.expanduser(config['PATHS']['BASE_PATH'])
        self.path = os.path.join(base_path, 'user_categories.ini')

    def run(self):
        cfg = ConfigParser(allow_no_value=True)
        cfg.read(self.path)
        if len(cfg.sections()) == 0:
            root_id = str(uuid.uuid1())
            cfg.add_section(root_id)
            cfg.set(root_id, 'id', root_id)
            cfg.set(root_id, 'is_root', 'True')
            cfg.set(root_id, 'name', 'root')
            cfg.set(root_id, 'children', '[]')
            cfg.set(root_id, 'warning', 'If you remove this section, the app will no longer recognize other categories.')
            with open(os.path.abspath(self.path), 'w+') as config_file:
                cfg.write(config_file)

        sections = cfg.sections()
        for section in sections:
            category = dict(cfg[section])
            children_str = category['children']
            category['children'] = json.loads(children_str)
            self.progress.emit(category)

        self.done.emit(None)
