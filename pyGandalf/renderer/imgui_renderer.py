from pyGandalf.renderer.base_renderer import BaseRenderer

from imgui_bundle import imgui
import OpenGL.GL as gl
import glfw

from enum import Enum
import ctypes

class ImGuiTheme(Enum):
    LIGHT = 0,
    DARK = 1

class ImGuiRenderer(BaseRenderer):    
    def initialize(cls, *kargs):
        cls.instance.window = kargs[0]
        cls.instance.theme = kargs[1]
        cls.instance.docking_enable = kargs[2]

        # Setup Dear ImGui context and flags
        imgui.create_context()
        io = imgui.get_io()
        io.config_flags |= imgui.ConfigFlags_.nav_enable_keyboard
        if cls.instance.docking_enable:
            io.config_flags |= imgui.ConfigFlags_.docking_enable

        # Setup Dear ImGui style
        match cls.instance.theme:
            case ImGuiTheme.LIGHT:
                imgui.style_colors_classic()
            case ImGuiTheme.DARK:
                imgui.style_colors_dark()

        # Setup Platform/Renderer backends
        window_address = ctypes.cast(cls.instance.window, ctypes.c_void_p).value
        imgui.backends.glfw_init_for_opengl(window_address, True)
        imgui.backends.opengl3_init('#version 330')

    def begin_frame(cls):
        imgui.backends.opengl3_new_frame()
        imgui.backends.glfw_new_frame()
        imgui.new_frame()
        
        if cls.instance.docking_enable:
            imgui.dock_space_over_viewport(imgui.get_main_viewport())
    
    def end_frame(cls):
        imgui.render()
        display_w, display_h = glfw.get_framebuffer_size(cls.instance.window)
        gl.glViewport(0, 0, display_w, display_h)
        imgui.backends.opengl3_render_draw_data(imgui.get_draw_data())
    
    def resize(cls, width, height):
        pass
    
    def clean(cls):
        imgui.backends.opengl3_shutdown()
        imgui.backends.glfw_shutdown()
        imgui.destroy_context()