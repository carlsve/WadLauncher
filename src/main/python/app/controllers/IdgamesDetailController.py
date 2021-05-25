import sys

from app.views.IdgamesDetailView import IdgamesDetailView

from app.workers.DWApiWorker import *
from app.workers.DownloadWorker import *
from app.helpers.StackedWidgetSelector import *

class IdgamesDetailController:
    def __init__(self):
        pass
    
    def show(self, root, models):
        self.root = root
        self.wads = models.wads
        self.view = IdgamesDetailView(root, self)
        self.wads.subscribe(self.wads_listener)

    def wads_listener(self, args):
        action, data = args

        if action in [self.wads.RANDOM, self.wads.DETAIL]:
            result, err = data
            self.data = result
            already_downloaded = bool(self.wads.find_by(id=result['id']))
            self.view.set_data(result, already_downloaded)
            display_widget(self.root, WidgetIndices.IDGAMES_DETAIL)
        elif action == self.wads.DOWNLOAD_PROGRESS:
            id, progress = data
            if id == self.view.idgames_response_widget.id:
                self.view.idgames_response_widget.download_progress(*progress)
        elif action == self.wads.DOWNLOAD_FINISHED:
            id = data
            if id == self.view.idgames_response_widget.id:
                self.view.idgames_response_widget.download_finished()

    def download(self, id, mirror):
        if self.data == None:
            return
        if id != self.data['id']:
            return

        self.wads.idgames_download(self.data, mirror)

sys.modules[__name__] = IdgamesDetailController()