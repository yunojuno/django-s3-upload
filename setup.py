import codecs
import os

from setuptools import setup, find_packages, Command

version = '0.2.1'

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with codecs.open(os.path.join(here, 'requirements.txt')) as f:
    install_requires = [line for line in f.readlines() if not line.startswith('#')]


class VersionCommand(Command):
    description = 'print library version'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print(version)


setup(
    author="YunoJuno",
    author_email='code@yunojuno.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    cmdclass={'version': VersionCommand},
    description='Integrates direct client-side uploading to s3 with Django',
    include_package_data=True,
    install_requires=install_requires,
    keywords='aws s3 tools django',
    license='MIT',
    long_description=long_description,
    name='django-s3-upload',
    packages=find_packages(exclude=['docs', 'tests*']),
    url='https://github.com/yunojuno/django-s3-upload',
    version=version,
)
