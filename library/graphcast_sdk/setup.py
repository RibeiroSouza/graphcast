from __future__ import annotations

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="graphcas_sdk",
    version="0.0.12",
    description="Allows people without massive GPUs to easily run graphcast on remote runpod servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["boto3", "runpod"],
    python_requires=">=3.8",
)
