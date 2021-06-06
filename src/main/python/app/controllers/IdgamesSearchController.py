import sys

from app.views.IdgamesSearchView import IdgamesSearchView

from app.workers.DownloadWorker import *
from app.helpers.StackedWidgetSelector import *

class IdgamesSearchController:
    def __init__(self):
        pass
    
    def show(self, root, models):
        self.view = IdgamesSearchView(root, self)
        self.wads = models.wads
        self.root = root
        self.wads.subscribe(self.wads_listener)

    def wads_listener(self, args):
        action, data = args

        if action == self.wads.SEARCH:
            self.view.updateResults(data)
            self.set_search_results(data)
        elif action == self.wads.DOWNLOAD_PROGRESS:
            id, progress = data
            if id in self.view.search_results_widgets:
                self.view.search_results_widgets[id].idgames_response_widget.download_progress(*progress)
        elif action == self.wads.DOWNLOAD_FINISHED:
            id = data
            if id in self.view.search_results_widgets:
                self.view.search_results_widgets[id].idgames_response_widget.download_finished()

    def search(self, text, search_by):
        self.wads.idgames_search(text, search_by)

    def set_search_results(self, result_blob):
        self.search_result = result_blob[0].get('file', [])
        if type(self.search_result) != list:
            self.search_result = [self.search_result]

    def display_detail(self, wad_id):
        self.wads.idgames_get(wad_id)

    def download(self, id):
        data = next((x for x in self.search_result if x['id'] == id), None)
        if data == None:
            return

        self.wads.idgames_download(data)
