import os
from core.utils.strings import snake_casify

def import_classes(package_name, class_names):
    package = __import__(package_name, fromlist=class_names)
    return [getattr(getattr(package, class_name), class_name) for class_name in class_names]

def get_file_names(main_dir, path):
    abspath = os.path.join(main_dir, path)
    return [file.replace('.py', '') for file in os.listdir(abspath)
                if not (file.startswith('__') and file.endswith(('__', '__.py')))]

class __classes_obj__:
    pass

def mvcimport(main_dir, root):
    model_names = get_file_names(main_dir, 'app/models')
    controller_names = get_file_names(main_dir, 'app/controllers')

    model_classes = import_classes('app.models', model_names)
    controller_classes = import_classes('app.controllers', controller_names)

    model_obj = __classes_obj__()
    for model, model_name in zip(model_classes, model_names):
        model_obj.__setattr__(snake_casify(model_name), model())

    controller_obj = __classes_obj__()
    for controller, controller_name in zip(controller_classes, controller_names):
        _c = controller(root, model_obj)
        controller_obj.__setattr__(snake_casify(controller_name), _c)

    return (model_obj, controller_obj)
