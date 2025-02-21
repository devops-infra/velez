from setuptools import setup, find_packages

setup(
    name='velez',
    version='0.1.0',
    py_modules=['velez', 'terragrunt_ops'],
    install_requires=[
        'pick',
    ],
    entry_points={
        'console_scripts': [
            'velez=velez:main',
        ],
    },
)