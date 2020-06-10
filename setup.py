
# -*- coding: utf-8 -*-
"""A Raspberry Pi telemetry module

See https://www.github.com/garethhowell/pitelemetry
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
import sys

sys.path.insert(0, 'src')
from pitelemetry import __version__

def readme():
    with open('README.rst') as f:
        return f.read()

with open('LICENSE') as f:
    license = f.read()


setup(
    name='pitelemetry',
    version =__version__,
    description = 'Collect data from 1-wire sensors connected to Raspberry Pi and send via mqtt',
    long_description = readme(),
    long_description_content_type = 'text/x-rst',
    url = 'https://www.github.com/garethhowell/pitelemetry.git',
    author = 'Gareth Howell',
    author_email = 'gareth.howell@gmail.com',
    license = license,
    classifiers = [
		# How mature is this project? Common values are
    	#   3 - Alpha
    	#   4 - Beta
    	#   5 - Production/Stable
	'Development Status :: 3 - Alpha',
	'Intended Audience :: Other Audience',
	'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
		'Topic :: Other/Nonlisted Topic',
        'Operating System :: Raspbian'
	],
    keywords = 'raspbian python RaspberryPi',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires= [
        'paho-mqtt>=1.5.0',
#        'RPi.GPIO>=0.7.0',
        'keyboard',
        'PyYAML>=5.1.2',
        'requests'
        ],
    data_files = [
	    ('/etc', ['etc/pitelemetry.yaml.example']),
        ('/etc/systemd/system', ['etc/systemd/pitelemetry.service'])
	],
    scripts = [
        'src/pitelemetry.py'
    ]
)
