import os
from setuptools import setup, find_packages

version = '0.2.0'

setup(
    name='django-pluggables',
    version=version,
    description='A design pattern for Django that allows you to build "Pluggable" Reusable Applications',
    long_description="""Django-Pluggables is a design pattern that endows reusable applications with a few additional features:

#. Applications can exist at multiple URL locations (e.g. http://example.com/foo/app/ and http://example.com/bar/app/).
#. Applications can be "parented" to other applications or objects which can then deliver specialized context information.
#. Posting form data and error handling can happen in locations that make sense to the user, as opposed to the common practice of using templatetags and standalone error or preview pages for form data processing.
#. Views and templates remain generic and reusable.""",
    author='Nowell Strite',
    author_email='nowell@strite.org',
    url='http://github.com/nowells/django-pluggables/',
    packages=find_packages(),
    zip_safe=False,
    platforms=["any"],
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
    )
