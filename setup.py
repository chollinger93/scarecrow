import setuptools

with open("./README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="otter-in-a-suit",
    version="0.2",
    author="Christian Hollinger",
    author_email="christian@chollinger.com",
    description="A Raspberry Pi powered edge-computing camera setups that runs a Tensorflow object detection model to determine whether a person is on the camera and plays loud audio to scare them off.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/otter-in-a-suit/scarecrow",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GNU :: GPLv3",
        "Operating System :: Linux",
    ],
    python_requires='>=3.6',
)