
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

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
	name='pitelemetry',
	version =__version__,
	description = 'Collect data from 1-wire sensors connected to Raspberry Pi and send via mqtt',
	long_description = readme,
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
        'paho-mqtt',
        'RPi.GPIO',
        'keyboard',
        'PyYAML'
        ],
    data_files = [
	    ('/etc', ['etc/pitelemetry.yaml', 'etc/pitelemetry_logging.yaml']),
        ('/etc/systemd/system', ['etc/systemd/pitelemetry.service'])
	],
    scripts = [
        'bin/pitelemetry'
    ]
)
