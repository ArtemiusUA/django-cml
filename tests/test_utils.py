# -*- coding: utf-8 -
from __future__ import absolute_import
import os
import six
from six.moves import range
try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET
from django.test import TestCase
from cml.utils import ImportManager, ExportManager
from cml.items import *

FIXTURES_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), 'tests_fixtures'))


class ImportManagerTestCase(TestCase):

    def setUp(self):
        pass

    def test_run(self):
        man = ImportManager(os.path.join(FIXTURES_PATH, 'import.xml'))
        man.import_all()
        self.assertTrue(GroupPipeline.collected_items)


class ExportManagerTestCase(TestCase):

    def setUp(self):
        pass

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
        for i in range(10):
            item = Order()
            item.id = six.text_type(i)
            item.number = six.text_type(i)
            item.currency_name = six.text_type(i)
            item.date = datetime.now()
            item.currency_rate = Decimal(i)
            item.sum = Decimal(i)
            yield item

