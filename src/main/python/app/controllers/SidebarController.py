import sys

from app.views.SidebarView import SidebarView

class SidebarController:
    def __init__(self):
        pass

    def show(self, root, models):
        self.wads = models.wads
        self.view = SidebarView(root, self.wads, self)
        self.root = root
        self.wads.subscribe(self.subscription)
    
    def subscription(self, args):
        action, data = args

        if action == self.wads.SELECTED:
            self.view.show_dir(data)
 
    def random_clicked(self):
        self.wads.idgames_random()
