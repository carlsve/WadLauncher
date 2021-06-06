import sys

from app.views.WadTableView import WadTableView

class WadTableController:
    def show(self, root, models):
        self.wads = models.wads
        self.view = WadTableView(root, self)
        self.wads.subscribe(self.wad_subscription)

    def wad_subscription(self, msg):
        action, data = msg

        if action == self.wads.CREATE:
            self.view.appendRow(self.wads.find(data))
        elif action == self.wads.REMOVE:
            self.view.remove_item(data)
        elif action == self.wads.LOADED:
            self.view.appendRow(data)

    def remove_wad(self, id):
        self.wads.remove(id)
