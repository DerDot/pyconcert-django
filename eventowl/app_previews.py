from eventowlproject.settings import APPS_WITH_PREVIEW

from importlib import import_module
from abc import ABCMeta, abstractmethod
abstractstaticmethod = abstractmethod


PREVIEW_MODULE_NAME = 'preview'
PREVIEW_CLASS_NAME = 'Preview'


class AbstractPreview(object, metaclass=ABCMeta):
    @abstractstaticmethod
    def description():
        pass
    
    @abstractstaticmethod
    def get_objects(options):
        pass
    
    
def get_all_objects(options):
    all_objects = {}
    
    for app_name in APPS_WITH_PREVIEW:
        class_obj = _class_from_app_name(app_name)
        objs = class_obj.get_objects(options)
        description = class_obj.description()
        all_objects[app_name] = (description, objs)
        
    return all_objects


def _class_from_app_name(app_name):
    module_name = '{}.{}'.format(app_name, PREVIEW_MODULE_NAME)
    module = import_module(module_name)
    class_obj = getattr(module, PREVIEW_CLASS_NAME)
    return class_obj