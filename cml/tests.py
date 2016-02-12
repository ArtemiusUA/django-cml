# -*- coding: utf-8 -
import os
try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET
from django.test import TestCase
from django.conf import settings
from .utils import ImportManager, ExportManager
from .items import *

FIXTURES_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), 'tests_fixtures'))


class ImportManagerTestCase(TestCase):

    def setUp(self):
        settings.CML_PROJECT_PIPELINES = 'cml.tests'

    def test_run(self):
        man = ImportManager(os.path.join(FIXTURES_PATH, 'import.xml'))
        man.import_all()
        self.assertTrue(GroupPipeline.collected_items)


class ExportManagerTestCase(TestCase):

    def setUp(self):
        settings.CML_PROJECT_PIPELINES = 'cml.tests'

    def test_run(self):
        man = ExportManager()
        man.export_all()
        tree = ET.fromstring(man.get_xml())
        orders_elements = tree.find(u'Документ')
        self.assertIsNotNone(orders_elements)


class GroupPipeline(object):

    collected_items = []

    def process_item(self, item):
        GroupPipeline.collected_items.append(item)


class OrderPipeline(object):

    def process_item(self, item):
        pass

    def yield_item(self):
        for i in xrange(10):
            item = Order()
            item.id = unicode(i)
            item.number = unicode(i)
            item.currency_name = unicode(i)
            item.date = datetime.now()
            item.currency_rate = Decimal(i)
            item.sum = Decimal(i)
            yield item

