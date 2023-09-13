from setuptools import setup

from m2r import parse_from_file

long_description = parse_from_file('README.md')

setup(
    name='typesense',
    python_requires='>=3',
    version='0.17.0',
    packages=['examples', 'typesense'],
    install_requires=['requests'],
    url='https://typesense.org',
    license='Apache 2.0',
    author='Typesense',
    author_email='contact@typesense.org',
    description='Python client for Typesense, an open source and typo tolerant search engine.',
    long_description=long_description,
)
