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

from pyGandalf.utilities.definitions import SHADERS_PATH, TEXTURES_PATH, MODELS_PATH
from pyGandalf.utilities.logger import logger
from pyGandalf.utilities.prt_lib import BVHTree, HDRI_frame, PRTLoader, Sampler, SphericalHarmonics


"""
Showcase of the Precomputed Radiance Transfer (PRT) algorithm.
"""

def main():

    #meshName = sys.argv[1]
    #lightprobeName = sys.argv[2]
    #samples = int(sys.argv[3])
    #bands = int(sys.argv[4])

    meshName = "monkey_flat.obj"
    lightprobeName = "campus_probe.hdr"
    samples = 5
    bands = 3

    shadowed = False # For shadowed version, set this to True
    interreflections = False #For interreflections version, set this to True (also shadowed version must be true)

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
    PRT_Model = PRTLoader()
    PRT_Model.load_model(MODELS_PATH / meshName, True)
    PRT_Vertices = PRT_Model.get_vertices()
    PRT_Indices = PRT_Model.get_faces().flatten()
    PRT_Normals = PRT_Model.get_normals()

    sh = SphericalHarmonics(bands)
    ssampler = Sampler(samples)

    if(shadowed):
        if(interreflections):
            bvh = BVHTree.computeBVHTree(PRT_Vertices, PRT_Indices)
            colors = sh.interreflections(bvh, bands*bands, ssampler, PRT_Vertices, PRT_Normals, PRT_Indices, 2, lightprobeName, meshName)
        else:
            colors = sh.ProjectShadowed(ssampler, PRT_Vertices, PRT_Normals, bands, PRT_Indices, lightprobeName) 
    else:
        colors = sh.ProjectUnshadowed(ssampler, PRT_Vertices, PRT_Normals, bands, lightprobeName, meshName)

    # Register components to mesh
    scene.add_component(mesh, InfoComponent("mesh"))
    scene.add_component(mesh, TransformComponent(glm.vec3(0, 0, 5), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(mesh, StaticMeshComponent('mesh',[PRT_Vertices, colors], PRT_Indices))
    scene.add_component(mesh, MaterialComponent('M_UnlitPRT'))

    # Register components to skybox
    scene.add_component(skybox, InfoComponent("skybox"))
    scene.add_component(skybox, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(skybox, StaticMeshComponent('skybox', [vertices_skybox]))
    scene.add_component(skybox, MaterialComponent('M_Skybox'))

    # Register components to camera
    scene.add_component(camera, InfoComponent("camera"))
    scene.add_component(camera, TransformComponent(glm.vec3(0, 0, 10), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(camera, CameraComponent(45, 1280/720, 0.01, 1000, 1, CameraComponent.Type.PERSPECTIVE))
    scene.add_component(camera, CameraControllerComponent())

    # Register the systems
    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(CameraSystem([CameraComponent, TransformComponent]))
    scene.register_system(OpenGLStaticMeshRenderingSystem([StaticMeshComponent, MaterialComponent, TransformComponent]))
    scene.register_system(CameraControllerSystem([CameraControllerComponent, CameraComponent, TransformComponent]))

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()
