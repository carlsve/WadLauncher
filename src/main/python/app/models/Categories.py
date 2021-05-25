import sys, json, os, uuid

from configparser import ConfigParser

from core.base.Model import Model
from app.config import Config
from app.workers.CategoryLoaderWorker import category_loader_worker_wrapper
from app.workers.CategorySaverWorker import category_saver_worker_wrapper

class Categories(Model):
    LOADED = 'CATEGORIES_LOADED'
    LOADED_ALL = 'CATEGORIES_LOADED_ALL'
    NEW = 'CATEGORIES_NEW'
    REMOVE = 'CATEGORIES_REMOVE'

    def __init__(self):
        Model.__init__(self)
        category_loader_worker_wrapper([self.categories_loaded], [self.categories_loaded_all])

    def categories_loaded(self, obj):
        id = self.create(**obj)
        self.broadcast((self.LOADED, self.find(id)))

    def categories_loaded_all(self):
        self.broadcast((self.LOADED_ALL, None))

    def remove(self, id, parent_id):
        self.remove_child(parent_id, id)
        children = self.find(id)['children']
        for child in children:
            self.add_child(parent_id, child)
        self.delete(id)
        category_saver_worker_wrapper(self.all())
        self.broadcast((self.REMOVE, (parent_id, id)))
    
    def new(self, parent_id):
        id = self.create(name='new category', children=[])
        self.add_child(parent_id, id)
        self.broadcast((self.NEW, (parent_id, self.find(id))))
        category_saver_worker_wrapper(self.all())

    def add_child(self, id, child_id):
        children = self.find(id)['children']
        children.append(child_id)
        self.update(id, children=children)
    
    def remove_child(self, id, child_id):
        children = self.find(id)['children']
        children.remove(child_id)
        self.update(id, children=children)
    
    def insert_child(self, id, child_id, index):
        children = self.find(id)['children']
        children.insert(index, child_id)
        self.update(id, children=children)

    def save(self):
        category_saver_worker_wrapper(self.all())

sys.modules[__name__] = Categories()
