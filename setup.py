from setuptools import setup, find_packages
from os import path


this_directory = path.abspath(path.dirname(__file__))

version = {}
with open(path.join(this_directory, "src", "albert", "__version__.py"), "r") as f:
    version = f.read().split("=")[1].strip().replace('"', "")


setup(
    name="albert",
    version=version,
    author="Albert Invent",
    author_email="support@albertinvent.com",
    description="A Python SDK for interacting with the Albert API",
    long_description=open("README.md").read(),
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    long_description_content_type="text/markdown",
    url="https://github.com/MoleculeEngineering/albert_api",
    install_requires=["pandas==2.2.2", "pydantic==2.8.2"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
