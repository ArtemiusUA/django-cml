import os
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.conf import settings

DEFAULT_FILE_NAME = 'cml_pipelines.py'


class Command(BaseCommand):
    help = 'Creates a template file with project cml pipelines'
    args = ['file']

    def handle(self, file_name=None, **options):
        project_name = os.path.basename(os.getcwd())
        dst = file_name is not None and file_name or DEFAULT_FILE_NAME
        if os.path.exists(dst):
            raise CommandError('Error: file "%s" already exists' % dst)
        open(dst, 'w').write(render_to_string('cml/cml-pipelines.txt', {
            'project': project_name,
            'file': os.path.basename(dst).split('.')[0]
        }))
        self.stdout.write('"%s" written.' % os.path.join(dst))
