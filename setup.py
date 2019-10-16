import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-cml',
    python_requires='>3.3.0',
    version='0.4.0',
    packages=['cml'],
    install_requires=['Django>=2.0', 'django-appconf>=1.0.1', 'six>=1.12.0'],
    include_package_data=True,
    license='BSD License',
    description='App for data exchange in CommerceML 2 standard..',
    long_description=README,
    url='https://github.com/ArtemiusUA/django-cml',
    author='Artem Merkulov',
    author_email='artem.merkulov@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
