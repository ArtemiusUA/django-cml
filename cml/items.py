# -*- coding: utf-8 -
from __future__ import absolute_import
from decimal import Decimal
from datetime import datetime

PROCESSED_ITEMS = ('Group', 'PropertyVariant', 'Property', 'PropertyVariant', 'Sku', 'Tax', 'Product', 'Offer', 'Order')


class BaseItem(object):

    def __init__(self, xml_element=None):
        self.xml_element = xml_element


class Group(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)
        self.id = u''
        self.name = u''
        self.groups = []


class Property(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Property, self).__init__(*args, **kwargs)
        self.id = u''
        self.name = u''
        self.value_type = u''
        self.for_products = False


class PropertyVariant(BaseItem):

    def __init__(self, *args, **kwargs):
        super(PropertyVariant, self).__init__(*args, **kwargs)
        self.id = u''
        self.value = u''
        self.property_id = u''


class Sku(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Sku, self).__init__(*args, **kwargs)
        self.id = u''
        self.name = u''
        self.name_full = u''
        self.international_abbr = u''


class Tax(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Tax, self).__init__(*args, **kwargs)
        self.name = u''
        self.value = Decimal()


class AdditionalField(BaseItem):

    def __init__(self, *args, **kwargs):
        super(AdditionalField, self).__init__(*args, **kwargs)
        self.name = u''
        self.value = u''


class Product(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        self.id = u''
        self.name = u''
        self.sku_id = u''
        self.group_ids = []
        self.properties = []
        self.tax_name = u''
        self.image_path = u''
        self.additional_fields = []


class PriceType(BaseItem):

    def __init__(self, *args, **kwargs):
        super(PriceType, self).__init__(*args, **kwargs)
        self.id = u''
        self.name = u''
        self.currency = u''
        self.tax_name = u''
        self.tax_in_sum = False


class Price(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Price, self).__init__(*args, **kwargs)
        self.representation = u''
        self.price_type_id = u''
        self.price_for_sku = Decimal()
        self.currency_name = u''
        self.sku_name = u''
        self.sku_ratio = Decimal()


class Offer(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Offer, self).__init__(*args, **kwargs)
        self.id = u''
        self.name = u''
        self.sku_id = u''
        self.prices = []


class Client(BaseItem):

    def __init__(self):
        self.id = u''
        self.name = u''
        self.role = u'Покупатель'
        self.full_name = u''
        self.first_name = u''
        self.last_name = u''
        self.address = u''


class OrderItem(BaseItem):

    def __init__(self):
        self.id = u''
        self.name = u''
        self.sku = Sku(None)
        self.price = Decimal()
        self.quant = Decimal()
        self.sum = Decimal()


class Order(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        self.id = u''
        self.number = u''
        self.date = datetime.now().date()
        self.currency_name = u''
        self.currency_rate = Decimal()
        self.operation = u'Заказ товара'
        self.role = u'Продавец'
        self.sum = Decimal()
        self.client = Client()
        self.time = datetime.now().time()
        self.comment = u''
        self.items = []
        self.additional_fields = []
