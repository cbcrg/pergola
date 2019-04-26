#!/usr/bin/env python
#
#  Copyright (c) 2014-2019, Centre for Genomic Regulation (CRG).
#  Copyright (c) 2014-2019, Jose Espinosa-Carrasco and the respective authors.
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
from setuptools.command.install import install
from os import path, getenv
from sys import exit

PATH = path.abspath(path.split(path.realpath(__file__))[0])

# VERSION = "0.1.5"
VERSION = open("pergola/_version.py").readlines()[-1].split()[-1].strip("\"'")

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
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Scientific/Engineering :: Visualization",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ]


def can_import(modname):
    """
    Test whether a module can be imported (already installed in the system)
    
    """

    try:
        __import__(modname)
    except ImportError:
        return None
    else:
        return True


def ask(string, valid_values, default=-1, case_sensitive=False):
    """ 
    Asks for a keyborad answer 
    
    """

    v = None
    if not case_sensitive:
        valid_values = [value.lower() for value in valid_values]

    while v not in valid_values:
        v = raw_input("%s [%s]" % (string,','.join(valid_values)))

        if v == '' and default >= 0:
            v = valid_values[default]
        if not case_sensitive:
            v = v.lower()

    return v


PYTHON_DEPENDENCIES = [
    ["csv"       , "Required for reading csv input files.", 1],
    ["argparse"  , "Required to read scripts arguments", 1],
    ["numpy"     , "Required for reading arrays from Jaaba matlab files and arange.", 1],
    ["bcbio"     , "Required for reading isatab files, aka biopy-isatab", 0],
    ["scipy"     , "Required for reading Jaaba matlab files.", 0],
    ["pybedtools", "Required to create pybedtools objects from Bed, BedGraph and Gff pergola objects.", 0]]


print "Checking dependencies..."
missing = False
for mname, msg, ex in PYTHON_DEPENDENCIES:

    if not can_import(mname):
        print "  *", mname, "cannot be found in your python installation."
        print "   ->", msg

        if ex:
            missing = True
        else:
            print('\nWARNING: It is HIGHLY RECOMMENDED to install all Pergola ' +
                  'dependencies.\nThe installation will continue. try to fix '
                  'it afterwards.')

if missing:
    exit("Essential dependencies missing, please review and install.\n")

long_description = 'A library to analyze and visualize behavioral data by unlocking genomic tools'

if path.exists ("README.rst"):
    with open('README.rst') as file:
        long_description = file.read()

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches version in setup"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            exit(info)

def main():
    setup(name='pergola',
          version=VERSION,
          description='A library to analyze and visualize behavioral data by unlocking genomic tools',
          long_description= long_description,
          url='http://github.com/cbcrg/pergola',
          author='Jose Espinosa-Carrasco',
          author_email='espinosacarrascoj@gmail.com',
          license='GPLv3', #License :: OSI Approved :: GNU General Public License v3 (GPLv3)
          package_dir={'pergola': PATH + '/pergola', 'scripts': PATH + '/pergola/scripts', },
          package_data={'mypkg': ['data/sample_data/*.csv']},
          packages=['pergola', 'scripts'],
          #       scripts = ['scripts/pergola_rules.py', 'scripts/pergola_isatab.py', 'scripts/jaaba_to_pergola.py'],
          zip_safe=False,
          classifiers=TAGS,
          #       install_requires=["scipy>=0.17", "pybedtools>=0.7", "numpy>=1.10"],
          entry_points={
              'console_scripts': [
                  'pergola = scripts.pergola_rules:main',
                  'pergola_rules.py = scripts.pergola_rules:main',
                  'jaaba_to_pergola = scripts.jaaba_to_pergola:main',
                  'pergola_isatab.py = scripts.pergola_isatab:main',
              ]},
          cmdclass={
              'verify': VerifyVersionCommand,
              }
          )

if __name__ == '__main__':
    exit(main())
