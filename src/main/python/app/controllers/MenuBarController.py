import sys

from app.views.MenuBarView import MenuBarView

class MenuBarController:
    def __init__(self):
        pass
    
    def show(self, root, models):
        self.view = MenuBarView(root, self)
        self.wads = models.wads
    
    def select_unzip_file(self, file_path):
        self.wads.extract_archive(file_path, should_remove_archive=False, item={}, detail_type='imported')

sys.modules[__name__] = MenuBarController()