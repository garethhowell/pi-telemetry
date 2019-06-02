
# -*- coding: utf-8 -*-
"""A Raspberry Pi telemetry module

See https://www.github.com/garethhowell/pi-telemetry
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
	name='pi-telemetry',
	version ='0.0.1',
	description = 'A Raspberry Pi telemetry module',
	long_description = readme,
	url = 'https://www.github.com/garethhowell/pi-telemetry.git',
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
		'Programming Language :: Python :: 2 :: Only',
		'Topic :: Other/Nonlisted Topic'
	],
	keywords = 'raspbian python RaspberryPi',

	# You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
        ipackages=find_packages(where="src", exclude=['contrib', 'docs', 'tests']),
        package_dir={"": "src"},

	data_files = [
	    ('/etc', ['etc/pi-telemetry'])
        ('/etc/systemd/system', ['etc/systemd/pi-telemetry.service'])

	],
    scripts = [
        'bin/pi-telemetry'
    ]
)
