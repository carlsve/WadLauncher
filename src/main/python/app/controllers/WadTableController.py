import sys

from app.views.WadTableView import WadTableView

class WadTableController:
    def show(self, root, models):
        self.wads = models.wads
        self.view = WadTableView(root, self)
        self.wads.subscribe(self.wad_subscription)

    def wad_subscription(self, msg):
        action, data = msg

        if (action == 'CREATE_WAD'):
            self.view.add_item(self.wads.find(data))
        elif action == 'REMOVE_WAD':
            self.view.remove_item(data)
        elif action == self.wads.WADS_LOADED:
            self.view.appendRow(data)

    def remove_wad(self, wad):
        self.wads.remove(wad['id'])

sys.modules[__name__] = WadTableController()