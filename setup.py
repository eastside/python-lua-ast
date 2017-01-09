from setuptools import find_packages
from setuptools import setup

REQUIREMENTS = [
    'pyparsing==2.1.3'
]

setup(
    name = "python-lua-ast",
    version = "0.0.3",
    author = "Tomasz Rybarczyk",
    author_email = "paluho@gmail.com",
    description = ("A Lua parser/printer"),
    license = "BSD",
    keywords = "lua parser printer",
    scripts=[],
    packages=find_packages(exclude=['tests']),
    install_requires=REQUIREMENTS,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
