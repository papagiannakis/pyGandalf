from pyGandalf.scene.entity import Entity
from pyGandalf.systems.system import System, SystemState
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.editor_manager import EditorManager
from pyGandalf.scene.components import *
from pyGandalf.scene.editor_components import EditorPanelComponent, EditorVisibleComponent
from pyGandalf.renderer.opengl_renderer import OpenGLRenderer
from pyGandalf.utilities.definitions import ROOT_DIR

from imgui_bundle import imgui
import OpenGL.GL as gl

from pathlib import Path
import os

class EditorPanelSystem(System):
    """
    The system responsible for drawing the editor panels.
    """
    def __init__(self, filters: list[type]):
        super().__init__(filters)
        self.viewport_size = imgui.ImVec2(0, 0)
        self.viewport_panel_size = imgui.ImVec2(0, 0)
        self.current_directory: Path = ROOT_DIR / "resources"
        self.resources_directory = ROOT_DIR / "resources"
        self.entity_to_be_deleted: Entity = None
        self.wireframe_value = False

    def on_create(self, entity: Entity, components):
        """
        Gets called once in the first frame for every entity that the system operates on.
        """
        pass

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        pass

    def on_gui_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        editor_panel, editor_visible = components

        if editor_panel.enabled:
            if editor_panel.styles != None:
                for style in editor_panel.styles:
                    if style.use_float:
                        imgui.push_style_var(style.style_var, style.float_value)
                    else:
                        imgui.push_style_var(style.style_var, style.vector_value)

            if editor_panel.type != EditorPanelComponent.Type.MENU_BAR:
                imgui.begin(editor_panel.name)

            match editor_panel.type:
                case EditorPanelComponent.Type.VIEWPORT:
                    self.viewport_panel_size = imgui.get_content_region_avail()
                    if self.viewport_size.x != self.viewport_panel_size.x or self.viewport_size.y != self.viewport_panel_size.y:
                        OpenGLRenderer().invalidate_framebuffer(self.viewport_panel_size.x, self.viewport_panel_size.y)
                        self.viewport_size = imgui.ImVec2(self.viewport_panel_size.x, self.viewport_panel_size.y)
                    imgui.image(OpenGLRenderer().get_color_attachment(), imgui.ImVec2(self.viewport_size.x, self.viewport_size.y), imgui.ImVec2(0, 1), imgui.ImVec2(1, 0))
                
                case EditorPanelComponent.Type.HIERACHY:
                    entities = SceneManager().get_active_scene().get_entities()
                    for entt in entities:
                        editor_visible_entt: EditorVisibleComponent = SceneManager().get_active_scene().get_component(entt, EditorVisibleComponent)
                        if editor_visible_entt.editor_visible:
                            link_entt: LinkComponent = SceneManager().get_active_scene().get_component(entt, LinkComponent)
                            
                            if link_entt != None:
                                if link_entt.parent == None:
                                    self.draw_hierachy(entt, link_entt)

                    # Clear selection if clicked on empty space inside hierachy panel.            
                    if imgui.is_mouse_down(0) and imgui.is_window_hovered():
                        EditorVisibleComponent.SELECTED = False
                        EditorVisibleComponent.SELECTED_ENTITY = None

                case EditorPanelComponent.Type.INSPECTOR:
                    flags: imgui.TreeNodeFlags_ = imgui.TreeNodeFlags_.default_open | imgui.TreeNodeFlags_.allow_overlap
                    if EditorVisibleComponent.SELECTED_ENTITY != None:
                        if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, InfoComponent):
                            info: InfoComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, InfoComponent)
                            modified, text = imgui.input_text('Tag', info.tag)
                            if modified:
                                info.tag = text                            
                            imgui.separator()
                            
                        if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, TransformComponent):
                            if imgui.tree_node_ex('Transform', flags):
                                transform: TransformComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, TransformComponent)
                                moved, move_amount = imgui.drag_float3('Translation', transform.translation.to_list(), 0.25)
                                rotated, rotate_amount = imgui.drag_float3('Rotation', transform.rotation.to_list(), 0.25)
                                scaled, scale_amount = imgui.drag_float3('Scale', transform.scale.to_list(), 0.25)

                                if moved:
                                    transform.translation.x = move_amount[0]
                                    transform.translation.y = move_amount[1]
                                    transform.translation.z = move_amount[2]

                                if rotated:
                                    transform.rotation.x = rotate_amount[0]
                                    transform.rotation.y = rotate_amount[1]
                                    transform.rotation.z = rotate_amount[2]

                                if scaled:
                                    transform.scale.x = scale_amount[0]
                                    transform.scale.y = scale_amount[1]
                                    transform.scale.z = scale_amount[2]

                                imgui.tree_pop()
                            imgui.separator()

                        if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, CameraComponent):
                            if imgui.tree_node_ex('Camera', flags):
                                camera: CameraComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, CameraComponent)

                                fov_changed, new_fov = imgui.drag_float('fov', camera.fov)
                                near_changed, new_near = imgui.drag_float('near', camera.near, 0.05)
                                far_changed, new_far = imgui.drag_float('far', camera.far)
                                aspect_ratio_changed, new_aspect_ratio = imgui.drag_float('aspect_ratio', camera.aspect_ratio, 0.1)
                                primary_changed, new_primary = imgui.checkbox('primary', camera.primary)
                                static_changed, new_static = imgui.checkbox('static', camera.static)

                                selected_projection = 'Orthographic' if camera.type == CameraComponent.Type.ORTHOGRAPHIC else 'Perspective'
                                projections = ['Perspective', 'Orthographic']
                                
                                if imgui.begin_combo('Projection', selected_projection):
                                    for projection in projections:
                                        is_selected = (selected_projection == projection)
                                        modified, new_value = imgui.selectable(projection, is_selected)
                                        if modified:
                                            if new_value:
                                                selected_projection = projection
                                        if is_selected:
                                            imgui.set_item_default_focus()
                                    imgui.end_combo()

                                if fov_changed: camera.fov = new_fov
                                if near_changed: camera.near = new_near
                                if far_changed: camera.far = new_far
                                if aspect_ratio_changed: camera.aspect_ratio = new_aspect_ratio
                                if primary_changed: camera.primary = new_primary
                                if static_changed: camera.static = new_static

                                camera.type = CameraComponent.Type.ORTHOGRAPHIC if selected_projection == 'Orthographic' else CameraComponent.Type.PERSPECTIVE
                                
                                imgui.tree_pop()
                            imgui.separator()

                        if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, LightComponent):
                            if imgui.tree_node_ex('Light', flags):
                                light: LightComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, LightComponent)

                                color_changed, new_color = imgui.color_edit3('color', light.color)
                                intensity_changed, new_intensity = imgui.drag_float('intensity', light.intensity, 0.1)
                                static_changed, new_static = imgui.checkbox('static', light.static)

                                if color_changed: light.color = glm.vec3(new_color[0], new_color[1], new_color[2])
                                if intensity_changed: light.intensity = new_intensity
                                if static_changed: light.static = new_static
                                
                                imgui.tree_pop()
                            imgui.separator()

                        if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, StaticMeshComponent):
                            if imgui.tree_node_ex('StaticMeshComponent', flags):
                                static_mesh: StaticMeshComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, StaticMeshComponent)

                                imgui.label_text('name', static_mesh.name)
                                
                                imgui.tree_pop()
                            imgui.separator()
                        
                        if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, LinkComponent):
                            if imgui.tree_node_ex('LinkComponent', flags):
                                link: LinkComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, LinkComponent)

                                parent = 'None'

                                if link.parent != None:
                                    info: InfoComponent = SceneManager().get_active_scene().get_component(link.parent, InfoComponent)
                                    if info != None:
                                        parent = info.tag

                                imgui.label_text('parent', parent)
                                
                                imgui.tree_pop()
                            imgui.separator()
                        
                        if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, MaterialComponent):
                            if imgui.tree_node_ex('MaterialComponent', flags):
                                material: MaterialComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, MaterialComponent)

                                if material.instance.has_uniform('u_Color'):
                                    color_changed, new_color = imgui.color_edit3('color', material.color)
                                    if color_changed: material.color = glm.vec3(new_color[0], new_color[1], new_color[2])
                                
                                if material.instance.has_uniform('u_Glossiness'):
                                    glossiness_changed, new_glossiness = imgui.drag_float('glossiness', material.glossiness, 0.1)
                                    if glossiness_changed: material.glossiness = new_glossiness
                                
                                imgui.tree_pop()
                            imgui.separator()

                case EditorPanelComponent.Type.MENU_BAR:
                    if imgui.begin_main_menu_bar():
                        if imgui.begin_menu('File'):
                            pressed, _ = imgui.menu_item('Close', '', False)
                            if pressed:
                                from pyGandalf.core.application import Application
                                Application().quit()
                            imgui.end_menu()
                        if imgui.begin_menu('View'):
                            editor_panel_system: EditorPanelSystem = EditorManager().get_scene().get_system(EditorPanelSystem)
                            if editor_panel_system != None:
                                for panel, _ in editor_panel_system.filtered_components:
                                    modified, show = imgui.checkbox(panel.name, panel.enabled)
                                    if modified:
                                        panel.enabled = show
                            imgui.end_menu()
                        if imgui.begin_menu('Settings'):
                            modified, show = imgui.checkbox('Wireframe', self.wireframe_value)
                            if modified:
                                if show:
                                    OpenGLRenderer().set_fill_mode(gl.GL_LINE)
                                else:
                                    OpenGLRenderer().set_fill_mode(gl.GL_FILL)
                                self.wireframe_value = show
                            imgui.end_menu()
                        imgui.end_main_menu_bar()

                case EditorPanelComponent.Type.CONTENT_BROWSER:
                    padding = 16.0
                    thumbnail_size = 128.0
                    panel_width = imgui.get_content_region_avail().x

                    column_count = int(panel_width / (padding + thumbnail_size))

                    if imgui.begin_table('Content', column_count):
                        if self.current_directory != self.resources_directory:
                            imgui.table_next_column()
                            # imgui.push_style_color(imgui.Col_.button, imgui.ImVec4(0, 0, 0, 0))
                            imgui.button('Back', imgui.ImVec2(thumbnail_size, thumbnail_size))
                            # imgui.image_button(f'Back{id}', tex_id, imgui.ImVec2(thumbnail_size, thumbnail_size), imgui.ImVec2(0, 1), imgui.ImVec2(1, 0))
                            if imgui.is_item_hovered() and imgui.is_mouse_double_clicked(0):
                                self.current_directory = self.current_directory.parent
                            # imgui.pop_style_color()
                            # imgui.text_wrapped('Back')

                        id = 0
                        # Loop through directory items
                        for entry in os.listdir(self.current_directory):
                            imgui.table_next_column()
                            imgui.push_id(id)
                            # Display directory item
                            # imgui.push_style_color(imgui.Col_.button, imgui.ImVec4(0, 0, 0, 0))
                            imgui.button(entry, imgui.ImVec2(thumbnail_size, thumbnail_size))
                            # imgui.image_button(f'{entry}{id}', tex_id, imgui.ImVec2(thumbnail_size, thumbnail_size), imgui.ImVec2(0, 1), imgui.ImVec2(1, 0))
                            # imgui.pop_style_color()
                            if imgui.is_item_hovered() and imgui.is_mouse_double_clicked(0):
                                new_path = self.current_directory / entry
                                if os.path.isdir(new_path):
                                    self.current_directory = new_path
                            # imgui.text_wrapped(entry)
                            imgui.pop_id()
                            id += 1
                        imgui.end_table()

                case EditorPanelComponent.Type.SYSTEMS:
                    for system in SceneManager().get_active_scene().get_systems():
                        imgui.text(str(type(system)))
                        imgui.same_line()
                        if system.state == SystemState.PAUSE:
                            imgui.button('Resume')
                            if imgui.is_item_clicked():
                                system.set_state(SystemState.PLAY)
                        elif system.state == SystemState.PLAY:
                            imgui.button('Pause')
                            if imgui.is_item_clicked():
                                system.set_state(SystemState.PAUSE)

            if editor_panel.type != EditorPanelComponent.Type.MENU_BAR:
                imgui.end()

            if editor_panel.styles != None:
                for style in editor_panel.styles:
                    imgui.pop_style_var()
            
            if self.entity_to_be_deleted != None:
                if self.entity_to_be_deleted == SceneManager().get_main_camera_entity():
                    SceneManager().set_main_camera(None, None)
                SceneManager().get_active_scene().destroy_entity(self.entity_to_be_deleted)
                self.entity_to_be_deleted = None
                EditorVisibleComponent.SELECTED = False
                EditorVisibleComponent.SELECTED_ENTITY = None
    
    def draw_hierachy(self, entt, link):
        info_entt: InfoComponent = SceneManager().get_active_scene().get_component(entt, InfoComponent)
        if info_entt == None:
            return
        
        flags: imgui.TreeNodeFlags_ = (imgui.TreeNodeFlags_.selected if EditorVisibleComponent.SELECTED and EditorVisibleComponent.SELECTED_ENTITY == entt else 0) | (imgui.TreeNodeFlags_.open_on_arrow if link != None and len(link.children) != 0 else imgui.TreeNodeFlags_.bullet)
        opened = imgui.tree_node_ex(info_entt.tag, flags)

        if imgui.is_item_clicked():
            EditorVisibleComponent.SELECTED = True
            EditorVisibleComponent.SELECTED_ENTITY = entt

        if imgui.begin_popup_context_item():
            if imgui.menu_item_simple('Destroy'):
                self.entity_to_be_deleted = entt
            imgui.end_popup()
        
        if opened:
            for child in link.children:
                child_link: LinkComponent = SceneManager().get_active_scene().get_component(child, LinkComponent)
                self.draw_hierachy(child, child_link)
            imgui.tree_pop()