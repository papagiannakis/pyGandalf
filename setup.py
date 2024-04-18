from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyGandalf',
    version="0.2.0",
    license='Apache-2.0', 
    description = "The pyGandalf project",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author = "George Papagiannakis", 
    author_email = "papagian@csd.uoc.gr",
    maintainer='John Petropoulos',
    maintainer_email='johnaipeia@gmail.com',
    url='https://github.com/papagiannakis/pyGandalf',
    keywords = ['ECS','Scenegraph','Python design patterns','Computer Graphics'],
    package_dir={'pyGandalf':'pyGandalf'},
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "numpy>=1.26.4",
        "glfw>=2.7.0",
        "PyOpenGL>=3.1.7",
        "pillow>=10.2.0",
        "pytest>=8.0.2",
        "PyGLM>=2.7.1",
        "trimesh>=4.2.0",
        "scipy>=1.12.0",
        "imgui-bundle>=1.3.0",
        "usd-core>=24.3",
        "jsonpickle>=3.0.4",
    ],    

    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.10",
    ],
    project_urls={
        "Homepage" : "https://github.com/papagiannakis/pyGandalf",
        "Source" : "https://github.com/papagiannakis/pyGandalf",
    },

    python_requires=">=3.10",

)


