from setuptools import setup, find_packages

setup(
    name='velez',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'pick',
        'boto3',
        'python-hcl2'
    ],
    entry_points={
        'console_scripts': [
            'velez=velez.velez:main',
        ],
    },
)
