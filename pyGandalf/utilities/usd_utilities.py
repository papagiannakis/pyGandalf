from pyGandalf.scene.entity import Entity

import glm
from pxr import Usd, UsdGeom, Sdf, Gf, Vt

python_types_to_usd = {
    "<class 'bool'>": Sdf.ValueTypeNames.Bool,
    "<class 'str'>": Sdf.ValueTypeNames.String,
    "<class 'int'>": Sdf.ValueTypeNames.Int,
    "<class 'glm.ivec2'>": Sdf.ValueTypeNames.Int2,
    "<class 'glm.ivec3'>": Sdf.ValueTypeNames.Int3,
    "<class 'glm.ivec4'>": Sdf.ValueTypeNames.Int4,
    "<class 'float'>": Sdf.ValueTypeNames.Float,
    "<class 'glm.vec2'>": Sdf.ValueTypeNames.Float2,
    "<class 'glm.vec3'>": Sdf.ValueTypeNames.Float3,
    "<class 'glm.vec4'>": Sdf.ValueTypeNames.Float4,
    "<class 'glm.quat'>": Sdf.ValueTypeNames.Quatf,
    "<class 'glm.mat4x4'>": Sdf.ValueTypeNames.Matrix4d,
    "<class 'pyGandalf.scene.entity.Entity'>": Sdf.ValueTypeNames.String,
}

def convert_type_to_usd(python_type: str) -> Sdf.ValueTypeNames | None:
    if python_type in python_types_to_usd.keys():
        return python_types_to_usd[python_type]
    return None

def get_or_covert_to_usd_type(attribute):
    match attribute:
        case bool():
            return attribute
        case str():
            return attribute
        case int():
            return attribute
        case float():
            return attribute
        case glm.ivec2():
            return glm_vec2_to_GfVec2i(attribute)
        case glm.ivec3():
            return glm_vec3_to_GfVec3i(attribute)
        case glm.ivec4():
            return glm_vec4_to_GfVec4i(attribute)
        case glm.vec2():
            return glm_vec2_to_GfVec2f(attribute)
        case glm.vec3():
            return glm_vec3_to_GfVec3f(attribute)
        case glm.vec4():
            return glm_vec4_to_GfVec4f(attribute)
        case glm.mat4x4():
            return glm_mat4x4_to_GfMatrix4d(attribute)
        case glm.quat():
            return glm_quat_to_GfQuatf(attribute)
        case Entity():
            return attribute.id.hex

def glm_vec2_to_GfVec2i(vec2: glm.ivec2) -> Gf.Vec2i:
    return Gf.Vec2i(vec2.x, vec2.y)

def glm_vec3_to_GfVec3i(vec3: glm.ivec3) -> Gf.Vec3i:
    return Gf.Vec3i(vec3.x, vec3.y, vec3.y)

def glm_vec4_to_GfVec4i(vec4: glm.ivec4) -> Gf.Vec4i:
    return Gf.Vec4i(vec4.x, vec4.y, vec4.y, vec4.z)

def glm_vec2_to_GfVec2f(vec2: glm.vec2) -> Gf.Vec2f:
    return Gf.Vec2f(vec2.x, vec2.y)

def glm_vec3_to_GfVec3f(vec3: glm.vec3) -> Gf.Vec3f:
    return Gf.Vec3f(vec3.x, vec3.y, vec3.y)

def glm_vec4_to_GfVec4f(vec4: glm.vec4) -> Gf.Vec4f:
    return Gf.Vec4f(vec4.x, vec4.y, vec4.y, vec4.z)

def glm_mat4x4_to_GfMatrix4d(mat: glm.mat4x4) -> Gf.Matrix4d:
    return Gf.Matrix4d(mat[0][0],  mat[0][1],  mat[0][2],  mat[0][3],
                       mat[1][0],  mat[1][1],  mat[1][2],  mat[1][3],
                       mat[2][0],  mat[2][1],  mat[2][2],  mat[2][3],
                       mat[3][0],  mat[3][1],  mat[3][2],  mat[3][3])

def glm_quat_to_GfQuatf(quat: glm.quat) -> Gf.Quatf:
    return Gf.Quatf(quat.x, quat.y, quat.z, quat.w)
