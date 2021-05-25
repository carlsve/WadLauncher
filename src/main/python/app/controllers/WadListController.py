import sys

from app.views.WadListView import WadListView

class WadListController:
    def __init__(self):
        pass
    
    def show(self, root, models):
        self.wads = models.wads
        self.view = WadListView(root, self)

        self.wads.subscribe(self.subscription)
    
    def subscription(self, msg):
        action, data = msg

        if (action == self.wads.WADS_CREATED):
            self.view.appendWad(self.wads.find(data))
        elif action == 'REMOVE_WAD':
            self.view.remove_item(data)
        elif action == self.wads.WADS_LOADED:
            self.view.appendWad(data)

    def remove_wad(self, wad):
        self.wads.remove(wad['id'])

sys.modules[__name__] = WadListController()