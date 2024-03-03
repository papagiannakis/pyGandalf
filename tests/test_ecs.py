import pytest

import src.utilities.math as utils

from src.scene.scene import Scene
from src.systems.transform_system import TransformSystem
from src.systems.link_system import LinkSystem
from src.scene.components import TransformComponent, InfoComponent, LinkComponent

from src.scene.scene_manager import SceneManager

def test_enroll_entity():
    scene = Scene()
    entity = scene.enroll_entity()
    assert(entity in scene.get_entities())

def test_add_component():
    scene = Scene()
    entity = scene.enroll_entity()
    scene.add_component(entity, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))
    assert(scene.has_component(entity, TransformComponent) is True)

def test_get_component():
    scene = Scene()
    entity = scene.enroll_entity()
    scene.add_component(entity, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))
    transform = scene.get_component(entity, TransformComponent)
    assert(transform is not None)

def test_remove_component():
    scene = Scene()
    entity1 = scene.enroll_entity()
    entity2 = scene.enroll_entity()
    scene.add_component(entity1, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))
    scene.add_component(entity2, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))

    transform = scene.get_component(entity1, TransformComponent)
    assert(transform is not None)

    transform_system = TransformSystem([TransformComponent])
    scene.register_system(transform_system)
    assert(len(transform_system.get_filtered_components()) == 2)
    assert(len(transform_system.get_filtered_entities()) == 2)

    scene.remove_component(entity1, TransformComponent)
    assert(scene.has_component(entity1, TransformComponent) is False)
    assert(entity1 not in transform_system.get_filtered_entities())
    assert(len(transform_system.get_filtered_components()) == 1)
    assert(len(transform_system.get_filtered_entities()) == 1)

def test_system():
    scene = Scene()

    entity1 = scene.enroll_entity()
    scene.add_component(entity1, InfoComponent('e1'))
    scene.add_component(entity1, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))
    scene.add_component(entity1, LinkComponent(None))

    entity2 = scene.enroll_entity()
    scene.add_component(entity2, InfoComponent('e2'))
    scene.add_component(entity2, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))
    scene.add_component(entity2, LinkComponent(entity1))

    entity3 = scene.enroll_entity()
    scene.add_component(entity3, InfoComponent('e3'))
    scene.add_component(entity3, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))

    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))

    transform_system : TransformSystem = scene.get_system(TransformSystem)
    assert(transform_system is not None)

    link_system : LinkSystem = scene.get_system(LinkSystem)
    assert(link_system is not None)

    entities = transform_system.get_filtered_entities()
    assert(entity1 in entities)
    assert(entity2 in entities)
    assert(entity3 in entities)

    entities = link_system.get_filtered_entities()
    assert(entity1 in entities)
    assert(entity2 in entities)
    assert(entity3 not in entities)

def test_scene():
    scene = Scene()

    entity1 = scene.enroll_entity()
    scene.add_component(entity1, InfoComponent('e1'))
    scene.add_component(entity1, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))
    scene.add_component(entity1, LinkComponent(None))

    entity2 = scene.enroll_entity()
    scene.add_component(entity2, InfoComponent('e2'))
    scene.add_component(entity2, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))
    scene.add_component(entity2, LinkComponent(entity1))

    entity3 = scene.enroll_entity()
    scene.add_component(entity3, InfoComponent('e3'))
    scene.add_component(entity3, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))

    scene.register_system(TransformSystem([TransformComponent]))
    scene.register_system(LinkSystem([LinkComponent, TransformComponent]))

    SceneManager().add_scene(scene)

    assert SceneManager().get_active_scene() is scene

def test_scene_change():
    scene1 = Scene()

    entity1 = scene1.enroll_entity()
    scene1.add_component(entity1, InfoComponent('e1'))
    scene1.add_component(entity1, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))
    scene1.add_component(entity1, LinkComponent(None))

    entity2 = scene1.enroll_entity()
    scene1.add_component(entity2, InfoComponent('e2'))
    scene1.add_component(entity2, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))
    scene1.add_component(entity2, LinkComponent(entity1))

    entity3 = scene1.enroll_entity()
    scene1.add_component(entity3, InfoComponent('e3'))
    scene1.add_component(entity3, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))

    scene1.register_system(TransformSystem([TransformComponent]))
    scene1.register_system(LinkSystem([LinkComponent, TransformComponent]))

    SceneManager().add_scene(scene1)

    assert SceneManager().get_active_scene() is scene1

    scene2 = Scene()

    entity4 = scene2.enroll_entity()
    scene2.add_component(entity4, InfoComponent('e4'))
    scene2.add_component(entity4, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))

    entity5 = scene2.enroll_entity()
    scene2.add_component(entity5, InfoComponent('e5'))
    scene2.add_component(entity5, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))

    entity6 = scene2.enroll_entity()
    scene2.add_component(entity6, InfoComponent('e6'))
    scene2.add_component(entity6, TransformComponent(utils.vec(0, 0, 0), utils.vec(0, 0, 0), utils.vec(1, 1, 1)))

    scene2.register_system(TransformSystem([TransformComponent]))

    SceneManager().add_scene(scene2)

    assert SceneManager().get_active_scene() is scene1

    SceneManager().change_scene()
    SceneManager().change_scene_deffered()

    assert SceneManager().get_active_scene() is scene2
    assert SceneManager().get_active_scene().get_system(LinkSystem) is None