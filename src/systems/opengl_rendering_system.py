from scene.entity import Entity
from systems.system import System
from renderer.opengl_renderer import OpenGLRenderer
from utilities.opengl_material_lib import OpenGLMaterialLib

import utilities.math as utils

import OpenGL.GL as gl

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
        projection = utils.perspective(45.0, 1920 / 1080, 0.1, 100.0)
        view = utils.translate(0.0, 0.0, -5.0)
        model = utils.identity()

        gl.glUniformMatrix4fv(gl.glGetUniformLocation(material.instance.shader_program, "projection"), 1, gl.GL_FALSE, projection)
        gl.glUniformMatrix4fv(gl.glGetUniformLocation(material.instance.shader_program, "view"), 1, gl.GL_FALSE, view)
        gl.glUniformMatrix4fv(gl.glGetUniformLocation(material.instance.shader_program, "model"), 1, gl.GL_FALSE, model)

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        render_data, material, transform = components
        
        if (render_data.indices is None):
            OpenGLRenderer().draw(transform.world_matrix, render_data, material)
        else:
            OpenGLRenderer().draw_indexed(transform.world_matrix, render_data, material)