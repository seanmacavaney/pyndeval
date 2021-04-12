import os
import sys
from glob import glob
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py_ndeval",
    version="0.0.0",
    author="Sean MacAvaney",
    author_email="sean.macavaney@glasgow.ac.uk",
    description="Interface to ndeval.c",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seanmacavaney/py_ndeval",
    include_package_data = True,
    packages=setuptools.find_packages(include=['py_ndeval']),
    install_requires=[],
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
    ext_modules=[setuptools.Extension("_py_ndeval", ["src/py_ndeval.c"])],
)
