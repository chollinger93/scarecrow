from plugin_base.base import BasePlugin
from utilities.utils import get_logger
logger = get_logger()

class PluginInterceptor:
    """Loads all allowed plugins, when they are a subclass of `BasePlugin` and have the constant `name` set (not `__name__`)
    """
    def __init__(self):
        self.cls = BasePlugin
        self.allowed_plugins = self.__load__allowed_plugins__()
        
    def __get_all_subclasses__(self, cls):
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in self.__get_all_subclasses__(c)]) 
    
    def __load__allowed_plugins__(self):
        __allowed_plugins__ = {}
        for cls in self.__get_all_subclasses__(self.cls):
            if cls.name:
                __allowed_plugins__[cls.name] = cls
        return __allowed_plugins__
    