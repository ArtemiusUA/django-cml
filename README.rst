===
CML
===

CML is a reusable Django app for data exchange in CommerceML 2 standard.

Detailed documentation is in the "docs" directory.

Requirements
------------

- Python 2.7
- Django 1.8, 1.9

Quick start
-----------

1. Install using pip::

    pip install django-cml

Or clone the repo and add to your PYTHONPATH::

    git clone https://github.com/ArtemiusUA/django-cml.git

2. Add "cml" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'cml',
    ]

3. Include the cml URLconf in your project urls.py like this::

    url(r'^cml/', include('cml.urls')),

4. Run `python manage.py migrate` to create the cml models.

5. Create a cml-pipelines.py file with 'python manage.py cmlpipelines' and add it to settings file like this::

    CML_PROJECT_PIPELINES = 'project.cml_pipelines'

6. Modify pipeline objects for your needs to stack this with your models
