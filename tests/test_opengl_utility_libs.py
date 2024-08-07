from pyGandalf.utilities.opengl_shader_lib import OpenGLShaderLib
from pyGandalf.utilities.opengl_texture_lib import OpenGLTextureLib, TextureData
from pyGandalf.utilities.opengl_material_lib import OpenGLMaterialLib, MaterialData
from pyGandalf.utilities.mesh_lib import MeshLib

from pyGandalf.utilities.definitions import *

from pyGandalf.core.application import Application
from pyGandalf.core.opengl_window import OpenGLWindow
from pyGandalf.renderer.opengl_renderer import OpenGLRenderer

Application().create(OpenGLWindow(), OpenGLRenderer)

def test_opengl_texture_lib():
    slot1 = OpenGLTextureLib().build('uoc_logo', data=TextureData(TEXTURES_PATH/'uoc_logo.png'))
    slot2 = OpenGLTextureLib().build('white_texture', data=TextureData(image_bytes=0xffffffff.to_bytes(4, byteorder='big'), width=1, height=1))

    assert slot1 != slot2
    assert slot2 != 0 and slot2 != 0

def test_opengl_shader_lib():
    program1 = OpenGLShaderLib().build('default_colored_yellow', SHADERS_PATH/'opengl'/'unlit_simple.vs', SHADERS_PATH/'opengl'/'unlit_simple.fs')

    assert program1 > 0

    program2 = OpenGLShaderLib().build('default_mesh', SHADERS_PATH/'opengl'/'lit_blinn_phong.vs', SHADERS_PATH/'opengl'/'lit_blinn_phong.fs')

    assert program2 > 0 and program1 != program2

    program3 = OpenGLShaderLib().build('default_mesh', SHADERS_PATH/'opengl'/'lit_blinn_phong.vs', SHADERS_PATH/'opengl'/'lit_blinn_phong.fs')

    assert program3 > 0 and program3 == program2

def test_opengl_material_lib():
    program1 = OpenGLShaderLib().build('default_colored_yellow', SHADERS_PATH/'opengl'/'unlit_simple.vs', SHADERS_PATH/'opengl'/'unlit_simple.fs')

    material1 = OpenGLMaterialLib().build('M_Yellow_Simple', MaterialData('default_colored_yellow', []))

    assert program1 > 0 and material1 != None

    material1_variation_1 = OpenGLMaterialLib().build('M_Yellow_Simple_Var', MaterialData('default_colored_yellow', []))

    assert material1 != material1_variation_1
    
    assert material1.name == material1_variation_1.name
    assert material1.data.textures == material1_variation_1.data.textures
    assert material1.shader_program == material1_variation_1.shader_program
    assert material1.shader_params == material1_variation_1.shader_params

    assert OpenGLMaterialLib().get('M_Yellow_Simple') != OpenGLMaterialLib().get('M_Yellow_Simple_Var')

    program2 = OpenGLShaderLib().build('default_mesh', SHADERS_PATH/'opengl'/'lit_blinn_phong.vs', SHADERS_PATH/'opengl'/'lit_blinn_phong.fs')

    OpenGLTextureLib().build('white_texture', data=TextureData(image_bytes=0xffffffff.to_bytes(4, byteorder='big'), width=1, height=1))
    OpenGLTextureLib().build('uoc_logo', data=TextureData(TEXTURES_PATH/'uoc_logo.png'))

    blinn_phong_material1 = OpenGLMaterialLib().build('M_Bilnn-Phong1', MaterialData('default_mesh', ['white_texture']))
    blinn_phong_material2 = OpenGLMaterialLib().build('M_Bilnn-Phong2', MaterialData('default_mesh', ['uoc_logo']))

    assert blinn_phong_material1 != blinn_phong_material2
    assert blinn_phong_material1.data.textures != blinn_phong_material2.data.textures
    assert blinn_phong_material1.shader_program == blinn_phong_material2.shader_program == program2
    assert blinn_phong_material1.shader_params == blinn_phong_material2.shader_params

def test_mesh_lib():
    mesh1 = MeshLib().build('monkeh_mesh1', MODELS_PATH/'monkey_flat.obj')
    mesh2 = MeshLib().build('monkeh_mesh2', MODELS_PATH/'monkey_flat.obj')
    mesh3 = MeshLib().build('monkeh_mesh3', MODELS_PATH/'fa_flintlockPistol.obj')

    assert mesh1 == mesh2
    assert mesh1 != mesh3 and mesh2 != mesh3

