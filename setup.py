from setuptools import setup, find_packages

setup(
    name='cloudopser',
    version='0.1.0',
    py_modules=['cloudopser'],
    packages=find_packages(),
    install_requires=[
        'pick',
    ],
    entry_points={
        'console_scripts': [
            'cloudopser=cloudopser:main',
        ],
    },
)
