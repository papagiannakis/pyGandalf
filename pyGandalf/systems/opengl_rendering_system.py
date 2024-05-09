from pyGandalf.systems.system import System
from pyGandalf.renderer.opengl_renderer import OpenGLRenderer

from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib

from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.entity import Entity

import glm

class OpenGLStaticMeshRenderingSystem(System):
    """
    The system responsible for rendering.
    """

    def on_create(self, entity: Entity, components):
        """
        Gets called once in the first frame for every entity that the system operates on.
        """
        mesh, material, transform = components

        mesh.vao = 0
        mesh.ebo = 0
        mesh.vbo.clear()

        material.instance = OpenGLMaterialLib().get(material.name)

        if mesh.load_from_file == True:
            mesh_instance = OpenGLMeshLib().get(mesh.name)
            mesh.attributes = [mesh_instance.vertices, mesh_instance.normals, mesh_instance.texcoords]
            mesh.indices = mesh_instance.indices

        if len(mesh.attributes) == 0:
            return
        
        mesh.batch = OpenGLRenderer().add_batch(mesh, material)

        # Set up matrices for projection and view
        camera = SceneManager().get_main_camera()
        if camera != None:
            material.instance.set_uniform('u_Projection', camera.projection)
            material.instance.set_uniform('u_View', camera.view)
            material.instance.set_uniform('u_Model', glm.mat4(1.0))

    def on_update(self, ts, entity: Entity, components):
        """
        Gets called every frame for every entity that the system operates on.
        """
        mesh, material, transform = components

        if len(mesh.attributes) == 0:
            return

        # Draw the mesh
        if (mesh.indices is None):
            OpenGLRenderer().draw(transform.world_matrix, mesh, material)
        else:
            OpenGLRenderer().draw_indexed(transform.world_matrix, mesh, material)