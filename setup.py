import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="objdict_bf",
    version="0.1.17",
    author="Baptiste Ferrand",
    author_email="bferrand.maths@gmail.com",
    description="A custom wrapper object around dict that allows attribute-style access to dictionary items and support for nested JSON data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/B4PT0R/objdict",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "jsonpickle"
    ],
    python_requires='>=3.6',
)
