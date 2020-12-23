# -*- coding: utf-8 -*-
from distutils.core import setup


version = "0.0.0"

setup(
    name="expect",
    packages=["expect"],
    version=version,
    description="Mocking API and function calls in Python - inspired by Ruby's RSpec-Mocks.",
    url="https://github.com/tcassou/expect",
    download_url=f"https://github.com/tcassou/expect/archive/{version}.tar.gz",
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
