import os

from core.utils.strings import snake_casify

def importer(main_dir, import_path, handler=lambda a: a):
    module_abspath = os.path.join(main_dir, import_path)
    module_names = [file.replace('.py', '') for file in os.listdir(module_abspath)
                        if not (file.startswith('__') and file.endswith(('__', '__.py')))]

    class __import_obj__:
        pass

    obj = __import_obj__()
    module_import_path = import_path.replace('/', '.')
    for module_name in module_names:
        module = __import__(module_import_path + '.' + module_name, fromlist=[module_name])
        obj.__setattr__(snake_casify(module_name), handler(module))

    return obj

def mvcimport(main_dir, root, models_path='app/models', controllers_path='app/controllers'):
    models = importer(main_dir, models_path)

    def controller_handler(controller):
        controller.show(root, models)

        return controller

    controllers = importer(main_dir, controllers_path, controller_handler)

    return (models, controllers)