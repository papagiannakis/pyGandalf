from pyGandalf.utilities.webgpu_shader_lib import WebGPUShaderLib
from pyGandalf.utilities.webgpu_texture_lib import WebGPUTextureLib, TextureData, TextureDescriptor
from pyGandalf.utilities.webgpu_material_lib import WebGPUMaterialLib, MaterialData, MaterialInstance
from pyGandalf.utilities.mesh_lib import MeshLib, MeshInstance

from pyGandalf.utilities.definitions import *

from pyGandalf.core.application import Application
from pyGandalf.core.webgpu_window import WebGPUWindow
from pyGandalf.renderer.webgpu_renderer import WebGPURenderer

Application().create(WebGPUWindow(), WebGPURenderer)

def test_wgpu_texture_lib():
    slot1 = WebGPUTextureLib().build('uoc_logo', TextureData(TEXTURES_PATH / 'uoc_logo.png'))
    slot2 = WebGPUTextureLib().build('white_texture', TextureData(image_bytes=0xffffffff.to_bytes(4, byteorder='big'), width=1, height=1))

    assert slot1 != slot2
    assert slot2 != 0 and slot2 != 0

def test_wgpu_shader_lib():
    program1 = WebGPUShaderLib().build('default_colored_yellow', SHADERS_PATH / 'webgpu' / 'unlit.wgsl')

    assert program1 != None

    program2 = WebGPUShaderLib().build('default_mesh', SHADERS_PATH / 'webgpu' / 'lit_blinn_phong.wgsl')

    assert program2 != None and program1 != program2

    program3 = WebGPUShaderLib().build('default_mesh', SHADERS_PATH / 'webgpu' / 'lit_blinn_phong.wgsl')

    assert program3 != None and program3 == program2

def test_wgpu_material_lib():
    program1 = WebGPUShaderLib().build('default_colored_yellow', SHADERS_PATH / 'webgpu' / 'unlit.wgsl')

    material1 = WebGPUMaterialLib().build('M_Yellow_Simple', MaterialData('default_colored_yellow', []))

    assert program1 != None and material1 != None

    material1_variation_1 = WebGPUMaterialLib().build('M_Yellow_Simple_Var', MaterialData('default_colored_yellow', []))

    assert material1 != material1_variation_1
    
    assert material1.name == material1_variation_1.name
    assert material1.data.textures == material1_variation_1.data.textures
    assert material1.shader_module == material1_variation_1.shader_module
    assert material1.shader_params == material1_variation_1.shader_params

    assert WebGPUMaterialLib().get('M_Yellow_Simple') != WebGPUMaterialLib().get('M_Yellow_Simple_Var')

    program2 = WebGPUShaderLib().build('default_mesh', SHADERS_PATH / 'webgpu' / 'lit_blinn_phong.wgsl')

    WebGPUTextureLib().build('white_texture', TextureData(image_bytes=0xffffffff.to_bytes(4, byteorder='big'), width=1, height=1))
    WebGPUTextureLib().build('uoc_logo', TextureData(TEXTURES_PATH / 'uoc_logo.png'))

    blinn_phong_material1 = WebGPUMaterialLib().build('M_Bilnn-Phong1', MaterialData('default_mesh', ['white_texture']))
    blinn_phong_material2 = WebGPUMaterialLib().build('M_Bilnn-Phong2', MaterialData('default_mesh', ['uoc_logo']))

    assert blinn_phong_material1 != blinn_phong_material2
    assert blinn_phong_material1.data.textures != blinn_phong_material2.data.textures
    assert blinn_phong_material1.shader_module == blinn_phong_material2.shader_module == program2
    assert blinn_phong_material1.shader_params == blinn_phong_material2.shader_params
