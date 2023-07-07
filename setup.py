import os
import sys
from glob import glob
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyndeval",
    version="0.0.3",
    author="Sean MacAvaney",
    author_email="sean.macavaney@glasgow.ac.uk",
    description="Interface to ndeval.c",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seanmacavaney/pyndeval",
    include_package_data = True,
    packages=setuptools.find_packages(include=['pyndeval']),
    install_requires=[],
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
    ext_modules=[setuptools.Extension("_pyndeval", ["src/pyndeval.c"], extra_compile_args=['-std=c99'])],
)
