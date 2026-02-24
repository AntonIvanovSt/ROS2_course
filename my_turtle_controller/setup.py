from setuptools import find_packages, setup

package_name = 'my_turtle_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='ivanov.ant.st@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    entry_points={
        'console_scripts': [
            'turtle_mover = my_turtle_controller.turtle_mover:main',
            'turtle_figure8 = my_turtle_controller.turtle_figure8:main',
            'turtle_pose_follower = my_turtle_controller.turtle_pose_follower:main',
        ],
    },
)
