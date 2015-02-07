from distutils.core import setup
#from Cython.Build import cythonize

from setuptools import find_packages, setup
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop


requirements = [
    "nltk>=3.0.1",
    "Pyphen >= 0.9.1",
]

def _post_install():
    #Thanks to: http://blog.diffbrent.com/correctly-adding-nltk-to-your-python-package-using-setup-py-post-install-commands/
    # since nltk may have just been install
    # we need to update our PYTHONPATH
    import site
    reload(site)
    # Now we can import nltk
    import nltk
    nltk.download('punkt')

class my_install(_install):
    def run(self):
        _install.run(self)

        # the second parameter, [], can be replaced with a set of parameters if _post_install needs any
        self.execute(_post_install, [], msg="Running post install task")

class my_develop(_develop):
    def run(self):
        self.execute(noop, (self.install_lib,), msg="Running develop task")
        _develop.run(self)
        self.execute(_post_install, [], msg="Running post develop task")

setup(name='ReadabilityCalculator',
        version='0.1.0',
        author='Joao Palotti',
        author_email='joaopalotti@gmail.com',
        license='LICENSE.txt',
        install_requires=requirements,
        packages=['readcalc'],
        #package_dir = {'': '.'},
        cmdclass={'install': my_install,  # override install
                  'develop': my_develop},  # develop is used for pip install -e .
        url='http://pypi.python.org/pypi/ReadabilityCalculator/',
        description='Estimate the readability of a text, e.g., the required reading skill level to understand a text.',
        long_description=open('README.txt').read()
        #ext_modules = cythonize("readcalc.pyx")
)


#setup(
