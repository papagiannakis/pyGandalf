from pyGandalf.scene.components import Component
from pyGandalf.scene.entity import Entity
from pyGandalf.core.input_manager import InputManager
from pyGandalf.systems.system import System, SystemState
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.scene_serializer import SceneSerializer
from pyGandalf.scene.editor_manager import EditorManager
from pyGandalf.scene.components import *
from pyGandalf.scene.editor_components import EditorPanelComponent, EditorVisibleComponent
from pyGandalf.renderer.opengl_renderer import OpenGLRenderer
from pyGandalf.utilities.definitions import ROOT_DIR, SCENES_PATH, MODELS_PATH, TEXTURES_PATH
from pyGandalf.utilities.entity_presets import *
from pyGandalf.utilities.mesh_lib import MeshLib
from pyGandalf.utilities.component_lib import ComponentLib
from pyGandalf.utilities.opengl_texture_lib import TextureData, TextureDescriptor

from pyGandalf.utilities.logger import logger
from PIL import Image

from imgui_bundle import imgui, imguizmo
import OpenGL.GL as gl
import numpy as np
import glfw

from pathlib import Path
import glob
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
        self.vsync_value = False
        self.gizmo_operation: imguizmo.im_guizmo.OPERATION = imguizmo.im_guizmo.OPERATION.translate
        self.camera_pivot_distance = 10.0
        self.drag_and_drop_mesh = None
        self.drag_and_drop_scene = None
        self.drag_and_drop_texture = None
        self.gizmos_pressed = False
        self.camera_controller_pressed = False

    def on_create_entity(self, entity: Entity, components: Component | tuple[Component]):
        pass

    def on_gui_update_entity(self, ts, entity: Entity, components: Component | tuple[Component]):
        editor_panel = components

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
                    self.draw_viewport_panel()
                
                case EditorPanelComponent.Type.HIERACHY:
                    self.draw_hierachy_panel()

                case EditorPanelComponent.Type.INSPECTOR:
                    self.draw_inspector_panel()

                case EditorPanelComponent.Type.MENU_BAR:
                    self.draw_menu_bar()

                case EditorPanelComponent.Type.CONTENT_BROWSER:
                    self.draw_content_browser()

                case EditorPanelComponent.Type.SYSTEMS:
                    self.draw_systems_panel()

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
        opened = imgui.tree_node_ex(f'{info_entt.tag}##{entt.id}', flags)

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
    
    def draw_viewport_panel(self):
        camera: CameraComponent = SceneManager().get_main_camera()
        camera_entity: CameraComponent = SceneManager().get_main_camera_entity()

        # Viewport
        self.viewport_panel_size = imgui.get_content_region_avail()
        if self.viewport_size.x != self.viewport_panel_size.x or self.viewport_size.y != self.viewport_panel_size.y:
            OpenGLRenderer().invalidate_framebuffer(self.viewport_panel_size.x, self.viewport_panel_size.y)
            self.viewport_size = imgui.ImVec2(self.viewport_panel_size.x, self.viewport_panel_size.y)
            camera.aspect_ratio = self.viewport_panel_size.x / self.viewport_panel_size.y
        else:
            imgui.image(OpenGLRenderer().get_color_attachment(), imgui.ImVec2(self.viewport_size.x, self.viewport_size.y), imgui.ImVec2(0, 1), imgui.ImVec2(1, 0))

        if imgui.begin_drag_drop_target():
            payload: imgui.Payload_PyId = imgui.accept_drag_drop_payload_py_id('scenes')
            if payload != None:
                EditorVisibleComponent.SELECTED = False
                EditorVisibleComponent.SELECTED_ENTITY = None

                OpenGLShaderLib().clean()

                path: Path = Path(self.drag_and_drop_scene)
                scene: Scene = Scene(path.stem)
                scene_serializer: SceneSerializer = SceneSerializer(scene)
                scene_serializer.deserialize(path)
                SceneManager().open_external_scene(scene)

        # Gizmos
        if camera != None and camera_entity != None:
            context = SceneManager().get_active_scene()
            selected_entity: Entity = EditorVisibleComponent.SELECTED_ENTITY

            if not imguizmo.im_guizmo.is_using():
                if InputManager().get_key_press(glfw.KEY_T):
                    self.gizmo_operation = imguizmo.im_guizmo.OPERATION.translate
                elif InputManager().get_key_press(glfw.KEY_R):
                    self.gizmo_operation = imguizmo.im_guizmo.OPERATION.rotate
                elif InputManager().get_key_press(glfw.KEY_S):
                    self.gizmo_operation = imguizmo.im_guizmo.OPERATION.scale
                elif InputManager().get_key_press(glfw.KEY_Q):
                    self.gizmo_operation = None

            if camera.type == CameraComponent.Type.ORTHOGRAPHIC:
                imguizmo.im_guizmo.set_orthographic(True)
            else:
                imguizmo.im_guizmo.set_orthographic(False)

            # Set window for rendering into.
            imguizmo.im_guizmo.set_drawlist()

            # Set viewport size.
            imguizmo.im_guizmo.set_rect(imgui.get_window_pos().x, imgui.get_window_pos().y, imgui.get_window_width(), imgui.get_window_height())

            # Transformations gizmo.
            if selected_entity != None and self.gizmo_operation != None:
                snap = InputManager().get_key_down(glfw.KEY_LEFT_CONTROL)
                snap_value = 45.0 if self.gizmo_operation == imguizmo.im_guizmo.OPERATION.rotate else 0.5
                snap_values: imguizmo.Matrix3 = np.array([snap_value, snap_value, snap_value], dtype=np.float32)

                transform = context.get_component(selected_entity, ComponentLib().Transform)
                new_matrix: imguizmo.Editable_Matrix16 = imguizmo.im_guizmo.manipulate(
                    np.asmatrix(camera.view, dtype=np.float32),
                    np.asmatrix(camera.projection, dtype=np.float32),
                    self.gizmo_operation,
                    imguizmo.im_guizmo.MODE.local,
                    np.asmatrix(transform.local_matrix, dtype=np.float32),
                    None,
                    None if snap == False else snap_values)
                
                if new_matrix.edited:
                    if imguizmo.im_guizmo.is_using():
                        matrix_components: imguizmo.im_guizmo.MatrixComponents = imguizmo.im_guizmo.decompose_matrix_to_components(new_matrix.value)
                        transform.translation = glm.vec3(matrix_components.translation[0], matrix_components.translation[1], matrix_components.translation[2])
                        transform.rotation += glm.vec3(matrix_components.rotation[0] - transform.rotation.x, matrix_components.rotation[1] - transform.rotation.y, matrix_components.rotation[2] - transform.rotation.z)
                        transform.scale = glm.vec3(matrix_components.scale[0], matrix_components.scale[1], matrix_components.scale[2])

            # Camera gizmo.
            view_manipulate_right = imgui.get_window_pos().x + imgui.get_window_width()
            view_manipulate_top = imgui.get_window_pos().y

            camera_transform: ComponentLib().Transform = context.get_component(camera_entity, ComponentLib().Transform)
            new_view: imguizmo.Editable_Matrix16 = imguizmo.im_guizmo.view_manipulate(
                np.asmatrix(camera.view, dtype=np.float32),
                self.camera_pivot_distance,
                imgui.ImVec2(view_manipulate_right - 128, view_manipulate_top),
                imgui.ImVec2(128, 128),
                0x10101010,
            )

            if new_view.edited:
                view_matrix_components: imguizmo.im_guizmo.MatrixComponents = imguizmo.im_guizmo.decompose_matrix_to_components(np.linalg.inv(new_view.value))
                camera_transform.translation = glm.vec3(view_matrix_components.translation[0], view_matrix_components.translation[1], view_matrix_components.translation[2])
                camera_transform.rotation += glm.vec3(view_matrix_components.rotation[0] - camera_transform.rotation.x, view_matrix_components.rotation[1] - camera_transform.rotation.y, view_matrix_components.rotation[2] - camera_transform.rotation.z)
                camera_transform.scale = glm.vec3(view_matrix_components.scale[0], view_matrix_components.scale[1], view_matrix_components.scale[2])

    def draw_hierachy_panel(self):
        modified, text = imgui.input_text('Scene', SceneManager().get_active_scene().name)
        if modified:
            SceneManager().get_active_scene().name = text

        if imgui.begin_popup_context_window('Right click options', imgui.PopupFlags_.no_open_over_items | imgui.PopupFlags_.mouse_button_right):
            modified_empty, _ = imgui.menu_item('Create Empty', '', False)

            entity: Entity = None

            if modified_empty:
                entity = create_empty()

            modified_cube, _ = imgui.menu_item('Create Cube', '', False)
            if modified_cube:
                entity = create_cube()

            modified_sphere, _ = imgui.menu_item('Create Sphere', '', False)
            if modified_sphere:
                entity = create_sphere()

            modified_plane, _ = imgui.menu_item('Create Plane', '', False)
            if modified_plane:
                entity = create_plane()

            modified_camera, _ = imgui.menu_item('Create Camera', '', False)
            if modified_camera:
                entity = create_camera()
            
            modified_light, _ = imgui.menu_item('Create Light', '', False)
            if modified_light:
                entity = create_light()

            if entity != None:
                EditorVisibleComponent.SELECTED = True
                EditorVisibleComponent.SELECTED_ENTITY = entity

            imgui.end_popup()
        
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

    def draw_inspector_panel(self):
        flags: imgui.TreeNodeFlags_ = imgui.TreeNodeFlags_.default_open | imgui.TreeNodeFlags_.allow_overlap
        if EditorVisibleComponent.SELECTED_ENTITY != None:
            if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, InfoComponent):
                info: InfoComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, InfoComponent)
                modified, text = imgui.input_text('Tag', info.tag)
                if modified:
                    info.tag = text                            
                imgui.separator()
            if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, ComponentLib().Transform):
                if imgui.tree_node_ex('Transform', flags):
                    transform: ComponentLib().Transform = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, ComponentLib().Transform)
                    moved, move_amount = imgui.drag_float3('Translation', transform.translation.to_list(), 0.25)
                    rotated, rotate_amount = imgui.drag_float3('Rotation', transform.rotation.to_list(), 0.25)
                    scaled, scale_amount = imgui.drag_float3('Scale', transform.scale.to_list(), 0.25)
                    static_changed, new_static = imgui.checkbox('static', transform.static)
                    if static_changed: transform.static = new_static

                    if moved:
                        transform.translation = glm.vec3(move_amount[0], move_amount[1], move_amount[2])

                    if rotated:
                        transform.rotation = glm.vec3(rotate_amount[0], rotate_amount[1], rotate_amount[2])

                    if scaled:
                        transform.scale = glm.vec3(scale_amount[0], scale_amount[1], scale_amount[2])

                    if static_changed:
                        transform.static = new_static

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

                    camera.type = CameraComponent.Type.ORTHOGRAPHIC if selected_projection == 'Orthographic' else CameraComponent.Type.PERSPECTIVE
                    
                    imgui.tree_pop()
                imgui.separator()

            if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, LightComponent):
                if imgui.tree_node_ex('Light', flags):
                    light: LightComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, LightComponent)

                    color_changed, new_color = imgui.color_edit3('color', light.color)
                    intensity_changed, new_intensity = imgui.drag_float('intensity', light.intensity, 0.1)

                    if color_changed: light.color = glm.vec3(new_color[0], new_color[1], new_color[2])
                    if intensity_changed: light.intensity = new_intensity
                    
                    imgui.tree_pop()
                imgui.separator()

            if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, TerrainComponent):
                if imgui.tree_node_ex('TerrainComponent', flags):
                    terrain: TerrainComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, TerrainComponent)
                    cameraTransform: TransformComponent = SceneManager().get_active_scene().get_component(terrain.camera, TransformComponent)
                    material: MaterialComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, MaterialComponent)
                    erosion: ErosionComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, ErosionComponent)
                    if (terrain.cameraCoords != cameraTransform.translation.xz) and not terrain.erode:
                        terrain.cameraCoords = cameraTransform.translation.xz
                        terrain.cameraMoved = True
                    scaleChanged, newScale = imgui.input_int('Scale', terrain.scale, 1)
                    elevationScaleChanged, newElevationScale = imgui.input_int('Elevation Scale', terrain.elevationScale, 1)
                    terrainChanged, newMapSize = imgui.drag_int('Map size', terrain.mapSize, 8, 8, 512)
                    imgui.button('Generate', imgui.ImVec2(60, 15))
                    if imgui.is_item_clicked():
                        terrain.generate = True
                        terrain.run = True
                        terrain.erode = False
                        erosion.enabled = False
                        terrain.loaded = 0
                    load_pressed = imgui.begin_menu('Load')
                    if load_pressed:
                        for file in glob.glob(str(TEXTURES_PATH/ "**")):
                            path: Path = Path(file)
                            file_pressed, _ = imgui.menu_item(path.name, '', False)
                            if file_pressed:
                                terrain.run = True
                                terrain.generate = True
                                img = Image.open(path.absolute())
                                width, height = img.size
                                terrain.offsetX = width / terrain.mapSize
                                terrain.offsetY = height / terrain.mapSize
                                terrain.loaded = 1
                                terrain.erode = True
                                computeTextureDescriptor = TextureDescriptor(internal_format=gl.GL_RGBA32F, wrap_s=gl.GL_CLAMP_TO_EDGE, wrap_t=gl.GL_CLAMP_TO_EDGE)
                                OpenGLTextureLib().update('loadedHeightmap', TextureData(path.absolute()), computeTextureDescriptor)
                        imgui.end_menu()
                    frequencyChnaged, newFrequency = imgui.drag_float('Frequency', terrain.frequency, 0.01, 0.0, 1000.0)
                    if frequencyChnaged: terrain.frequency = newFrequency
                    lacunarityChanged, newLacunarity = imgui.drag_float('Lacunarity', terrain.lacunarity, 0.01, 0.0, 1000.0)
                    if lacunarityChanged: terrain.lacunarity = newLacunarity
                    persistenceChanged, newPersistence = imgui.drag_float('Persistence', terrain.persistence, 0.01, 0.0, 1000.0)
                    if persistenceChanged: terrain.persistence = newPersistence
                    octavesChanged, newOctaves = imgui.input_int('Octaves', terrain.octaves, 1)
                    if octavesChanged: terrain.octaves = newOctaves
                    turbulanceChanged, newTurbulance = imgui.checkbox('Turbulance', terrain.turbulance)
                    if turbulanceChanged: terrain.turbulance = newTurbulance
                    ridgesChanged, newRidges = imgui.checkbox('Ridges', terrain.Ridges)
                    if ridgesChanged: terrain.Ridges = newRidges
                    ridgesStrengthChanged, newRidgesStrength = imgui.slider_int('Ridges Strength', terrain.ridgesStrength, 0, 5)
                    if ridgesStrengthChanged: terrain.ridgesStrength = newRidgesStrength
                    seedChanged, newSeed = imgui.drag_int('Seed', terrain.seed, 1)
                    if seedChanged: terrain.seed = newSeed
                    fallOffEnabledChanged, newFallOffEnabled = imgui.checkbox('Fall Off Enabled', terrain.fallOffEnabled)
                    if fallOffEnabledChanged: terrain.fallOffEnabled = newFallOffEnabled
                    fallOffTypeChanged, newFallOffType = imgui.combo('Fall Off Type', terrain.fallOffType, ['Circle', 'Rectangle'])
                    if fallOffTypeChanged: terrain.fallOffType = newFallOffType
                    fallOffHeightChanged, newFallOffHeight = imgui.drag_float('Fall Off Height', terrain.fallOffHeight, 0.01)
                    if fallOffHeightChanged: terrain.fallOffHeight = newFallOffHeight
                    aChanged, newA = imgui.drag_float('A', terrain.a, 0.01)
                    if aChanged: terrain.a = newA
                    bChanged, newB = imgui.drag_float('B', terrain.b, 0.01)
                    if bChanged: terrain.b = newB
                    underWaterRavinesChanged, newUnderWaterRavines = imgui.checkbox('Under Water Ravines', terrain.underWaterRavines)
                    if underWaterRavinesChanged: terrain.underWaterRavines = newUnderWaterRavines
                    clampHeightChanged, newClampHeight = imgui.checkbox('Clamp Height', terrain.clampHeight)
                    if clampHeightChanged: terrain.clampHeight = newClampHeight
                    minHeightChanged, newMinHeight = imgui.drag_float('Min Height', terrain.minHeight, 0.01)
                    if minHeightChanged: terrain.minHeight = newMinHeight
                    maxHeightChanged, newMaxHeight = imgui.drag_float('Max Height', terrain.maxHeight, 0.01)
                    if maxHeightChanged: terrain.maxHeight = newMaxHeight

                    if scaleChanged: terrain.scale = newScale
                    if elevationScaleChanged: terrain.elevationScale = newElevationScale
                    if terrainChanged: terrain.mapSize = newMapSize
                    if material.instance.has_uniform('scale'):
                        material.instance.data.scale = terrain.scale
                    if material.instance.has_uniform('elevationScale'):
                        material.instance.data.elevationScale = terrain.elevationScale
                    if terrain.run:
                        if material.instance.has_uniform('mapSize'):
                            material.instance.data.mapSize = terrain.mapSize / 8
                    if material.instance.has_uniform('cameraCoords'):
                        material.instance.data.cameraCoords = terrain.cameraCoords
                    if material.instance.has_uniform('generate'):
                        material.instance.data.generate = terrain.run
                    
                    imgui.tree_pop()
                imgui.separator()

            if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, ErosionComponent):
                if imgui.tree_node_ex('ErosionComponent', flags):
                    erosion: ErosionComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, ErosionComponent)
                    terrain: TerrainComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, TerrainComponent)

                    imgui.button('Erode', imgui.ImVec2(60, 15))
                    if imgui.is_item_clicked():
                        erosion.enabled = True
                        terrain.run = False
                        terrain.erode = True
                        erosion.counter = 0
                        erosion.started = 0
                    imgui.button('Save', imgui.ImVec2(60, 15))
                    if imgui.is_item_clicked():
                        erosion.save = True

                    imgui.tree_pop()
                imgui.separator()

            if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, StaticMeshComponent):
                if imgui.tree_node_ex('StaticMeshComponent', flags):
                    static_mesh: StaticMeshComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, StaticMeshComponent)

                    imgui.begin_disabled()
                    imgui.input_text('name', static_mesh.name)
                    imgui.end_disabled()

                    def init_drag_and_drop_mesh(instance):
                        static_mesh.name = instance.name
                        static_mesh.vbo.clear()
                        static_mesh.ebo = 0
                        static_mesh.vao = 0
                        static_mesh.load_from_file = True
                        static_mesh.attributes = [instance.vertices, instance.normals, instance.texcoords]
                        static_mesh.indices = instance.indices

                        material = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, MaterialComponent)
                        static_mesh.batch = OpenGLRenderer().add_batch(static_mesh, material)
                        
                        # Set up matrices for projection and view
                        camera = SceneManager().get_main_camera()
                        if camera != None:
                            material.instance.set_uniform('u_ModelViewProjection', camera.projection * camera.view)
                            material.instance.set_uniform('u_Model', glm.mat4(1.0))

                    if imgui.begin_drag_drop_target():
                        payload: imgui.Payload_PyId = imgui.accept_drag_drop_payload_py_id('models')
                        if payload != None:
                            mesh_already_built = False
                            for mesh_instance in MeshLib().get_meshes().values():
                                if self.drag_and_drop_mesh == str(MODELS_PATH / mesh_instance.path):
                                    instance = MeshLib().get(mesh_instance.name)
                                    init_drag_and_drop_mesh(instance)
                                    mesh_already_built = True
                                    break

                            if not mesh_already_built:
                                path: Path = Path(self.drag_and_drop_mesh)
                                try:
                                    instance = MeshLib().build(path.stem, path)
                                    init_drag_and_drop_mesh(instance)
                                except ValueError:
                                    logger.error('Error loading mesh, file type not supported')
                        imgui.end_drag_drop_target()
                    
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
                        color_changed, new_color = imgui.color_edit4('color', material.instance.data.color)
                        if color_changed: material.instance.data.color = glm.vec4(new_color[0], new_color[1], new_color[2], new_color[3])
                    
                    if material.instance.has_uniform('metallic'):
                        metallic_changed, new_metallic = imgui.drag_float('metallic', material.instance.data.metallic, 0.01, 0.0, 1.0)
                        if metallic_changed: material.instance.data.metallic = new_metallic

                    if material.instance.has_uniform('roughness'):
                        roughness_changed, new_roughness = imgui.drag_float('roughness', material.instance.data.roughness, 0.01, 0.0, 1.0)
                        if roughness_changed: material.instance.data.roughness = new_roughness

                    if material.instance.has_uniform('ao'):
                        ao_changed, new_ao = imgui.drag_float('ao', material.instance.data.ao, 0.01, 0.0, 1.0)
                        if ao_changed: material.instance.data.ao = new_ao

                    if material.instance.has_uniform('tiling'):
                        tiling_changed, new_tiling = imgui.drag_int2('tiling', material.instance.data.tiling, 1, 1, 100)
                        if tiling_changed: material.instance.data.tiling = glm.ivec2(new_tiling[0], new_tiling[1])

                    if material.instance.has_uniform('useTextures'):
                        useTextures_changed, new_useTextures = imgui.checkbox('useTextures', material.instance.data.useTextures)
                        if useTextures_changed: material.instance.data.useTextures = new_useTextures

                    if material.instance.has_uniform('_Depth'):
                        depth_changed, new_depth = imgui.drag_float('_Depth', material.instance.data.depthOfBlend, 0.01, 0.0, 10.0)
                        if depth_changed: material.instance.data.depthOfBlend = new_depth

                    if material.instance.has_uniform('maxHeight'):
                        maxHeightChanged, newMaxHeight = imgui.drag_float('maxHeight', material.instance.data.maxHeight, 0.1, 0.0)
                        if maxHeightChanged: material.instance.data.maxHeight = newMaxHeight

                    if material.instance.has_uniform('heightOfSnow'):
                        heightSnowChanged, newHeightSnow = imgui.drag_float('heightOfSnow', material.instance.data.heightOfSnow, 0.01, 0.0, 10.0)
                        if heightSnowChanged: material.instance.data.heightOfSnow = newHeightSnow
                                
                    if material.instance.has_uniform('heightOfGrass'):
                        heightGrassChanged, newHeightGrass = imgui.drag_float('heightOfGrass', material.instance.data.heightOfGrass, 0.01, 0.0, 10.0)
                        if heightGrassChanged: material.instance.data.heightOfGrass = newHeightGrass
                        
                    if material.instance.has_uniform('rockColor'):
                        rockColorChanged, newRockColor = imgui.color_edit3('rockColor', material.instance.data.rockColor.rgb)
                        if rockColorChanged: material.instance.data.rockColor = glm.vec4(newRockColor[0], newRockColor[1], newRockColor[2], 1.0)
                        
                    if material.instance.has_uniform('rockBlendAmount'):
                        rockBlendAmountChanged, newRockBlendAmount = imgui.drag_float('rockBlendAmount', material.instance.data.rockBlendAmount, 0.01, 0.0)
                        if rockBlendAmountChanged: material.instance.data.rockBlendAmount = newRockBlendAmount
                        
                    if material.instance.has_uniform('slopeTreshold'):
                        slopeThresholdChanged, newSlopeTreshold = imgui.drag_float('slopeTreshold', material.instance.data.slopeTreshold, 0.01, 0.0, 1.0)
                        if slopeThresholdChanged: material.instance.data.slopeTreshold = newSlopeTreshold
                        
                    if material.instance.has_uniform('snowColor'):
                        snowColorChanged, newSnowColor = imgui.color_edit3('snowColor', material.instance.data.snowColor.rgb)
                        if snowColorChanged: material.instance.data.snowColor = glm.vec4(newSnowColor[0], newSnowColor[1], newSnowColor[2], 1.0)
                        
                    if material.instance.has_uniform('grassColor'):
                        grassColorChanged, newGrassColor = imgui.color_edit3('grassColor', material.instance.data.grassColor.rgb)
                        if grassColorChanged: material.instance.data.grassColor = glm.vec4(newGrassColor[0], newGrassColor[1], newGrassColor[2], 1.0)
                        
                    if material.instance.has_uniform('sandColor'):
                        sandColorChanged, newSandColor = imgui.color_edit3('sandColor', material.instance.data.sandColor.rgb)
                        if sandColorChanged: material.instance.data.sandColor = glm.vec4(newSandColor[0], newSandColor[1], newSandColor[2], 1.0)

                    # Get uniform textures
                    textures = OpenGLMaterialLib().get_textures(material.instance.name)

                    for index, texture in enumerate(textures):
                        imgui.begin_disabled()
                        texture_changed, new_texture = imgui.input_text(texture, material.instance.data.textures[index])
                        imgui.end_disabled()
                        if texture_changed: material.instance.data.textures[index] = new_texture

                        if imgui.begin_drag_drop_target():
                            payload: imgui.Payload_PyId = imgui.accept_drag_drop_payload_py_id('textures')
                            if payload != None:
                                texture_already_built = False
                                for texture in OpenGLTextureLib().get_textures().values():
                                    if texture.path == None:
                                        continue
                                    
                                    # TODO: Handle textures that are in subfolders.
                                    if self.drag_and_drop_texture == str(TEXTURES_PATH / texture.path):
                                        material.instance.data.textures[0] = texture.name
                                        texture_already_built = True
                                        break

                                if not texture_already_built:
                                    path: Path = Path(self.drag_and_drop_texture)
                                    instance = OpenGLTextureLib().build(path.stem, TextureData(path))
                                    material.instance.data.textures[0] = path.stem
                            imgui.end_drag_drop_target()
                    
                    if material.instance.has_uniform('u_Glossiness'):
                        glossiness_changed, new_glossiness = imgui.drag_float('glossiness', material.instance.data.glossiness, 0.1)
                        if glossiness_changed: material.instance.data.glossiness = new_glossiness
                    
                    imgui.tree_pop()
                imgui.separator()

            if SceneManager().get_active_scene().has_component(EditorVisibleComponent.SELECTED_ENTITY, CameraControllerComponent):
                if imgui.tree_node_ex('CameraControllerComponent', flags):
                    camera_controller: InfoComponent = SceneManager().get_active_scene().get_component(EditorVisibleComponent.SELECTED_ENTITY, CameraControllerComponent)
                    modified_speed, new_speed = imgui.slider_float('Movement Speed', camera_controller.movement_speed, 0.0, 10.0)
                    if modified_speed:
                        camera_controller.movement_speed = new_speed

                    modified_mouse_sensitivity, new_mouse_sensitivity = imgui.slider_float('Mouse Sensitivity', camera_controller.mouse_sensitivity, 0.0, 2.0)
                    if modified_mouse_sensitivity:
                        camera_controller.mouse_sensitivity = new_mouse_sensitivity
                    imgui.tree_pop()                  
                imgui.separator()

            if imgui.begin_menu('Add Component'):
                modified_info, _ = imgui.menu_item('Info Component', '', False)
                if modified_info:
                    SceneManager().get_active_scene().add_component(EditorVisibleComponent.SELECTED_ENTITY, InfoComponent())
                modified_transform, _ = imgui.menu_item('Transform Component', '', False)
                if modified_transform:
                    SceneManager().get_active_scene().add_component(EditorVisibleComponent.SELECTED_ENTITY, ComponentLib().Transform(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
                modified_link, _ = imgui.menu_item('Link Component', '', False)
                if modified_link:
                    SceneManager().get_active_scene().add_component(EditorVisibleComponent.SELECTED_ENTITY, LinkComponent(None))
                modified_camera, _ = imgui.menu_item('Camera Component', '', False)
                if modified_camera:
                    SceneManager().get_active_scene().add_component(EditorVisibleComponent.SELECTED_ENTITY, CameraComponent(45, 1.778, 0.1, 1000, 5.0, CameraComponent.Type.PERSPECTIVE))
                modified_camera_controller, _ = imgui.menu_item('Camera Controller Component', '', False)
                if modified_camera_controller:
                    SceneManager().get_active_scene().add_component(EditorVisibleComponent.SELECTED_ENTITY, CameraControllerComponent())
                modified_light, _ = imgui.menu_item('Light Component', '', False)
                if modified_light:
                    SceneManager().get_active_scene().add_component(EditorVisibleComponent.SELECTED_ENTITY, LightComponent(glm.vec3(1, 1, 1), 1.0))
                modified_static_mesh, _ = imgui.menu_item('Static Mesh Component', '', False)
                if modified_static_mesh:
                    SceneManager().get_active_scene().add_component(EditorVisibleComponent.SELECTED_ENTITY, StaticMeshComponent('empty', [], None))
                    
                    # TODO: Extend editor to be able to choose shader
                    OpenGLTextureLib().build('white_texture', TextureData(image_bytes=0xffffffff.to_bytes(4, byteorder='big'), width=1, height=1))
                    OpenGLShaderLib().build('default_lit', SHADERS_PATH/'lit_blinn_phong_vertex.glsl', SHADERS_PATH/'lit_blinn_phong_fragment.glsl')
                    OpenGLMaterialLib().build('M_Lit', MaterialData('default_lit', ['white_texture']))

                    SceneManager().get_active_scene().add_component(EditorVisibleComponent.SELECTED_ENTITY, MaterialComponent('M_Lit'))
                imgui.end_menu()

    def draw_menu_bar(self):
        if InputManager().get_key_down(glfw.KEY_LEFT_CONTROL):
            if InputManager().get_key_down(glfw.KEY_S):
                scene: Scene = SceneManager().get_active_scene()
                scene_serializer: SceneSerializer = SceneSerializer(scene)
                scene_serializer.serialize(SCENES_PATH / f"{scene.name}.usda")

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu('File'):
                save_pressed, _ = imgui.menu_item('Save', 'Ctrl + S', False)
                if save_pressed:
                    scene: Scene = SceneManager().get_active_scene()
                    scene_serializer: SceneSerializer = SceneSerializer(scene)
                    scene_serializer.serialize(SCENES_PATH / f"{scene.name}.usda")
                load_pressed = imgui.begin_menu('Load')
                if load_pressed:
                    for file in glob.glob(str(SCENES_PATH / "*.usd*")):
                        path: Path = Path(file)
                        file_pressed, _ = imgui.menu_item(path.name, '', False)
                        if file_pressed:
                            EditorVisibleComponent.SELECTED = False
                            EditorVisibleComponent.SELECTED_ENTITY = None

                            OpenGLShaderLib().clean()

                            scene: Scene = Scene(path.name)
                            scene_serializer: SceneSerializer = SceneSerializer(scene)
                            scene_serializer.deserialize(SCENES_PATH / path.name)
                            SceneManager().open_external_scene(scene)

                    imgui.end_menu()
                close_pressed, _ = imgui.menu_item('Close', 'Alt + F4', False)
                if close_pressed:
                    from pyGandalf.core.application import Application
                    Application().quit()
                imgui.end_menu()

            if imgui.begin_menu('View'):
                editor_panel_system: EditorPanelSystem = EditorManager().get_scene().get_system(EditorPanelSystem)
                if editor_panel_system != None:
                    for panel in editor_panel_system.filtered_components:
                        modified, show = imgui.checkbox(panel[0].name, panel[0].enabled)
                        if modified:
                            panel[0].enabled = show
                imgui.end_menu()
                
            if imgui.begin_menu('Settings'):
                modified_camera_distance, new_distance = imgui.slider_float('Camera Pivot Distance', self.camera_pivot_distance, 0.0, 50.0)
                if modified_camera_distance:
                    self.camera_pivot_distance = new_distance

                modified_wireframe, show = imgui.checkbox('Wireframe', self.wireframe_value)
                if modified_wireframe:
                    if show:
                        OpenGLRenderer().set_fill_mode(gl.GL_LINE)
                    else:
                        OpenGLRenderer().set_fill_mode(gl.GL_FILL)
                    self.wireframe_value = show

                from pyGandalf.core.application import Application
                self.vsync_value = Application().get_window().vertical_sync

                modified_vsync, enable = imgui.checkbox('Vertical Sync', self.vsync_value)
                if modified_vsync:
                    if enable:
                        glfw.swap_interval(1)
                        Application().get_window().vertical_sync = True
                    else:
                        glfw.swap_interval(0)
                        Application().get_window().vertical_sync = False
                    self.vsync_value = enable

                imgui.end_menu()
            if imgui.begin_menu('Help'):
                gizmos_pressed, _ = imgui.menu_item('Gizmos', '', False)
                if gizmos_pressed:
                    self.gizmos_pressed = True
                camera_controller_pressed, _ = imgui.menu_item('Camera Controller', '', False)
                if camera_controller_pressed:
                    self.camera_controller_pressed = True
                imgui.end_menu()
            imgui.end_main_menu_bar()

            if self.gizmos_pressed:
                self.gizmos_pressed, self.gizmos_pressed = imgui.begin('Gizmos Help', self.gizmos_pressed)
                imgui.text_wrapped('1. Select the object that you want to manipulate from the Hierachy panel')
                imgui.text_wrapped('2. You can press the T key for enabling the translation mode of the gizmo')
                imgui.text_wrapped('3. You can press the R key for enabling the rotation mode of the gizmo')
                imgui.text_wrapped('4. You can press the S key for enabling the scale mode of the gizmo')
                imgui.text_wrapped('5. You can press the Q key for disabling the gizmo')
                imgui.end()

            if self.camera_controller_pressed:
                self.gizmos_camera_controller_pressedpressed, self.camera_controller_pressed = imgui.begin('Camera Controller Help', self.camera_controller_pressed)
                imgui.text_wrapped('When the camera entity has the CameraControllerComponent, you can move aroung by:')
                imgui.text_wrapped('While pressing the Right Mouse Button:')
                imgui.text_wrapped('    - WASD: for moving forwards/backwards, left/right')
                imgui.text_wrapped('    - QE: for moving up/down')
                imgui.text_wrapped('    - Draging the mouse around pans the camera view')
                imgui.end()

    def draw_content_browser(self):
        padding = 16.0
        thumbnail_size = 128.0
        panel_width = imgui.get_content_region_avail().x

        column_count = int(panel_width / (padding + thumbnail_size))

        column_count = 1 if column_count == 0 else column_count

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
                        
            self.drag_and_drop_mesh = None
            self.drag_and_drop_scene = None
            self.drag_and_drop_texture = None

            id = 0
            # Loop through directory items
            for entry in os.listdir(self.current_directory):
                imgui.table_next_column()
                imgui.push_id(id)
                # Display directory item
                # imgui.push_style_color(imgui.Col_.button, imgui.ImVec4(0, 0, 0, 0))
                imgui.button(entry, imgui.ImVec2(thumbnail_size, thumbnail_size))

                if 'models' in str(self.current_directory):
                    if imgui.begin_drag_drop_source():
                        payload_id = id
                        if imgui.set_drag_drop_payload_py_id("models", payload_id):
                            self.drag_and_drop_mesh = str(MODELS_PATH / entry)
                        imgui.end_drag_drop_source()

                if 'scenes' in str(self.current_directory):
                    if imgui.begin_drag_drop_source():
                        payload_id = id
                        if imgui.set_drag_drop_payload_py_id("scenes", payload_id):
                            self.drag_and_drop_scene = str(SCENES_PATH / entry)
                        imgui.end_drag_drop_source()

                if 'textures' in str(self.current_directory):
                    if imgui.begin_drag_drop_source():
                        payload_id = id
                        if imgui.set_drag_drop_payload_py_id("textures", payload_id):
                            self.drag_and_drop_texture = str(TEXTURES_PATH / entry)
                        imgui.end_drag_drop_source()

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

    def draw_systems_panel(self):
        for system in SceneManager().get_active_scene().get_systems():
            imgui.text_wrapped(type(system).__name__)
            imgui.same_line(imgui.get_window_width() - 80)
            if system.state == SystemState.PAUSE:
                imgui.button('Resume', imgui.ImVec2(60, 20))
                if imgui.is_item_clicked():
                    system.set_state(SystemState.PLAY)
            elif system.state == SystemState.PLAY:
                imgui.button('Pause', imgui.ImVec2(60, 20))
                if imgui.is_item_clicked():
                    system.set_state(SystemState.PAUSE)
            imgui.separator()