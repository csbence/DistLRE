from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='distlre',
    version='0.0.1',
    description='A Python package to distribute commands on remote hosts via'
                'SSH and to execute them locally in parallel.',
    long_description=long_description,
    url='https://github.com/csbence/DistLRE',
    author='Bence Cserna',
    packages=find_packages(),
    install_requires=['paramiko']
)
