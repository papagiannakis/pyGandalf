from scene.scene import Scene
from utilities.logger import logger

class SceneManager(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SceneManager, cls).__new__(cls)
            cls.instance.scenes = []
            cls.instance.active_scene = None
            cls.instance.new_scene_to_loaded = None
            cls.instance.active_scene_index = 0
            cls.instance.scene_change_requested = False
        return cls.instance
    
    def add_scene(cls, scene: Scene):
        if scene is None:
            logger.error('Scene is null, not appending it.')
            return
        
        cls.instance.scenes.append(scene)

        if len(cls.instance.scenes) == 1:
            cls.instance.active_scene = cls.instance.scenes[0]

    def on_create(cls):
        if len(cls.instance.scenes) == 0:
            logger.critical('No scenes added, exiting...')
            exit(-1)

        cls.instance.active_scene_index = 0
        cls.instance.active_scene = cls.instance.scenes[cls.instance.active_scene_index]
        cls.instance.active_scene.on_create()

    def on_update(cls, ts):
        if cls.instance.active_scene is None:
            logger.critical('There is no active scene currenlty')
            return
        
        cls.instance.active_scene.on_update(ts)

        if cls.instance.scene_change_requested:
            cls.instance.change_scene_deffered()

    def change_scene(cls, scene: Scene = None):
        if scene is None:
            cls.instance.active_scene_index += 1
        else:
            cls.instance.new_scene_to_loaded = scene

        cls.instance.scene_change_requested = True

    def change_scene_deffered(cls):
        if cls.instance.new_scene_to_loaded is None:
            if len(cls.instance.scenes) <= cls.instance.active_scene_index:
                logger.error(f'Out of bounds scene index: {cls.instance.active_scene_index} for scene change')
                cls.instance.scene_change_requested = False
                return
            
            cls.instance.active_scene = cls.instance.scenes[cls.instance.active_scene_index]
        else:
            cls.instance.active_scene = cls.instance.new_scene_to_loaded

        cls.instance.active_scene.on_create()
        cls.instance.new_scene_to_loaded = None
        cls.instance.scene_change_requested = False

    def get_active_scene(cls):
        return cls.instance.active_scene