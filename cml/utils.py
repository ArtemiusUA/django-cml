# -*- coding: utf-8 -
from __future__ import absolute_import
import os
import logging
import importlib
from io import BytesIO
import six
try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from .items import *
from .conf import settings

logger = logging.getLogger(__name__)


class ImportManager(object):

    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = None
        self.item_processor = ItemProcessor()

    def import_all(self):
        try:
            self.tree = self._get_tree()
        except Exception:
            logger.error('Import all error!')
            return
        self.import_classifier()
        self.import_catalogue()
        self.import_offers_pack()
        self.import_orders()
        logger.info('Import success!')

    def _get_tree(self):
        if self.tree is not None:
            return self.tree
        if not os.path.exists(self.file_path):
            message = 'File not found {}'.format(self.file_path)
            logger.error(message)
            raise OSError(message)
        try:
            tree = ET.parse(self.file_path)
        except Exception as e:
            message = 'File parse error {}'.format(self.file_path)
            logger.error(message)
            raise e
        return tree

    def _get_cleaned_text(self, element):
        try:
            text = element.text
        except:
            text = u''
        if text is None:
            return u''
        return text.strip(u' ')

    def import_classifier(self):
        try:
            tree = self._get_tree()
        except Exception:
            logger.error('Import classifier error!')
            return
        classifier_element = tree.find(u'Классификатор')
        if classifier_element is not None:
            self._parse_groups(classifier_element)
            self._parse_properties(classifier_element)

    def _parse_groups(self, current_element, parent_item=None):
        for group_element in current_element.findall(u'Группы/Группа'):
            group_item = Group(group_element)
            group_item.id = self._get_cleaned_text(group_element.find(u'Ид'))
            group_item.name = self._get_cleaned_text(group_element.find(u'Наименование'))
            if parent_item is not None:
                parent_item.groups.append(group_item)
            self._parse_groups(group_element, group_item)
            # processing only top level groups
            if parent_item is None:
                self.item_processor.process_item(group_item)

    def _parse_properties(self, current_element):
        for property_element in current_element.findall(u'Свойства/Свойство'):
            property_item = Property(property_element)
            property_item.id = self._get_cleaned_text(property_element.find(u'Ид'))
            property_item.name = self._get_cleaned_text(property_element.find(u'Наименование'))
            property_item.value_type = self._get_cleaned_text(property_element.find(u'ТипЗначений'))
            property_item.for_products = self._get_cleaned_text(property_element.find(u'ДляТоваров')) == u'true'
            self.item_processor.process_item(property_item)
            for variant_element in property_element.findall(u'ВариантыЗначений/{}'.format(property_item.value_type)):
                variant = PropertyVariant(variant_element)
                variant.id = self._get_cleaned_text(variant_element.find(u'ИдЗначения'))
                variant.value = self._get_cleaned_text(variant_element.find(u'Значение'))
                variant.property_id = property_item.id
                self.item_processor.process_item(variant)

    def import_catalogue(self):
        try:
            tree = self._get_tree()
        except Exception:
            logger.error('Import catalogue error!')
            return
        catalogue_element = tree.find(u'Каталог')
        if catalogue_element is not None:
            self._parse_products(catalogue_element)

    def _parse_products(self, current_element):
        for product_element in current_element.findall(u'Товары/Товар'):
            product_item = Product(product_element)
            product_item.id = self._get_cleaned_text(product_element.find(u'Ид'))
            product_item.name = self._get_cleaned_text(product_element.find(u'Наименование'))

            sku_element = product_element.find(u'БазоваяЕдиница')
            if sku_element is not None:
                sku_item = Sku(sku_element)
                sku_item.id = sku_element.get(u'Код')
                sku_item.name_full = sku_element.get(u'НаименованиеПолное')
                sku_item.international_abbr = sku_element.get(u'МеждународноеСокращение')
                sku_item.name = self._get_cleaned_text(sku_element)
                product_item.sku_id = sku_item.id
                self.item_processor.process_item(sku_item)

            image_element = product_element.find(u'Картинка')
            if image_element is not None:
                image_text = self._get_cleaned_text(image_element)
                try:
                    image_filename = os.path.basename(image_text)
                except Exception:
                    image_filename = u''
                if image_filename:
                    product_item.image_path = os.path.join(settings.CML_UPLOAD_ROOT, image_filename)

            for group_id_element in product_element.findall(u'Группы/Ид'):
                product_item.group_ids.append(self._get_cleaned_text(group_id_element))

            for property_element in product_element.findall(u'ЗначенияСвойств/ЗначенияСвойства'):
                property_id = self._get_cleaned_text(property_element.find(u'Ид'))
                property_variant_id = self._get_cleaned_text(property_element.find(u'Значение'))
                if property_variant_id:
                    product_item.properties.append((property_id, property_variant_id))

            for tax_element in product_element.findall(u'СтавкиНалогов/СтавкаНалога'):
                tax_item = Tax(tax_element)
                tax_item.name = self._get_cleaned_text(tax_element.find(u'Наименование'))
                try:
                    tax_item.value = Decimal(self._get_cleaned_text(tax_element.find(u'Ставка')))
                except:
                    tax_item.value = Decimal()
                self.item_processor.process_item(tax_item)
                product_item.tax_name = tax_item.name

            for additional_field_element in product_element.findall(u'ЗначенияРеквизитов/ЗначениеРеквизита'):
                additional_field = AdditionalField(additional_field_element)
                additional_field.name = self._get_cleaned_text(additional_field_element.find(u'Наименование'))
                additional_field.value = self._get_cleaned_text(additional_field_element.find(u'Значение'))
                product_item.additional_fields.append(additional_field)

            self.item_processor.process_item(product_item)

    def import_offers_pack(self):
        try:
            tree = self._get_tree()
        except Exception:
            logger.error('Import offers pack error!')
            return
        offers_pack_element = tree.find(u'ПакетПредложений')
        if offers_pack_element is not None:
            self._parse_price_types(offers_pack_element)
            self._parse_offers(offers_pack_element)

    def _parse_price_types(self, current_element):
        for price_type_element in current_element.findall(u'ТипыЦен/ТипЦены'):
            price_type_item = PriceType(price_type_element)
            price_type_item.id = self._get_cleaned_text(price_type_element.find(u'Ид'))
            price_type_item.name = self._get_cleaned_text(price_type_element.find(u'Наименование'))
            price_type_item.currency = self._get_cleaned_text(price_type_element.find(u'Валюта'))
            price_type_item.tax_name = self._get_cleaned_text(price_type_element.find(u'Налог/Наименование'))
            if self._get_cleaned_text(price_type_element.find(u'Налог/УчтеноВСумме')) == u'true':
                price_type_item.tax_in_sum = True
            self.item_processor.process_item(price_type_item)

    def _parse_offers(self, current_element):
        for offer_element in current_element.findall(u'Предложения/Предложение'):
            offer_item = Offer(offer_element)
            offer_item.id = self._get_cleaned_text(offer_element.find(u'Ид'))
            offer_item.name = self._get_cleaned_text(offer_element.find(u'Наименование'))

            sku_element = offer_element.find(u'БазоваяЕдиница')
            if sku_element is not None:
                sku_item = Sku(sku_element)
                sku_item.id = sku_element.get(u'Код')
                sku_item.name_full = sku_element.get(u'НаименованиеПолное')
                sku_item.international_abbr = sku_element.get(u'МеждународноеСокращение')
                sku_item.name = self._get_cleaned_text(sku_element)
                offer_item.sku_id = sku_item.id
                self.item_processor.process_item(sku_item)

            for price_element in offer_element.findall(u'Цены/Цена'):
                price_item = Price(price_element)
                price_item.representation = self._get_cleaned_text(price_element.find(u'Представление'))
                price_item.price_type_id = self._get_cleaned_text(price_element.find(u'ИдТипаЦены'))
                price_item.price_for_sku = Decimal(self._get_cleaned_text(price_element.find(u'ЦенаЗаЕдиницу')))
                price_item.currency_name = self._get_cleaned_text(price_element.find(u'Валюта'))
                price_item.sku_name = self._get_cleaned_text(price_element.find(u'Единица'))
                price_item.sku_ratio = Decimal(self._get_cleaned_text(price_element.find(u'Коэффициент')))
                offer_item.prices.append(price_item)

            self.item_processor.process_item(offer_item)

    def import_orders(self):
        try:
            tree = self._get_tree()
        except Exception:
            logger.error('Import orders error!')
            return
        orders_elements = tree.find(u'Документ')
        if orders_elements is not None:
            self._parse_orders(orders_elements)

    def _parse_orders(self, order_elements):
        for order_element in order_elements:
            order_item = Order(order_element)
            order_item.id = self._get_cleaned_text(order_element.find(u'Ид'))
            order_item.number = self._get_cleaned_text(order_element.find(u'Номер'))
            order_item.date = self._get_cleaned_text(order_element.find(u'Дата'))
            order_item.currency_name = self._get_cleaned_text(order_element.find(u'Валюта'))
            order_item.currency_rate = self._get_cleaned_text(order_element.find(u'Курс'))
            order_item.operation = self._get_cleaned_text(order_element.find(u'ХозОперация'))
            order_item.role = self._get_cleaned_text(order_element.find(u'Роль'))
            order_item.sum = self._get_cleaned_text(order_element.find(u'Сумма'))
            order_item.client.id = self._get_cleaned_text(order_element.find(u'Контрагенты/Контрагент/Ид'))
            order_item.client.name = self._get_cleaned_text(order_element.find(u'Контрагенты/Контрагент/Наименование'))
            order_item.client.full_name = self._get_cleaned_text(
                                          order_element.find(u'Контрагенты/Контрагент/ПолноеНаименование'))
            order_item.time = self._get_cleaned_text(order_element.find(u'Время'))
            order_item.comment = self._get_cleaned_text(order_element.find(u'Комментарий'))
            item_elements = order_element.find(u'Товары/Товар')
            if item_elements is not None:
                for item_element in item_elements:
                    order_item_item = OrderItem(item_element)
                    order_item_item.id = self._get_cleaned_text(item_element.find(u'Ид'))
                    order_item_item.name = self._get_cleaned_text(item_element.find(u'Наименование'))
                    sku_element = item_element.find(u'БазоваяЕдиница')
                    if sku_element is not None:
                        order_item_item.sku.id = sku_element.get(u'Код')
                        order_item_item.sku.name = self._get_cleaned_text(sku_element)
                        order_item_item.sku.name_full = sku_element.get(u'НаименованиеПолное')
                        order_item_item.sku.international_abbr = sku_element.get(u'МеждународноеСокращение')
                    order_item_item.price = self._get_cleaned_text(item_element.find(u'ЦенаЗаЕдиницу'))
                    order_item_item.quant = self._get_cleaned_text(item_element.find(u'Количество'))
                    order_item_item.sum = self._get_cleaned_text(item_element.find(u'Сумма'))
                    order_item.items.append(order_item_item)
            additional_field_elements = order_element.find(u'ЗначенияРеквизитов/ЗначениеРеквизита')
            if additional_field_elements is not None:
                for additional_field_element in additional_field_elements:
                    additional_field_item = AdditionalField(additional_field_element)
                    additional_field_item.name = self._get_cleaned_text(item_element.find(u'Наименование'))
                    additional_field_item.value = self._get_cleaned_text(item_element.find(u'Значение'))
            self.item_processor.process_item(order_item)


class ExportManager(object):

    def __init__(self):
        self.item_processor = ItemProcessor()
        self.root = ET.Element(u'КоммерческаяИнформация')
        self.root.set(u'ВерсияСхемы', '2.05')
        self.root.set(u'ДатаФормирования', six.text_type(datetime.now().date()))

    def get_xml(self):
        f = BytesIO()
        tree = ET.ElementTree(self.root)
        tree.write(f, encoding='windows-1251', xml_declaration=True)
        return f.getvalue()

    def export_all(self):
        self.export_orders()

    def export_orders(self):
        for order in self.item_processor.yield_item(Order):
            order_element = ET.SubElement(self.root, u'Документ')
            ET.SubElement(order_element, u'Ид').text = six.text_type(order.id)
            ET.SubElement(order_element, u'Номер').text = six.text_type(order.number)
            ET.SubElement(order_element, u'Дата').text = six.text_type(order.date.strftime('%Y-%m-%d'))
            ET.SubElement(order_element, u'Время').text = six.text_type(order.time.strftime('%H:%M:%S'))
            ET.SubElement(order_element, u'ХозОперация').text = six.text_type(order.operation)
            ET.SubElement(order_element, u'Роль').text = six.text_type(order.role)
            ET.SubElement(order_element, u'Валюта').text = six.text_type(order.currency_name)
            ET.SubElement(order_element, u'Курс').text = six.text_type(order.currency_rate)
            ET.SubElement(order_element, u'Сумма').text = six.text_type(order.sum)
            ET.SubElement(order_element, u'Комментарий').text = six.text_type(order.comment)
            clients_element = ET.SubElement(order_element, u'Контрагенты')
            client_element = ET.SubElement(clients_element, u'Контрагент')
            ET.SubElement(client_element, u'Ид').text = six.text_type(order.client.id)
            ET.SubElement(client_element, u'Наименование').text = six.text_type(order.client.name)
            ET.SubElement(client_element, u'Роль').text = six.text_type(order.client.role)
            ET.SubElement(client_element, u'ПолноеНаименование').text = six.text_type(order.client.full_name)
            ET.SubElement(client_element, u'Фамилия').text = six.text_type(order.client.last_name)
            ET.SubElement(client_element, u'Имя').text = six.text_type(order.client.first_name)
            address_element = ET.SubElement(clients_element, u'АдресРегистрации')
            ET.SubElement(clients_element, u'Представление').text = six.text_type(order.client.address)
            products_element = ET.SubElement(order_element, u'Товары')
            for order_item in order.items:
                product_element = ET.SubElement(products_element, u'Товар')
                ET.SubElement(product_element, u'Ид').text = six.text_type(order_item.id)
                ET.SubElement(product_element, u'Наименование').text = six.text_type(order_item.name)
                sku_element = ET.SubElement(product_element, u'БазоваяЕдиница ')
                sku_element.set(u'Код', order_item.sku.id)
                sku_element.set(u'НаименованиеПолное', order_item.sku.name_full)
                sku_element.set(u'МеждународноеСокращение', order_item.sku.international_abbr)
                sku_element.text = order_item.sku.name
                ET.SubElement(product_element, u'ЦенаЗаЕдиницу').text = six.text_type(order_item.price)
                ET.SubElement(product_element, u'Количество').text = six.text_type(order_item.quant)
                ET.SubElement(product_element, u'Сумма').text = six.text_type(order_item.sum)

    def flush(self):
        self.item_processor.flush_pipeline(Order)


class ItemProcessor(object):

    def __init__(self):
        self._project_pipelines = {}
        self._load_project_pipelines()

    def _load_project_pipelines(self):
        try:
            pipelines_module_name = settings.CML_PROJECT_PIPELINES
        except AttributeError:
            logger.info('Configure CML_PROJECT_PIPELINES in settings!')
            return
        try:
            pipelines_module = importlib.import_module(pipelines_module_name)
        except ImportError:
            return
        for item_class_name in PROCESSED_ITEMS:
            try:
                pipeline_class = getattr(pipelines_module, '{}Pipeline'.format(item_class_name))
            except AttributeError:
                continue
            self._project_pipelines[item_class_name] = pipeline_class()

    def _get_project_pipeline(self, item_class):
        item_class_name = item_class.__name__
        return self._project_pipelines.get(item_class_name, False)

    def process_item(self, item):
        project_pipeline = self._get_project_pipeline(item.__class__)
        if project_pipeline:
            try:
                project_pipeline.process_item(item)
            except Exception as e:
                logger.error('Error processing of item {}: {}'.format(item.__class__.__name__, repr(e)))

    def yield_item(self, item_class):
        project_pipeline = self._get_project_pipeline(item_class)
        if project_pipeline:
            try:
                return project_pipeline.yield_item()
            except Exception as e:
                logger.error('Error yielding item {}: {}'.format(item_class.__name__, repr(e)))
                return []
        return []

    def flush_pipeline(self, item_class):
        project_pipeline = self._get_project_pipeline(item_class)
        if project_pipeline:
            try:
                project_pipeline.flush()
            except Exception as e:
                logger.error('Error flushing pipeline for item {}: {}'.format(item_class.__name__, repr(e)))
