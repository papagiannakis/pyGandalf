from pyGandalf.core.application import Application
from pyGandalf.core.webgpu_window import WebGPUWindow

from pyGandalf.renderer.webgpu_renderer import WebGPURenderer

from pyGandalf.scene.scene import Scene
from pyGandalf.scene.components import *
from pyGandalf.scene.scene_manager import SceneManager

from pyGandalf.utilities.logger import logger

"""
Showcase of a basic empty scene with just a background color.
"""

def main():
    # Set the logger DEBUG to report all the logs
    logger.setLevel(logger.DEBUG)

    # Create a new application
    Application().create(WebGPUWindow('Empty Scene', 1280, 720, True), WebGPURenderer)

    # Set the clear color
    WebGPURenderer().set_clear_color(glm.vec4(0.25, 0.25, 0.25, 1.0))

    # Create a new scene
    scene = Scene('Empty')

    # Add scene to manager
    SceneManager().add_scene(scene)

    # Start application
    Application().start()

if __name__ == "__main__":
    main()