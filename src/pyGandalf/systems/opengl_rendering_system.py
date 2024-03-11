from pyGandalf.scene.entity import Entity
from pyGandalf.systems.system import System
from pyGandalf.scene.components import CameraComponent
from pyGandalf.renderer.opengl_renderer import OpenGLRenderer
from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib

from pyGandalf.scene.scene_manager import SceneManager

import glm

class OpenGLRenderingSystem(System):
    """
    The system responsible for rendering.
    """

    def on_create(self, entity: Entity, components):
        """
        Gets called once in the first frame for every entity that the system operates on.
        """
        render_data, material, transform = components

        material.instance = OpenGLMaterialLib().get(material.name)

        render_data.batch = OpenGLRenderer().add_batch(render_data, material)

        # Set up matrices for projection and view
        camera = SceneManager().get_main_camera()
        material.instance.set_uniform('u_Projection', camera.projection)
        material.instance.set_uniform('u_View', camera.view)
        material.instance.set_uniform('u_Model', glm.mat4(1.0))

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        render_data, material, transform = components
        
        if (render_data.indices is None):
            OpenGLRenderer().draw(transform.world_matrix, render_data, material)
        else:
            OpenGLRenderer().draw_indexed(transform.world_matrix, render_data, material)