import sys

from core.base.Model import Model, singularize, singularizable

from app.workers.CategoryLoaderWorker import category_loader_worker_wrapper
from app.workers.CategorySaverWorker import category_saver_worker_wrapper
from app.schemas.Category import Category

@singularizable
class Categories(Model):
    LOADED = 'CATEGORIES_LOADED'
    LOADED_ALL = 'CATEGORIES_LOADED_ALL'
    NEW = 'CATEGORIES_NEW'
    REMOVE = 'CATEGORIES_REMOVE'

    def __init__(self):
        Model.__init__(self, schema=Category)
        category_loader_worker_wrapper([self.loaded], [self.loaded_all])

    def loaded(self, obj):
        id = self.create(**obj)
        self.broadcast((self.LOADED, self.find(id)))

    def loaded_all(self):
        self.broadcast((self.LOADED_ALL, None))

    def remove(self, id, parent_id):
        row = self.find(parent_id).children.index(id)
        self.remove_child(parent_id, id)
        children = self.find(id).children
        for child in reversed(children):
            self.insert_child(parent_id, child, row)
        self.delete(id)
        category_saver_worker_wrapper(self.all())
        self.broadcast((self.REMOVE, (parent_id, id)))
    
    def new(self, parent_id, name='new category'):
        id = self.create(name=name)
        self.add_child(parent_id, id)
        self.broadcast((self.NEW, (parent_id, self.find(id))))
        category_saver_worker_wrapper(self.all())

    @singularize
    def add_child(self, id, child_id):
        children = self.find(id).children
        children.append(child_id)
        self.update(id, children=children)
    
    @singularize
    def remove_child(self, id, child_id):
        children = self.find(id).children
        children.remove(child_id)
        self.update(id, children=children)

    @singularize
    def insert_child(self, id, child_id, index):
        children = self.find(id).children
        children.insert(index, child_id)
        self.update(id, children=children)

    def save(self):
        category_saver_worker_wrapper(self.all())

