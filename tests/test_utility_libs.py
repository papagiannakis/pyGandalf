from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib
from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib, MaterialData, MaterialInstance
from pyGandalf.utilities.opengl_mesh_lib import OpenGLMeshLib, MeshInstance

from pyGandalf.utilities.definitions import *

from pyGandalf.core.application import Application
from pyGandalf.core.opengl_window import OpenGLWindow
from pyGandalf.renderer.opengl_renderer import OpenGLRenderer

Application().create(OpenGLWindow(), OpenGLRenderer)

def test_texture_lib():
    slot1 = OpenGLTextureLib().build('uoc_logo', TEXTURES_PATH/'uoc_logo.png')
    slot2 = OpenGLTextureLib().build('white_texture', None, [0xffffffff.to_bytes(4, byteorder='big'), 1, 1])

    assert slot1 != slot2
    assert slot2 != 0 and slot2 != 0

def test_shader_lib():
    vertex_shader_code = OpenGLShaderLib().load_from_file(SHADERS_PATH/'vertex_shader_code.glsl')
    fragment_shader_code_yellow = OpenGLShaderLib().load_from_file(SHADERS_PATH/'fragment_shader_code_yellow.glsl')

    program1 = OpenGLShaderLib().build('default_colored_yellow', vertex_shader_code, fragment_shader_code_yellow)

    assert program1 > 0

    blinn_phong_mesh_vertex = OpenGLShaderLib().load_from_file(SHADERS_PATH/'blinn_phong_mesh_vertex.glsl')
    blinn_phong_mesh_fragment = OpenGLShaderLib().load_from_file(SHADERS_PATH/'blinn_phong_mesh_fragment.glsl')

    program2 = OpenGLShaderLib().build('default_mesh', blinn_phong_mesh_vertex, blinn_phong_mesh_fragment)

    assert program2 > 0 and program1 != program2

def test_material_lib():
    vertex_shader_code = OpenGLShaderLib().load_from_file(SHADERS_PATH/'vertex_shader_code.glsl')
    fragment_shader_code_yellow = OpenGLShaderLib().load_from_file(SHADERS_PATH/'fragment_shader_code_yellow.glsl')

    program1 = OpenGLShaderLib().build('default_colored_yellow', vertex_shader_code, fragment_shader_code_yellow)

    material1 = OpenGLMaterialLib().build('M_Yellow_Simple', MaterialData('default_colored_yellow', []))

    assert program1 > 0 and material1 != None

    material1_variation_1 = OpenGLMaterialLib().build('M_Yellow_Simple_Var', MaterialData('default_colored_yellow', []))

    assert material1 != material1_variation_1
    
    assert material1.name == material1_variation_1.name
    assert material1.textures == material1_variation_1.textures
    assert material1.shader_program == material1_variation_1.shader_program
    assert material1.shader_params == material1_variation_1.shader_params

    assert OpenGLMaterialLib().get('M_Yellow_Simple') != OpenGLMaterialLib().get('M_Yellow_Simple_Var')

    blinn_phong_mesh_vertex = OpenGLShaderLib().load_from_file(SHADERS_PATH/'blinn_phong_mesh_vertex.glsl')
    blinn_phong_mesh_fragment = OpenGLShaderLib().load_from_file(SHADERS_PATH/'blinn_phong_mesh_fragment.glsl')

    program2 = OpenGLShaderLib().build('default_mesh', blinn_phong_mesh_vertex, blinn_phong_mesh_fragment)

    OpenGLTextureLib().build('white_texture', None, [0xffffffff.to_bytes(4, byteorder='big'), 1, 1])
    OpenGLTextureLib().build('uoc_logo', TEXTURES_PATH/'uoc_logo.png')

    blinn_phong_material1 = OpenGLMaterialLib().build('M_Bilnn-Phong1', MaterialData('default_mesh', ['white_texture']))
    blinn_phong_material2 = OpenGLMaterialLib().build('M_Bilnn-Phong2', MaterialData('default_mesh', ['uoc_logo']))

    assert blinn_phong_material1 != blinn_phong_material2
    assert blinn_phong_material1.textures != blinn_phong_material2.textures
    assert blinn_phong_material1.shader_program == blinn_phong_material2.shader_program == program2
    assert blinn_phong_material1.shader_params == blinn_phong_material2.shader_params

def test_mesh_lib():
    mesh1 = OpenGLMeshLib().build('monkeh_mesh1', MODELS_PATH/'monkey_flat.obj')
    mesh2 = OpenGLMeshLib().build('monkeh_mesh2', MODELS_PATH/'monkey_flat.obj')
    mesh3 = OpenGLMeshLib().build('monkeh_mesh3', MODELS_PATH/'fa_flintlockPistol.obj')

    assert mesh1 == mesh2
    assert mesh1 != mesh3 and mesh2 != mesh3

