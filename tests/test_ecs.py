import pytest

from pyGandalf.scene.scene import Scene
from pyGandalf.systems.transform_system import TransformSystem
from pyGandalf.systems.link_system import LinkSystem
from pyGandalf.scene.components import TransformComponent, InfoComponent, LinkComponent

from pyGandalf.scene.scene_manager import SceneManager

import glm

def test_enroll_entity():
    scene = Scene()
    entity = scene.enroll_entity()
    assert(entity in scene.get_entities())

def test_add_component():
    scene = Scene()
    entity = scene.enroll_entity()
    scene.add_component(entity, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    assert scene.has_component(entity, TransformComponent) is True

def test_get_component():
    scene = Scene()
    entity = scene.enroll_entity()
    scene.add_component(entity, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    transform = scene.get_component(entity, TransformComponent)
    assert transform is not None

def test_remove_component():
    scene = Scene()
    entity1 = scene.enroll_entity()
    entity2 = scene.enroll_entity()
    scene.add_component(entity1, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity2, TransformComponent(glm.vec3(2, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))

    transform = scene.get_component(entity1, TransformComponent)
    assert transform is not None

    transform_system = TransformSystem([TransformComponent])
    scene.register_system(transform_system)
    assert len(transform_system.get_filtered_components()) == 2
    assert len(transform_system.get_filtered_entities()) == 2

    scene.remove_component(entity1, TransformComponent)
    
    assert scene.has_component(entity1, TransformComponent) is False
    assert entity1 not in transform_system.get_filtered_entities()
    assert len(transform_system.get_filtered_components()) == 1
    assert len(transform_system.get_filtered_entities()) == 1
    assert transform not in transform_system.get_filtered_components()

    transform2 = scene.get_component(entity2, TransformComponent)
    assert transform2 != None and transform2.translation == glm.vec3(2, 0, 0)

def test_destroy_entity():
    scene = Scene()

    entity1 = scene.enroll_entity()
    scene.add_component(entity1, InfoComponent('e1'))
    transform1 = scene.add_component(entity1, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    link1 = scene.add_component(entity1, LinkComponent(None))

    entity2 = scene.enroll_entity()
    scene.add_component(entity2, InfoComponent('e2'))
    transform2 = scene.add_component(entity2, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    link2 = scene.add_component(entity2, LinkComponent(entity1))

    entity3 = scene.enroll_entity()
    scene.add_component(entity3, InfoComponent('e3'))
    transform3 = scene.add_component(entity3, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))

    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))

    SceneManager().add_scene(scene)

    scene.get_system(TransformSystem).on_create_base()
    scene.get_system(LinkSystem).on_create_base()

    scene.destroy_entity(entity1)

    assert entity2 not in scene.get_entities() and entity1 not in scene.get_entities()
    assert entity3 in scene.get_entities()

    assert entity1 not in scene.get_system(TransformSystem).get_filtered_entities()
    assert entity2 not in scene.get_system(TransformSystem).get_filtered_entities()

    assert entity1 not in scene.get_system(LinkSystem).get_filtered_entities()
    assert entity2 not in scene.get_system(LinkSystem).get_filtered_entities()

    assert entity3 in scene.get_system(TransformSystem).get_filtered_entities()

    for components in scene.get_system(TransformSystem).get_filtered_components():
        assert transform1 not in components
        assert transform2 not in components

    for components in scene.get_system(LinkSystem).get_filtered_components():
        assert link1 not in components
        assert link2 not in components

    for components in scene.get_system(TransformSystem).get_filtered_components():
        assert transform3 in components

def test_system():
    scene = Scene()

    entity1 = scene.enroll_entity()
    scene.add_component(entity1, InfoComponent('e1'))
    scene.add_component(entity1, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity1, LinkComponent(None))

    entity2 = scene.enroll_entity()
    scene.add_component(entity2, InfoComponent('e2'))
    scene.add_component(entity2, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity2, LinkComponent(entity1))

    entity3 = scene.enroll_entity()
    scene.add_component(entity3, InfoComponent('e3'))
    scene.add_component(entity3, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))

    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))

    transform_system : TransformSystem = scene.get_system(TransformSystem)
    assert(transform_system is not None)

    link_system : LinkSystem = scene.get_system(LinkSystem)
    assert(link_system is not None)

    entities = transform_system.get_filtered_entities()
    assert entity1 in entities 
    assert entity2 in entities
    assert entity3 in entities

    entities = link_system.get_filtered_entities()
    assert entity1 in entities
    assert entity2 in entities
    assert entity3 not in entities

def test_scene():
    scene = Scene()

    entity1 = scene.enroll_entity()
    scene.add_component(entity1, InfoComponent('e1'))
    scene.add_component(entity1, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity1, LinkComponent(None))

    entity2 = scene.enroll_entity()
    scene.add_component(entity2, InfoComponent('e2'))
    scene.add_component(entity2, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene.add_component(entity2, LinkComponent(entity1))

    entity3 = scene.enroll_entity()
    scene.add_component(entity3, InfoComponent('e3'))
    scene.add_component(entity3, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))

    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))

    SceneManager().add_scene(scene)

    assert SceneManager().get_active_scene() is scene

    SceneManager().clean()

def test_scene_change():
    scene1 = Scene()

    entity1 = scene1.enroll_entity()
    scene1.add_component(entity1, InfoComponent('e1'))
    scene1.add_component(entity1, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene1.add_component(entity1, LinkComponent(None))

    entity2 = scene1.enroll_entity()
    scene1.add_component(entity2, InfoComponent('e2'))
    scene1.add_component(entity2, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))
    scene1.add_component(entity2, LinkComponent(entity1))

    entity3 = scene1.enroll_entity()
    scene1.add_component(entity3, InfoComponent('e3'))
    scene1.add_component(entity3, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))

    scene1.register_system(TransformSystem([TransformComponent]))
    scene1.register_system(LinkSystem([LinkComponent, TransformComponent]))

    SceneManager().add_scene(scene1)

    assert SceneManager().get_active_scene() is scene1

    scene2 = Scene()

    entity4 = scene2.enroll_entity()
    scene2.add_component(entity4, InfoComponent('e4'))
    scene2.add_component(entity4, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))

    entity5 = scene2.enroll_entity()
    scene2.add_component(entity5, InfoComponent('e5'))
    scene2.add_component(entity5, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))

    entity6 = scene2.enroll_entity()
    scene2.add_component(entity6, InfoComponent('e6'))
    scene2.add_component(entity6, TransformComponent(glm.vec3(0, 0, 0), glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)))

    scene2.register_system(TransformSystem([TransformComponent]))

    SceneManager().add_scene(scene2)

    assert SceneManager().get_active_scene() is scene1

    SceneManager().change_scene()
    SceneManager().change_scene_deffered()

    assert SceneManager().get_active_scene() is scene2
    assert SceneManager().get_active_scene().get_system(LinkSystem) is None

    SceneManager().clean()