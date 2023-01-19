# -*- coding: utf-8 -*-
from distutils.core import setup


version = "1.2.3"
name = "expectise"

setup(
    name=name,
    packages=[name],
    version=version,
    description="Mocking API and function calls in Python - inspired by Ruby's RSpec-Mocks.",
    url=f"https://github.com/tcassou/{name}",
    download_url=f"https://github.com/tcassou/{name}/archive/{version}.tar.gz",
    keywords=["python", "testing", "mocking", "unit", "tests"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: Mocking",
    ],
    install_requires=[],
)
