#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

version = "0.1.5"

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

requirements = [
    "click>=7.1",
    "xlrd>=1.2.0"
]

setup(
    name='sqlgen',
    version=version,
    description=(
        'Infers SQL DDL (Data Definition Language) from template file'
    ),
    long_description=readme,
    long_description_content_type='text/markdown',
    author='wangzhiwei',
    author_email='wangzhiwei@bertadata.com',
    url='http://git.qixin007.com/zhiwei/sqlgen',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=requirements,
    license=None,
    zip_safe=False,
    keywords=[
        "sqlgen",
        "Python",
        "MySQL",
        "DDL",
    ],
    entry_points={
        'console_scripts': ['sqlgen = sqlgen.__main__:main']
    },
)
