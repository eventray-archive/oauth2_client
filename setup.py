#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name="oauth2_client"
    , version="0.9"
    , description="Library for OAuth version 2 'Bearer Token'"
    , author="John Anderson"
    , author_email="sontek@gmail.com"
    , url="http://github.com/eventray/oauth2_client"
    , packages = find_packages()
    , license = "MIT License"
    , keywords="oauth"
    , zip_safe = True
    , classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
)
