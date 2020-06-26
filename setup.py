import setuptools
from setuptools.command.install import install
import subprocess
import os
import sys

class ShellInstall(install):
    def run(self):
        if not sys.platform.startswith("linux"):
            print('Your platform {} might not be supported'.format(sys.platform))
        subprocess.call(['./sbin/install_tensorflow_models.sh'])
        #subprocess.call(['./sbin/install_vidgear.sh']) # Switched to vidgear=0.1.8 stable
        install.run(self)

with open("./README.md", "r") as fh:
    long_description = fh.read()

with open('scarecrow_server/requirements.txt') as f:
    requirements_server = f.read().splitlines()

with open('scarecrow_client/requirements.txt') as f:
    requirements_client = f.read().splitlines()
# Combine server and client
requirements = requirements_client + requirements_server

setuptools.setup(
    cmdclass={'install': ShellInstall},
    name="scarecrow-cam",
    version="0.4",
    author="Christian Hollinger",
    author_email="christian@chollinger.com",
    description="A Raspberry Pi powered edge-computing camera setups that runs a Tensorflow object detection model to determine whether a person is on the camera and plays loud audio to scare them off.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chollinger93/scarecrow",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GNU :: GPLv3",
        "Operating System :: Linux",
    ],
    entry_points={
        'console_scripts': [
            'scarecrow_server = scarecrow_server.server.receiver:start',
            'scarecrow_client = scarecrow_client.client.sender:start',
        ]
    },
    python_requires='>=3.6',
)
