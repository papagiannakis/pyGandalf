from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.editor_manager import EditorManager
from pyGandalf.renderer.base_renderer import BaseRenderer
from pyGandalf.renderer.opengl_renderer import OpenGLRenderer
from pyGandalf.renderer.webgpu_renderer import WebGPURenderer
from pyGandalf.renderer.imgui_renderer import ImGuiRenderer, ImGuiTheme
from pyGandalf.core.base_window import BaseWindow
from pyGandalf.core.input_manager import InputManager
from pyGandalf.core.event_manager import EventManager

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
            cls.instance.is_imgui_attached = False
            cls.instance.is_editor_attached = False
        return cls.instance
    
    def get_window(cls) -> BaseWindow:
        return cls.instance.window
    
    def get_renderer(cls) -> BaseRenderer:
        return cls.instance.renderer()
    
    def is_running(cls) -> bool:
        return cls.instance.is_application_running
    
    def set_is_running(cls, is_running):
        cls.instance.is_application_running = is_running

    def create(cls, window : BaseWindow, renderer : BaseRenderer, attach_imgui = False, attach_editor = False):
        cls.instance.window = window
        cls.instance.renderer = renderer
        cls.instance.is_imgui_attached = attach_imgui
        cls.instance.is_editor_attached = attach_editor
        cls.instance.window.create()
        InputManager().initialize(cls.instance.window.get_handle())
        EventManager().initialize(cls.instance.window.get_handle(), renderer=cls.instance.renderer)
        
        if type(renderer()) == OpenGLRenderer:
            renderer().initialize(attach_editor)
        elif type(renderer()) == WebGPURenderer:
            renderer().initialize(cls.instance.window, "high-performance")

        if cls.instance.is_imgui_attached:
            ImGuiRenderer().initialize(cls.instance.window.get_handle(), ImGuiTheme.DARK, attach_editor)

    def start(cls):
        SceneManager().on_create()

        if cls.instance.is_editor_attached:
            EditorManager().on_create()

        def main_loop():
            cls.instance.begin_frame()
            cls.instance.renderer().begin_frame()
            SceneManager().on_update(cls.instance.delta_time)
            cls.instance.renderer().end_frame()
            if cls.instance.is_imgui_attached:
                ImGuiRenderer().begin_frame()
                if cls.instance.is_editor_attached:
                    EditorManager().on_gui_update(cls.instance.delta_time)
                SceneManager().on_gui_update(cls.instance.delta_time)
                ImGuiRenderer().end_frame()
            cls.instance.end_frame()
            EventManager().process()

        cls.instance.window.dispatch_main_loop(main_loop)

        cls.instance.clean()

    def begin_frame(cls):
        time = glfw.get_time()
        cls.instance.delta_time = time - cls.instance.last_time
        cls.instance.last_time = time

    def end_frame(cls):
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
        if cls.instance.is_imgui_attached:
            ImGuiRenderer().clean()
        if (cls.instance.renderer is not None):
            cls.instance.renderer().clean()
        if (cls.instance.window is not None):
            cls.instance.window.destroy()
        SceneManager().clean()