#!/usr/bin/env python
#
#  Copyright (c) 2014-2016, Centre for Genomic Regulation (CRG).
#  Copyright (c) 2014-2016, Jose Espinosa-Carrasco and the respective authors.
#
#  This file is part of Pergola.
#
#  Pergola is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pergola is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Pergola.  If not, see <http://www.gnu.org/licenses/>.

# from distutils.core import setup
from setuptools import setup
from os import path

PATH = path.abspath(path.split(path.realpath(__file__))[0])

# "Operating System :: Microsoft :: Windows",
TAGS = [
    "Development Status :: 2 - Pre-Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Other Audience",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    "Operating System :: MacOS",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
    "Topic :: Scientific/Engineering :: Visualization",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ]

setup(name='pergola',
      version='0.4',
      description='A library to analyze and visualize behavioral data by unlocking genomic tools ',
      long_description= open('README.md').read(),
      url='http://github.com/cbcrg/pergola',
      author='Jose Espinosa-Carrasco',
      author_email='espinosacarrascoj@gmail.com',
      license='GNU General Public License 3.0',
      package_dir = {'pergola': PATH + '/pergola', 'scripts': PATH + '/pergola/scripts',},
      package_data={'mypkg': ['data/sample_data/*.csv']},
      packages=['pergola', 'scripts'], 
#       scripts = ['scripts/pergola_rules.py', 'scripts/pergola_isatab.py', 'scripts/jaaba_to_pergola.py'],      
      zip_safe=False,
      classifiers = TAGS,
      entry_points={
        'console_scripts': [
            'pergola = scripts.pergola_rules:main',
            'pergola_rules.py = scripts.pergola_rules:main',            
            'jaaba_to_pergola = scripts.jaaba_to_pergola:main',  
            'pergola_isatab.py = scripts.pergola_isatab:main',            
        ]}
      )

# mandatory package to add are argparse