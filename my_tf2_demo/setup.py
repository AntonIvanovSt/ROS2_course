import os
from glob import glob
from setuptools import find_packages, setup

package_name = "my_tf2_demo"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="user",
    maintainer_email="ivanov.ant.st@gmail.com",
    description="TODO: Package description",
    license="TODO: License declaration",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "spawn_second_turtle = my_tf2_demo.spawn_second_turtle:main",
            "turtle_tf2_broadcaster = my_tf2_demo.turtle_tf2_broadcaster:main",
            "turtle_tf2_listener = my_tf2_demo.turtle_tf2_listener:main",
        ],
    },
)
