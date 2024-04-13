class BaseRenderer(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(BaseRenderer, cls).__new__(cls)
        return cls.instance
    
    def initialize(cls, *kargs):
        raise NotImplementedError()

    def begin_frame(cls):
        raise NotImplementedError()
    
    def end_frame(cls):
        raise NotImplementedError()
    
    def resize(cls, width, height):
        raise NotImplementedError()
    
    def clean(cls):
        raise NotImplementedError()