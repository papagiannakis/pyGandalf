from pyGandalf.scene.entity import Entity
from pyGandalf.systems.system import System
from pyGandalf.renderer.opengl_renderer import OpenGLRenderer
from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib

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
        projection = glm.perspective(45.0, 1920 / 1080, 0.1, 100.0)
        view = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -5.0))
        model = glm.mat4(1.0)

        material.instance.set_uniform('u_Projection', projection)
        material.instance.set_uniform('u_View', view)
        material.instance.set_uniform('u_Model', model)

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        render_data, material, transform = components
        
        if (render_data.indices is None):
            OpenGLRenderer().draw(transform.world_matrix, render_data, material)
        else:
            OpenGLRenderer().draw_indexed(transform.world_matrix, render_data, material)