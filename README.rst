===
CML
===

CMS is an app for data exchange in CommerceML 2 standard.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "cml" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'cml',
    ]

2. Include the cml URLconf in your project urls.py like this:

    url(r'^cml/', include('cml.urls')),

3. Run `python manage.py migrate` to create the cml models.

4. Create a cml-pipelines.py file and add it to settings file like this:

    CML_PROJECT_PIPELINES = 'project.cml_pipelines'

5. Modify pipeline objects for your needs to stack this with your models
