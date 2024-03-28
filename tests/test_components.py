from pyGandalf.scene.components import *

def test_InfoComponent():
    info = InfoComponent()
    assert info.tag == 'UnnamedEntity'
    assert info.enabled == True
    custom_info = InfoComponent('Name')
    assert custom_info.tag == 'Name'

def test_TransformComponent():
    translation = glm.vec3(1.0, 2.0, 3.0)
    rotation = glm.vec3(0.0, 0.0, 0.0)
    scale = glm.vec3(1.0, 1.0, 1.0)
    transform = TransformComponent(translation, rotation, scale)
    assert np.allclose(transform.translation, translation)
    assert np.allclose(transform.rotation, rotation)
    assert np.allclose(transform.scale, scale)
    assert np.allclose(transform.local_matrix, glm.mat4(1.0))
    assert np.allclose(transform.world_matrix, glm.mat4(1.0))
    assert np.allclose(transform.quaternion, glm.quat())
    assert transform.is_dirty == True
    assert transform.is_static == False

def test_LinkComponent():
    parent_entity = Entity()
    link_component = LinkComponent(parent_entity)
    assert link_component.parent == parent_entity
    assert link_component.prev_parent == parent_entity
    assert link_component.children == []

def test_MaterialComponent():
    material_name = "TestMaterial"
    color = glm.vec3(0.5, 0.5, 0.5)
    material = MaterialComponent(material_name, color)
    assert material.name == material_name
    assert np.allclose(material.color, color)
    assert material.glossiness == 5.0
    assert material.metallicness == 0.0

def test_CameraComponent():
    camera = CameraComponent(45.0, 16/9, 0.1, 100.0, 1.0, CameraComponent.Type.PERSPECTIVE)
    assert camera.fov == 45.0
    assert camera.aspect_ratio == 16/9
    assert camera.near == 0.1
    assert camera.far == 100.0
    assert camera.zoom_level == 1.0
    assert camera.type == CameraComponent.Type.PERSPECTIVE

    camera = CameraComponent(45.0, 16/9, 0.1, 100.0, 1.0, CameraComponent.Type.ORTHOGRAPHIC)
    assert camera.fov == 45.0
    assert camera.aspect_ratio == 16/9
    assert camera.near == 0.1
    assert camera.far == 100.0
    assert camera.zoom_level == 1.0
    assert camera.type == CameraComponent.Type.ORTHOGRAPHIC

def test_StaticMeshComponent():
    mesh_name = "TestMesh"
    mesh = StaticMeshComponent(mesh_name)
    assert mesh.name == mesh_name
    assert mesh.attributes == None
    assert mesh.indices == None
    assert mesh.vao == 0
    assert mesh.vbo == []
    assert mesh.ebo == 0
    assert mesh.batch == -1

def test_LightComponent():
    light_color = glm.vec3(1.0, 1.0, 1.0)
    light_intensity = 0.8
    light = LightComponent(light_color, light_intensity)
    assert np.allclose(light.color, light_color)
    assert light.intensity == light_intensity
    assert light.static == True