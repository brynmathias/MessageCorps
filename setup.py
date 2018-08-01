import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


links = []
required = []
with open('./requirements.txt') as f:
    for line in f:
        if "git" in line:
            links.append(line)
        else:
            required.append(line)

print("we are building ", links, required)


def __path(filename):
    return os.path.join(os.path.dirname(__file__), filename)


version = "0.0.1"
print(version)

try:
    version = read("./VERSION").strip()
except:
    pass


setup(
    name="MessageCorps",
    version=version,
    author="Bryn Mathias",
    author_email="brynmathias@gmail.com",
    description=(""),
    license="BSD",
    packages=find_packages(),
    install_requires=required,
    dependency_links=links,
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities"
    ],
)
