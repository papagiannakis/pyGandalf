from scene.scene_manager import SceneManager
from renderer.base_renderer import BaseRenderer
from core.base_window import BaseWindow

import glfw

class Application(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Application, cls).__new__(cls)
            cls.instance.renderer = None
            cls.instance.window = None
            cls.instance.is_application_running = False
            cls.instance.delta_time = 0.0
            cls.instance.last_time = 0.0
            cls.instance.timer = 0.0
            cls.instance.frames = 0.0
        return cls.instance
    
    def get_window(cls):
        return cls.instance.window
    
    def is_running(cls):
        return cls.instance.is_application_running
    
    def set_is_running(cls, is_running):
        cls.instance.is_application_running = is_running

    def create(cls, window : BaseWindow, renderer : BaseRenderer):
        cls.instance.window = window
        cls.instance.renderer = renderer
        cls.instance.window.create()
        renderer().initialize()

    def start(cls):
        SceneManager().on_create()

        def main_loop():
            cls.instance.begin_frame()
            cls.instance.renderer().begin_frame()
            SceneManager().on_update(cls.instance.delta_time)
            cls.instance.renderer().end_frame()
            cls.instance.end_frame()

        cls.instance.window.dispatch_main_loop(main_loop)

        cls.instance.clean()

    def begin_frame(cls):
        time = glfw.get_time()
        cls.instance.delta_time = time - cls.instance.last_time
        cls.instance.last_time = time

    def end_frame(cls):
        # Calculate fps
        cls.instance.frames += 1
        if glfw.get_time() - cls.instance.timer > 1.0:
            title = cls.instance.window.get_title() + f' [FPS: {cls.instance.frames}]'
            glfw.set_window_title(cls.instance.window.get_handle(), title)
            cls.instance.timer += 1
            cls.instance.frames = 0

    def quit(cls):
        cls.instance.is_application_running = False
        cls.instance.window.close()

    def clean(cls):
        if (cls.instance.window is not None):
            cls.instance.window.destroy()
        if (cls.instance.renderer is not None):
            cls.instance.renderer().clean()
        SceneManager().clean()