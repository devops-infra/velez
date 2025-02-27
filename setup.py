from setuptools import setup, find_packages

setup(
    name='velez',
    version='0.2.1',
    packages=find_packages(),
    install_requires=[
        'pick',
        'boto3',
        'python-hcl2',
        'PyGithub'
    ],
    entry_points={
        'console_scripts': [
            'velez=velez.velez:main',
        ],
    },
)
