from pyGandalf.scene.components import *

class ComponentLib(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ComponentLib, cls).__new__(cls)
            cls.instance.decorators: dict[type, type] = {} # type: ignore
        return cls.instance
    
    def register(cls, component: type):
        cls.instance.decorators[component] = component
    
    def decorate(cls, component: type, decorator: type):
        cls.instance.decorators[component] = decorator

    @property
    def Transform(cls):
        return cls.instance.decorators[TransformComponent]

    @property
    def Decorators(cls):
        return cls.instance.decorators
    
ComponentLib().register(TransformComponent)