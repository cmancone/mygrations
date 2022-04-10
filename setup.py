"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mygrations',
    version='1.0.1',
    description='A general purpose migration tool for managing MySQL updates',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cmancone/mygrations',
    author='Conor Mancone',
    author_email='cmancone@gmail.com',
    license='MIT',
    download_url='https://github.com/cmancone/mygrations/archive/v1.0.0.tar.gz',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='setuptools development migrations mysql',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires=">=3.6",
    install_requires=[
        'PyMySQL',
    ],
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # data_files=[('/usr/local/bin', ['mygrate.py'])],
)
