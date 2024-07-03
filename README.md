# pyGandalf

## a **G**eometric, **AN**imation, **D**irected, **A**lgorithmic, **L**earning **F**ramework

Incorporating Geometric algebra and Animation for advanced computer graphics, Neural visual computing for GPU-based application development, using Directed acyclic graphs for efficient structure, focused on Algorithmic solutions, dedicated to Learning through an open-source Framework that leverages Entities, Components, Systems in a Shader-based Scenegraph environment using latest CG GPU-accelerated APIs.

![concept of pyGandalf][def]

[def]: ./data/images/pygandalf1.png

Copyright (c) 2024, University of Crete, Greece & ICS-FORTH, Greece

## Introduction

pyGandalf is a Python-based framework for computer graphics, visual computing in an entity-components-systems (ECS) approach. It is designed to be a flexible, modular, and extensible framework for developing advanced computer graphics applications. It is built on top of modern graphics APIs such as OpenGL and WebGPU, with an emphasis on learning, teaching and understanding of key discipline concepts.

## Features

- **Geometric**: pyGandalf is able to utilize geometric data of any kind and size and renders them effectively and with great quality.
- **Animation**: pyGandalf provides a powerful and flexible framework for developing advanced computer graphics applications. It is designed to be easy to use and easy to extend. It is designed to be a flexible, modular, and extensible framework for developing advanced computer graphics applications. It is built on top of modern graphics APIs such as OpenGL, and WebGPU and is designed to be easy to use and easy to extend.
- **Directed acyclic graphs**:  An Entity-Component-System (ECS) architecture is used to organize the data and functionality of the application into a directed acyclic graph. This allows for efficient structure and organization of the application, and provides a powerful and flexible framework for developing advanced computer graphics applications.
- **Algorithmic solutions**: Several algorithms are provided for advanced computer graphics applications. These algorithms are designed to be easy to use and easy to extend, and are built on top of modern graphics APIs such as OpenGL, and WebGPU.
- **Learning**: Emphasis is given to learning through an open-source framework that leverages Entities, Components, Systems in a Shader-based Scenegraph environment using latest CG APIs.

## Installation

1. Create a python 3.10 environment (in the code examples below named `pyGandalf`).
  1. (Recommended way): 
    1. Install [Anaconda or Miniconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) 
    2. Create a new environment: ```conda create -n pygandalf python=3.10```
    3. Activate the environment: ```conda activate pygandalf```
  2. (Alternative way):
    1. You may use any other virtual environment manager, such as venv, pipenv, or pdm.
2. Install the pyGandalf package from the root directory (the one containining the `setup.py`) by running ```pip install -e .``` in the activated environment
  1. This will install the package in editable mode, so you can modify the code and see the changes immediately (make sure to run the command often, if you restructure the folders).

## Usage

TBD

## Testing

- **After selecting the python interpreter in VSCode**, go to ```View > Command Palette```.
- Select ```Python: Configure Tests```.
- Select ```pytest``` and then ```. (Root Directory)```


## Project Structure

```
├── data                                <- Data for the github README
├── LICENSE
├── pyGandalf                           <- The Source Code
│   ├── core                            
│   │   ├── application.py              <- The Application Class
│   │   ├── base_window.py              <- The BaseWindow Class
│   │   ├── event_manager.py            <- The EventManager Class
│   │   ├── events.py                   <- The EventType and Event Class
│   │   ├── input_manager.py            <- Input management
│   │   └── opengl_window.py            <- Window management using GLFW
│   ├── examples                        <- Examples of all kind
│   │   └── OpenGL                      <- Examples using OpenGL
│   ├── renderer
│   │   ├── base_renderer.py            <- BaseRenderer Class
│   │   └── opengl_renderer.py          <- OpenGLRenderer
│   ├── resources
│   │   ├── models                      <- Model files (obj,etc)
│   │   ├── shaders                     <- Shader files (glsl, etc)
│   │   └── textures                    <- Texture files (jpg, png, etc)
│   ├── scene
│   │   ├── components.py               <- All kinds of Components
│   │   ├── entity.py                   <- Entity Class
│   │   ├── scene.py                    <- The Scene Class
│   │   └── scene_manager.py            <- Scene management Class
│   ├── systems
│   │   ├── camera_system.py            <- A Camera System
│   │   ├── light_system.py             <- A Light System 
│   │   ├── link_system.py              <- System for scene hierarchy
│   │   ├── opengl_rendering_system.py  <- System for static mesh rendering
│   │   ├── system.py                   <- The System Class 
│   │   └── transform_system.py         <- System for Transformations
│   └── utilities                       <- Utilities for anything
│       ├── definitions.py              <- PATH shortcuts 
│       ├── logger.py                   <- Custom logger 
│       ├── math.py                     <- Math related functions
│       ├── opengl_material_lib.py      <- Material related classes
│       ├── opengl_mesh_lib.py          <- Mesh related classes       
│       ├── opengl_shader_lib.py        <- Shader related classes
│       └── opengl_texture_lib.py       <- Texture related classes
├── tests
│   ├── test_ecs.py                     <- Tests involving the entity component system
│   ├── test_components.py              <- Tests involving the components
│   └── test_utility_libs.py            <- Tests involving the utility libs
├── README.md
├── setup.cfg                           <- Optional configuration options
└── setup.py                            <- Setup configuration 
``` 


## Documentation

TBD

## License

Apache 2.0 License (see LICENSE file)

## Contributors

- [George Papagiannakis](https://george.papagiannakis.org)
- [John Petropoulos](https://github.com/johnoyo)
- [Stratos Geronikolakis](https://github.com/stratosger)
- [Manos Kamarianakis](https://github.com/kamarianakis)
- [Antonis Protopsaltis](https://github.com/aprotopsaltis)
