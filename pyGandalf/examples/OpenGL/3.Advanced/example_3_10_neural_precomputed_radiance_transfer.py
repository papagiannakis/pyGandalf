import numpy as np
import OpenGL.GL as gl
from pyGandalf.core.application import Application
from pyGandalf.core.opengl_window import OpenGLWindow

from pyGandalf.systems.system import System
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.camera_system import CameraSystem
from pyGandalf.systems.camera_controller_system import CameraControllerSystem
from pyGandalf.systems.opengl_rendering_system import OpenGLStaticMeshRenderingSystem

from pyGandalf.renderer.opengl_renderer import OpenGLRenderer

from pyGandalf.scene.scene import Scene
from pyGandalf.scene.scene_manager import SceneManager
from pyGandalf.scene.components import *

from pyGandalf.utilities.opengl_material_lib import MaterialDescriptor, OpenGLMaterialLib, MaterialData
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib, TextureData, TextureDescriptor, TextureDimension
from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH, MODELS_PATH, NN_PATH
from pyGandalf.utilities.logger import logger
from pyGandalf.utilities.prt_lib import HDRI_frame, NeuralPRT, OBJLoader, Sampler, SphericalHarmonics, SHModel


"""
Showcase of the Precomputed Radiance Transfer (PRT) algorithm.
"""
NPRT_Model = None
PRT_Vertices = None
PRT_Normals = None

def rotate_vertices(vertices, vec3):
    """
    Rotate vertices by Euler angles.
    :param vertices: Nx3 NumPy array of vertices
    :param vec3: List or array [theta_x, theta_y, theta_z] in radians
    :return: Rotated Nx3 NumPy array of vertices
    """
    theta_x, theta_y, theta_z = vec3

    # Rotation matrix for X-axis
    R_x = np.array([
        [1, 0, 0],
        [0, np.cos(theta_x), -np.sin(theta_x)],
        [0, np.sin(theta_x), np.cos(theta_x)]
    ])

    # Rotation matrix for Y-axis
    R_y = np.array([
        [np.cos(theta_y), 0, np.sin(theta_y)],
        [0, 1, 0],
        [-np.sin(theta_y), 0, np.cos(theta_y)]
    ])

    # Rotation matrix for Z-axis
    R_z = np.array([
        [np.cos(theta_z), -np.sin(theta_z), 0],
        [np.sin(theta_z), np.cos(theta_z), 0],
        [0, 0, 1]
    ])

    # Combined rotation matrix (Z * Y * X)
    R = R_z @ R_y @ R_x

    # Rotate vertices
    rotated_vertices = vertices @ R.T  # Transpose R for correct multiplication
    return rotated_vertices

class RotateAroundComponent(Component):
    def __init__(self, axis: list, speed: float, meshC: StaticMeshComponent) -> None:
        self.axis = axis
        self.speed = speed
        self.enabled = True
        self.meshC = meshC

class RotateAroundSystem(System):
    """
    The system responsible rotating around entities.
    """

    def on_create_entity(self, entity: Entity, components: Component | tuple[Component]):
        pass

    def on_update_entity(self, ts, entity: Entity, components: Component | tuple[Component]):
        rotate_around, transform = components

        global NPRT_Model
        global PRT_Vertices
        global PRT_Normals

        if rotate_around.enabled:
            if rotate_around.axis[0] == 1:
                transform.rotation.x += rotate_around.speed * ts

            if rotate_around.axis[1] == 1:
                transform.rotation.y += rotate_around.speed * ts
                
            if rotate_around.axis[2] == 1:
                transform.rotation.z += rotate_around.speed * ts

            if(NPRT_Model!=None):
                new_vertices = rotate_vertices(PRT_Vertices, glm.vec3(np.radians(transform.rotation.x),np.radians(transform.rotation.y), np.radians(transform.rotation.z)))
                new_normals = rotate_vertices(PRT_Normals, glm.vec3(np.radians(transform.rotation.x),np.radians(transform.rotation.y), np.radians(transform.rotation.z)))
                NPRT_Model.set_vertices(new_vertices)
                NPRT_Model.set_normals(new_normals)
                colors = NPRT_Model.run_model()

                OpenGLRenderer().update_colors(colors, 2)


def main():

    #meshName = sys.argv[1]
    #lightprobeName = sys.argv[2]
    #samples = int(sys.argv[3])
    #bands = int(sys.argv[4])

    global NPRT_Model
    global PRT_Vertices
    global PRT_Normals

    meshName = "monkey_flat.obj"
    lightprobeName = "campus_probe.hdr"
    samples = 5
    bands = 3

    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new scene
    scene = Scene('Precomputed Radiance Transfer Scene')

    # Create a new application
    Application().create(OpenGLWindow('Precomputed Radiance Transfer', 1280, 720, True), OpenGLRenderer)

    # Create Enroll entities to registry

    mesh = scene.enroll_entity()
    camera = scene.enroll_entity()
    skybox = scene.enroll_entity()

    hdrImg = HDRI_frame()
    hdrImg.create_cube_map_faces(hdrImg.read_hdr(TEXTURES_PATH / 'skybox' / 'cubemaps' / lightprobeName))

    # Array that holds all the skybox textures
    skybox_bytes = [
        hdrImg.cubemap[0],
        hdrImg.cubemap[1],
        hdrImg.cubemap[2],
        hdrImg.cubemap[3],
        hdrImg.cubemap[4],
        hdrImg.cubemap[5],
    ]

    # Vertices for the cube
    vertices_skybox = np.array([
        [-1.0, -1.0, -1.0], [-1.0, -1.0,  1.0], [-1.0,  1.0,  1.0], [ 1.0,  1.0, -1.0],
        [-1.0, -1.0, -1.0], [-1.0,  1.0, -1.0], [1.0, -1.0,  1.0], [-1.0, -1.0, -1.0],
        [1.0, -1.0, -1.0], [ 1.0,  1.0, -1.0], [1.0, -1.0, -1.0], [-1.0, -1.0, -1.0],

        [-1.0, -1.0, -1.0], [-1.0,  1.0,  1.0], [-1.0,  1.0, -1.0], [ 1.0, -1.0,  1.0],
        [-1.0, -1.0,  1.0], [-1.0, -1.0, -1.0], [-1.0,  1.0,  1.0], [-1.0, -1.0,  1.0],
        [1.0, -1.0,  1.0], [1.0,  1.0,  1.0], [1.0, -1.0, -1.0], [1.0,  1.0, -1.0],

        [1.0, -1.0, -1.0], [1.0,  1.0,  1.0], [1.0, -1.0,  1.0], [1.0,  1.0,  1.0],
        [1.0,  1.0, -1.0], [-1.0,  1.0, -1.0], [1.0,  1.0,  1.0], [-1.0,  1.0, -1.0],
        [-1.0,  1.0,  1.0], [1.0,  1.0,  1.0], [-1.0,  1.0,  1.0], [1.0, -1.0,  1.0]
    ], dtype=np.float32)

    #Build skybox texutre
    if(hdrImg.dimx < hdrImg.dimy):
        OpenGLTextureLib().build('cube_map', TextureData(image_bytes=skybox_bytes, width=(hdrImg.dimx//3), height=(hdrImg.dimy//4)), TextureDescriptor(flip=False, dimention=TextureDimension.CUBE, internal_format=gl.GL_RGB, format=gl.GL_RGB))
    else:
        OpenGLTextureLib().build('cube_map', TextureData(image_bytes=skybox_bytes, width=(hdrImg.dimx//4), height=(hdrImg.dimy//3)), TextureDescriptor(flip=False, dimention=TextureDimension.CUBE, internal_format=gl.GL_RGB, format=gl.GL_RGB))
    OpenGLShaderLib().build('skybox', SHADERS_PATH / 'opengl' / 'skybox.vs', SHADERS_PATH / 'opengl' / 'skybox.fs')
    OpenGLMaterialLib().build('M_Skybox', MaterialData('skybox', ['cube_map']), MaterialDescriptor(cull_face=gl.GL_FRONT, depth_mask=gl.GL_FALSE))


    # Build shaders 
    OpenGLShaderLib().build('unlitPRT', SHADERS_PATH/'opengl'/'unlit_color.vs', SHADERS_PATH/'opengl'/'unlit_color.fs')
    
    # Build Materials
    OpenGLMaterialLib().build('M_UnlitPRT', MaterialData('unlitPRT', []))

    # Load model
    PRT_Model = OBJLoader()

    PRT_Model.load_model(MODELS_PATH / meshName, True)
    PRT_Vertices = PRT_Model.get_vertices()
    PRT_Indices = PRT_Model.get_faces().flatten()
    PRT_Normals = PRT_Model.get_normals()

    sh = SphericalHarmonics(bands)
    ssampler = Sampler(samples)

    NPRT_Model = NeuralPRT(NN_PATH / 'PRTUnshadowed.pth', PRT_Vertices, PRT_Normals, sh, ssampler, lightprobeName, bands)

    colors = NPRT_Model.run_model()

    # Register components to mesh
    scene.add_component(mesh, InfoComponent("mesh"))
    scene.add_component(mesh, TransformComponent(glm.vec3(0, 0, 5), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(mesh, StaticMeshComponent('mesh',[PRT_Vertices, colors], PRT_Indices))
    scene.add_component(mesh, MaterialComponent('M_UnlitPRT'))
    scene.add_component(mesh, RotateAroundComponent([0, 1, 0], 30.0, scene.get_component(mesh, StaticMeshComponent)))

    # Register components to skybox
    scene.add_component(skybox, InfoComponent("skybox"))
    scene.add_component(skybox, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(skybox, StaticMeshComponent('skybox', [vertices_skybox]))
    scene.add_component(skybox, MaterialComponent('M_Skybox'))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 180, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, CameraComponent(45, 1280/720, 0.01, 1000, 1, CameraComponent.Type.PERSPECTIVE))
    scene.add_component(camera, CameraControllerComponent())

    # Register the systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(OpenGLStaticMeshRenderingSystem([StaticMeshComponent, MaterialComponent, TransformComponent]))
    scene.register_system(CameraControllerSystem([CameraControllerComponent, CameraComponent, TransformComponent]))

    scene.register_system(RotateAroundSystem([RotateAroundComponent, TransformComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start applications
    Application().start()

if __name__ == "__main__":
    main()
