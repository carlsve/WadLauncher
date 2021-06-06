import sys

from app.views.WadTreeView import WadTreeView

class WadTreeController:
    def __init__(self, root, models):
        self.models = models
        self.view = WadTreeView(root, self)
        
        self.models.wads.subscribe(self.subscription)
        self.models.categories.subscribe(self.subscription)
    
    def subscription(self, msg):
        action, data = msg

        if action == self.models.wads.LOADED:
            self.view.appendWad(data)
        elif action == self.models.wads.LOADED_ALL:
            self.view.finish_loading('wads')
        elif action == self.models.wads.REMOVE:
            self.view.wad_removed(data)
        elif action == self.models.wads.IMPORT:
            self.view.import_wad(*data)
        elif action == self.models.categories.LOADED:
            self.view.appendCategory(data)
        elif action == self.models.categories.LOADED_ALL:
            self.view.finish_loading('categories')
        elif action == self.models.categories.NEW:
            self.view.category_added(*data)
        elif action == self.models.categories.REMOVE:
            self.view.category_removed(*data)

    def edit_category(self, id, **params):
        self.models.categories.update(id, **params)
        self.models.categories.save()
