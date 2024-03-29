from pyGandalf.scene.scene import Scene
from pyGandalf.scene.editor_components import *

from imgui_bundle import imgui

class EditorManager(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(EditorManager, cls).__new__(cls)
            cls.instance.editor_scene: Scene = Scene('EditorScene') # type: ignore
        return cls.instance
    
    def on_create(cls):
        viewport = cls.instance.editor_scene.enroll_entity()
        hierachy = cls.instance.editor_scene.enroll_entity()
        properties = cls.instance.editor_scene.enroll_entity()
        menu_bar = cls.instance.editor_scene.enroll_entity()
        content_browser = cls.instance.editor_scene.enroll_entity()
        systems = cls.instance.editor_scene.enroll_entity()

        cls.instance.editor_scene.add_component(viewport, EditorPanelComponent('Viewport', EditorPanelComponent.Type.VIEWPORT, None, [EditorPanelComponent.Style(imgui.StyleVar_.window_padding, imgui.ImVec2(0, 0), 0, False)]))
        cls.instance.editor_scene.add_component(hierachy, EditorPanelComponent('Hierachy', EditorPanelComponent.Type.HIERACHY, None))
        cls.instance.editor_scene.add_component(properties, EditorPanelComponent('Properties', EditorPanelComponent.Type.INSPECTOR, None))
        cls.instance.editor_scene.add_component(menu_bar, EditorPanelComponent('MenuBar', EditorPanelComponent.Type.MENU_BAR, None))
        cls.instance.editor_scene.add_component(content_browser, EditorPanelComponent('Content Browser', EditorPanelComponent.Type.CONTENT_BROWSER, None))
        cls.instance.editor_scene.add_component(systems, EditorPanelComponent('Systems', EditorPanelComponent.Type.SYSTEMS, None))

        cls.instance.editor_scene.get_component(viewport, EditorVisibleComponent).editor_visible = False
        cls.instance.editor_scene.get_component(hierachy, EditorVisibleComponent).editor_visible = False
        cls.instance.editor_scene.get_component(properties, EditorVisibleComponent).editor_visible = False
        cls.instance.editor_scene.get_component(menu_bar, EditorVisibleComponent).editor_visible = False
        cls.instance.editor_scene.get_component(content_browser, EditorVisibleComponent).editor_visible = False
        cls.instance.editor_scene.get_component(systems, EditorVisibleComponent).editor_visible = False
        
        from pyGandalf.systems.editor_panel_system import EditorPanelSystem

        cls.instance.editor_scene.register_system(EditorPanelSystem([EditorPanelComponent, EditorVisibleComponent]))

        cls.instance.editor_scene.on_create()

    def on_gui_update(cls, ts: float):
        cls.instance.editor_scene.on_gui_update(ts)

    def get_scene(cls):
        return cls.instance.editor_scene