from distutils.core import setup
#from Cython.Build import cythonize

from setuptools import find_packages, setup
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop


requirements = [
    "nltk>=3.0.1",
    "Pyphen >= 0.9.1",
    "justext >= 2.2.0",
    "beautifulsoup4 >= 4.5.0",
]

setup(name='ReadabilityCalculator',
        version='0.2.36',
        author='Joao Palotti',
        author_email='joaopalotti@gmail.com',
        license='LICENSE.txt',
        install_requires=requirements,
        packages=['readcalc'],
        url='http://pypi.python.org/pypi/ReadabilityCalculator/',
        description='Estimate the readability of a text, e.g., the required reading skill level to understand a text.',
        long_description=open('README.txt').read()
        #ext_modules = cythonize("readcalc.pyx")
)

