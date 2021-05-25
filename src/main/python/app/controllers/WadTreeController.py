import sys

from app.views.WadTreeView import WadTreeView

class WadTreeController:
    def show(self, root, models):
        self.models = models
        self.view = WadTreeView(root, self)
        
        self.models.wads.subscribe(self.subscription)
        self.models.categories.subscribe(self.subscription)
    
    def subscription(self, msg):
        action, data = msg

        if action == self.models.wads.WADS_LOADED:
            self.view.appendWad(data)
        elif action == self.models.wads.WADS_LOADED_ALL:
            self.view.finish_loading('wads')
        elif action == self.models.wads.WADS_REMOVE:
            self.view.wad_removed(data)
        elif action == self.models.wads.WADS_CREATED:
            self.view.new_wad(self.models.wads.find(data))
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


sys.modules[__name__] = WadTreeController()