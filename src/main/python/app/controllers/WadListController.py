import sys

from app.views.WadListView import WadListView

class WadListController:
    def __init__(self, root, models):
        self.wads = models.wads
        self.view = WadListView(root, self)

        self.wads.subscribe(self.subscription)
    
    def subscription(self, msg):
        action, data = msg

        if action == self.wads.CREATE:
            self.view.append_wad(self.wads.find(data))
        elif action == self.wads.REMOVE:
            self.view.remove_item(data)
        elif action == self.wads.LOADED:
            self.view.append_wad(data)

    def remove_wad(self, id):
        self.wads.remove(id)
