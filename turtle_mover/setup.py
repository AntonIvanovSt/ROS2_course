from setuptools import find_packages, setup

package_name = "turtle_mover"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
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
            "turtle_mover = turtle_mover.turtle_mover:main",
            "figure8 = turtle_mover.figure8:main",
            "turtle_pose_follower = turtle_mover.pose_follower:main",
        ],
    },
)
