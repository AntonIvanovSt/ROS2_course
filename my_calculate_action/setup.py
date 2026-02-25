from setuptools import find_packages, setup

package_name = 'my_calculate_action'

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
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'calculate_action_server = my_calculate_action.calculate_action_server:main',
            'calculate_action_client = my_calculate_action.calculate_action_client:main',
            'turtle_action_server = my_calculate_action.turtle_action_server:main',
            'turtle_action_client = my_calculate_action.turtle_action_client:main',
            'number_publisher = my_calculate_action.publisher_node:main',
        ],
    },
)
