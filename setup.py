from setuptools import setup

setup(
    name='ofx',
    version='0.1',
    py_modules=['ofx'],
    install_requires=[
        'Click',
        'sh',
        'simplejson'

    ],
    entry_points='''
        [console_scripts]
        ofx=ofx:cli
    ''',
)