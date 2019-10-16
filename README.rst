===
CML
===

CML is a reusable Django app for data exchange in CommerceML 2 standard.

Requirements
------------

- Python 3.3, 3.4, 3.5, 3.6
- Django 2.x

Quick start
-----------

Install using pip::

    pip install django-cml

Or clone the repo and add to your `PYTHONPATH`::

    git clone https://github.com/ArtemiusUA/django-cml.git

Add "cml" to your `INSTALLED_APPS` setting like this::

    INSTALLED_APPS = [
        ...
        'cml',
    ]

Include the cml URLconf in your project `urls.py` like this::

    re_path(r'^cml/', include('cml.urls')),

Run `python manage.py migrate` to create the cml models.

Create a `cml-pipelines.py` file with `python manage.py cmlpipelines` and add it to settings file like this::

    CML_PROJECT_PIPELINES = 'project.cml_pipelines'

Modify pipeline objects for your needs to stack this with your models.
