import sys

from app.views.WadDirView import WadDirView

class WadDirController:
    def __init__(self):
        pass

    def show(self, root, models):
        self.wads = models.wads
        self.view = WadDirView(root)

        self.wads.subscribe(self.select_wad_listener)
    
    def select_wad_listener(self, args):
        action, _ = args

        if action == 'SELECT_WAD':
            dir_files = self.wads.get_dir_contents()

            self.view.show_dirs(dir_files)

sys.modules[__name__] = WadDirController()