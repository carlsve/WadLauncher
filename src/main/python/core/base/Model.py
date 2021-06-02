from dataclasses import asdict
from core.utils.strings import snake_casify

class Model:
    def __init__(self, schema, **io):
        self.schema = schema
        self.objects = {}
        self.subscriptions = {}
        self.subscriptions_index = -1
        self.loader = io.get('loader', lambda: [])
        self.saver = io.get('saver', lambda: None)

    def load(self):
        for obj in self.loader():
            self.create(**obj)

    def save(self, id):
        return self.saver(asdict(self.objects[id]))

    def all(self):
        return [obj for obj in self.objects.values()]

    def create(self, **kwargs):
        kwargs.pop('model_type', None)
        obj = self.schema(
            model_type=snake_casify(self.__class__.__name__),
            **kwargs
        )
        self.objects[obj.id] = obj

        return obj.id

    def find(self, id):
        return self.objects[id]

    def find_by(self, **kwargs):
        for obj_key in self.objects:
            obj_dict = asdict(self.objects[obj_key])
            found_object = all([kwargs[key] == obj_dict.get(key) for key in kwargs])

            if found_object:
                return self.objects[obj_key]

        return None

    def update(self, id, **kwargs):
        for key, val in kwargs.items():
            setattr(self.objects[id], key, val)

    def delete(self, id):
        return self.objects.pop(id)

    def subscribe(self, func):
        self.subscriptions_index += 1

        func_index = str(self.subscriptions_index)
        self.subscriptions[func_index] = func

        def unsubscribe():
            self.subscriptions.pop(func_index)

        return unsubscribe

    def broadcast(self, data):
        for func in self.subscriptions.values():
            func(data)