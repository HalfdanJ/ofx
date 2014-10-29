from setuptools import setup
from setuptools import find_packages
from distutils.core import setup

setup(
    name='ofx',
    description='Commandline tool for managing addons in OpenFrameworks',
    author="Jonas Jongejan",
    author_email="ofx@halfdanj.dk",
    url="https://github.com/HalfdanJ/ofx",
    download_url='https://github.com/HalfdanJ/ofx/tarball/0.1',
    version='0.1',
    py_modules=['ofx'],
    install_requires=[
        'Click',
        'sh',
        'simplejson'
    ],
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities'

    ],
    entry_points='''
        [console_scripts]
        ofx=ofx:cli
    '''

)
