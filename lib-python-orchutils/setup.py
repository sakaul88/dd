#!/usr/bin/env python
from setuptools import setup
from setuptools import find_packages

setup(
    name='p2paas-orchutils',
    version='1.0.0',
    description='Infrastructure orchestration utilities for P2PaaS',
    author='Alan Byrne',
    author_email='alan.byrne@ie.ibm.com',
    url='https://github.ibm.com/WCE-SaaS-Ops/lib-python-orchutils',
    packages=find_packages(exclude=['scripts', '*.tests', '*.tests.*']),
    include_package_data=True,
    license="Apache License 2.0",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    install_requires=[
        'hvac',
        'jinja2',
        'semver',
        'six',
        'softlayer==5.8.0',  # Remove version when we no longer support Py2
        'p2paas-baseutils'
    ],
)
