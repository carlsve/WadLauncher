import sys

from app.views.WadTableView import WadTableView

class WadTableController:
    def __init__(self, root, models):
        self.wads = models.wads
        self.view = WadTableView(root, self)
        self.wads.subscribe(self.wad_subscription)

    def wad_subscription(self, msg):
        action, data = msg

        if action == self.wads.CREATE:
            self.view.append_row(self.wads.find(data))
        elif action == self.wads.REMOVE:
            self.view.remove_item(data)
        elif action == self.wads.LOADED:
            self.view.append_row(data)

    def remove_wad(self, id):
        self.wads.remove(id)
