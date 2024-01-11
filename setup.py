from setuptools import find_packages, setup

VERSION = '1.0.0'


setup(
    name='simple_asgi_server',
    version=VERSION,
    packages=find_packages(),
    package_dir={'simple_asgi_server': 'asgi_server'},
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/MercyClassic/simple_asgi_server',
    author='MercyClassic',
    requires=[],
)
