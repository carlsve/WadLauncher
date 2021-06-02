import pathlib, os, urllib

from PyQt5.QtCore import QThread, pyqtSignal

from app.config import Config
from app.workers.WorkerPool import *

MIRRORS = {
    'GERMANY': 'ftp://ftp.fu-berlin.de/pc/games/idgames/',
    'IDAHO': 'ftp://mirrors.syringanetworks.net/idgames/',
    'GREECE': 'ftp://ftp.ntua.gr/pub/vendors/idgames/',
    'GREECE (HTTP)': 'http://ftp.ntua.gr/pub/vendors/idgames/',
    'TEXAS': 'http://ftp.mancubus.net/pub/idgames/',
    'GERMANY (TLS)': 'https://www.quaddicted.com/files/idgames/',
    'NEW YORK': 'http://youfailit.net/pub/idgames/',
    'VIRGINIA': 'http://www.gamers.org/pub/idgames/'
}

def download_worker_wrapper(item, progress_handlers=[], download_handlers=[], mirror='GERMANY'):
    worker = DownloadWorker(item, mirror)
    for handler in progress_handlers:
        worker.downloading.connect(handler)
    for handler in download_handlers:
        worker.downloaded.connect(handler)

    WorkerPool.Instance().start(worker)

class DownloadWorker(QThread):
    downloading = pyqtSignal(int, int, int)
    downloaded = pyqtSignal(str)

    def __init__(self, item, mirror='GERMANY', parent=None):
        QThread.__init__(self, parent)

        config = Config.Instance()
        base_path = os.path.expanduser(config['PATHS']['BASE_PATH'])

        mirror_url = MIRRORS[mirror or 'GERMANY']
        dirname = item['dir']
        filename = item['filename']

        self.temp_dir = os.path.join(base_path, 'temp')
        self.download_url = mirror_url + dirname + filename
        self.save_path = os.path.join(self.temp_dir, filename)

    def run(self):
        pathlib.Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
        file_path, _ = urllib.request.urlretrieve(self.download_url, self.save_path, self.progress_handler)
        self.downloaded.emit(file_path)

    def progress_handler(self, count, block_size, total_size):
        self.downloading.emit(count, block_size, total_size)
