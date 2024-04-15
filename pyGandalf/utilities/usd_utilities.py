from pyGandalf.scene.entity import Entity

import glm
from pxr import Usd, UsdGeom, Sdf, Gf, Vt

class USDUtilities(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(USDUtilities, cls).__new__(cls)
            cls.instance.types_map = {}
            cls.instance.type_values_map = {}
        return cls.instance
    
    def add_type_conversion(cls, python_type: type, usd_type: type):
        cls.instance.types_map[str(python_type)] = usd_type

    def add_value_conversion(cls, python_type: type, conversion_lamda):
        cls.instance.type_values_map[str(python_type)] = conversion_lamda
    
    def convert_type(cls, python_type: type) -> Sdf.ValueTypeNames | None:
        if str(python_type) in cls.instance.types_map.keys():
            return cls.instance.types_map[str(python_type)]
        return None
    
    def convert_value(cls, value):
        if str(type(value)) in cls.instance.type_values_map.keys():
            return cls.instance.type_values_map[str(type(value))](value)
        return None

USDUtilities().add_type_conversion(bool, Sdf.ValueTypeNames.Bool)
USDUtilities().add_type_conversion([bool], Sdf.ValueTypeNames.BoolArray)
USDUtilities().add_type_conversion(str, Sdf.ValueTypeNames.String)
USDUtilities().add_type_conversion([str], Sdf.ValueTypeNames.StringArray)
USDUtilities().add_type_conversion(int, Sdf.ValueTypeNames.Int)
USDUtilities().add_type_conversion([int], Sdf.ValueTypeNames.IntArray)
USDUtilities().add_type_conversion(glm.ivec2, Sdf.ValueTypeNames.Int2)
USDUtilities().add_type_conversion(glm.ivec3, Sdf.ValueTypeNames.Int3)
USDUtilities().add_type_conversion(glm.ivec4, Sdf.ValueTypeNames.Int4)
USDUtilities().add_type_conversion(float, Sdf.ValueTypeNames.Float)
USDUtilities().add_type_conversion([float], Sdf.ValueTypeNames.FloatArray)
USDUtilities().add_type_conversion(glm.vec2, Sdf.ValueTypeNames.Float2)
USDUtilities().add_type_conversion(glm.vec3, Sdf.ValueTypeNames.Float3)
USDUtilities().add_type_conversion(glm.vec4, Sdf.ValueTypeNames.Float4)
USDUtilities().add_type_conversion(glm.quat, Sdf.ValueTypeNames.Quatf)
USDUtilities().add_type_conversion(glm.mat4x4, Sdf.ValueTypeNames.Matrix4d)
USDUtilities().add_type_conversion(Entity, Sdf.ValueTypeNames.String)

def glm_ivec2_to_GfVec2i(vec2: glm.ivec2) -> Gf.Vec2i:
    return Gf.Vec2i(vec2.x, vec2.y)

def glm_ivec3_to_GfVec3i(vec3: glm.ivec3) -> Gf.Vec3i:
    return Gf.Vec3i(vec3.x, vec3.y, vec3.z)

def glm_ivec4_to_GfVec4i(vec4: glm.ivec4) -> Gf.Vec4i:
    return Gf.Vec4i(vec4.x, vec4.y, vec4.z, vec4.w)

def glm_vec2_to_GfVec2f(vec2: glm.vec2) -> Gf.Vec2f:
    return Gf.Vec2f(vec2.x, vec2.y)

def glm_vec3_to_GfVec3f(vec3: glm.vec3) -> Gf.Vec3f:
    return Gf.Vec3f(vec3.x, vec3.y, vec3.z)

def glm_vec4_to_GfVec4f(vec4: glm.vec4) -> Gf.Vec4f:
    return Gf.Vec4f(vec4.x, vec4.y, vec4.z, vec4.w)

def glm_mat4x4_to_GfMatrix4d(mat: glm.mat4x4) -> Gf.Matrix4d:
    return Gf.Matrix4d(mat[0][0],  mat[0][1],  mat[0][2],  mat[0][3],
                       mat[1][0],  mat[1][1],  mat[1][2],  mat[1][3],
                       mat[2][0],  mat[2][1],  mat[2][2],  mat[2][3],
                       mat[3][0],  mat[3][1],  mat[3][2],  mat[3][3])

def glm_quat_to_GfQuatf(quat: glm.quat) -> Gf.Quatf:
    return Gf.Quatf(quat.x, quat.y, quat.z, quat.w)

USDUtilities().add_value_conversion(bool, lambda x: x)
USDUtilities().add_value_conversion([bool], lambda x: x)
USDUtilities().add_value_conversion(str, lambda x: x)
USDUtilities().add_value_conversion([str], lambda x: x)
USDUtilities().add_value_conversion(int, lambda x: x)
USDUtilities().add_value_conversion([int], lambda x: x)
USDUtilities().add_value_conversion(float, lambda x: x)
USDUtilities().add_value_conversion([float], lambda x: x)
USDUtilities().add_value_conversion(Entity, lambda x: x.id.hex)
USDUtilities().add_value_conversion(glm.ivec2, glm_ivec2_to_GfVec2i)
USDUtilities().add_value_conversion(glm.ivec3, glm_ivec3_to_GfVec3i)
USDUtilities().add_value_conversion(glm.ivec4, glm_ivec4_to_GfVec4i)
USDUtilities().add_value_conversion(glm.vec2, glm_vec2_to_GfVec2f)
USDUtilities().add_value_conversion(glm.vec3, glm_vec3_to_GfVec3f)
USDUtilities().add_value_conversion(glm.vec4, glm_vec4_to_GfVec4f)
USDUtilities().add_value_conversion(glm.quat, glm_quat_to_GfQuatf)
USDUtilities().add_value_conversion(glm.mat4x4, glm_mat4x4_to_GfMatrix4d)