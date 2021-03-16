from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from codecs import open
from os import path

class Tox(TestCommand):

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        tox.cmdline(args=args)

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='jsonstreams',
    version='0.6.0',
    description='A JSON streaming writer',
    long_description=long_description,
    url='https://github.com/dcbaker/jsonstreams',
    author='Dylan Baker',
    author_email='dylan@pnwbakers.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Developers',
    ],
    install_requires=[
        'six',
    ],
    extras_require={
        ':python_version < "3.4"': ['enum34'],
        'recomended': [
            'simplejson',
        ],
        'test': [
            'tox',
        ]
    },
    package_data={
        '': ['*pyi'],
    },
    keywords='JSON stream',
    packages=['jsonstreams'],
    cmdclass={'test': Tox},
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*",
)
