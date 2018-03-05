from setuptools import setup

from m2r import parse_from_file

long_description = parse_from_file('README.md')

setup(
    name='typesense',
    version='0.2.6',
    packages=['examples', 'typesense'],
    install_requires=['requests'],
    url='https://typesense.org',
    license='Apache 2.0',
    author='Typesense',
    author_email='contact+typesense@wreally.com',
    description='Python client for Typesense, an open source and typo tolerant search engine.',
    long_description=long_description,
)
