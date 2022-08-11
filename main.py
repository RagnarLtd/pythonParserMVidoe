import json
import math

import requests
import os
from config import cookies, headers


def get_data(asked_id):
    """
    Запрос на сайт Мвидео для получения данных о запрашиваемом продукте
    :param asked_id: int
    :return: boolean
    """

    params = {
        'categoryId': asked_id,
        'offset': '0',
        'limit': '24',
        'filterParams': [
            'WyJza2lka2EiLCIiLCJkYSJd',
            'WyJ0b2xrby12LW5hbGljaGlpIiwiIiwiZGEiXQ==',
        ],
        'doTranslit': 'true',
    }

    if not os.path.exists('result'):
        os.mkdir('result')

    sess = requests.Session()
    response = sess.get('https://www.mvideo.ru/bff/products/listing',
                        params=params,
                        cookies=cookies,
                        headers=headers).json()
    total_items = response.get('body').get('total')
    if total_items != 0:
        pages = math.ceil(total_items / 24)

        ids = {}
        description = {}
        prices = {}

        for number in range(pages):
            offset = f'{number * 24}'
            params = {
                'categoryId': asked_id,
                'offset': offset,
                'limit': '24',
                'filterParams': [
                    'WyJza2lka2EiLCIiLCJkYSJd',
                    'WyJ0b2xrby12LW5hbGljaGlpIiwiIiwiZGEiXQ==',
                ],
                'doTranslit': 'true',
            }
            response = sess.get('https://www.mvideo.ru/bff/products/listing',
                                params=params,
                                cookies=cookies,
                                headers=headers).json()
            ids_list = response.get('body').get('products')
            ids[number] = ids_list
            json_data = {
                'productIds': ids_list,
                'mediaTypes': [
                    'images',
                ],
                'category': True,
                'status': True,
                'brand': True,
                'propertyTypes': [
                    'KEY',
                ],
                'propertiesConfig': {
                    'propertiesPortionSize': 5,
                },
                'multioffer': False,
            }

            response = sess.post('https://www.mvideo.ru/bff/product-details/list',
                                 cookies=cookies,
                                 headers=headers,
                                 json=json_data).json()
            description[number] = response

            ids_str = ','.join(ids_list)
            params = {
                'productIds': ids_str,
                'addBonusRubles': 'true',
                'isPromoApplied': 'true',
            }

            response = sess.get('https://www.mvideo.ru/bff/products/prices',
                                params=params,
                                cookies=cookies,
                                headers=headers).json()
            material_prices = response.get('body').get('materialPrices')
            for item in material_prices:
                item_id = item.get('price').get('productId')
                base_price = item.get('price').get('basePrice')
                sale_price = item.get('price').get('salePrice')

                prices[item_id] = {
                    'base_price': base_price,
                    'sale_price': sale_price
                }

        for items in description.values():
            products = items.get('body').get('products')

            for item in products:
                item_id = item.get('productId')
                if item_id in prices:
                    item_prices = prices[item_id]
                    item['base_price'] = item_prices.get('base_price')
                    item['sale_price'] = item_prices.get('sale_price')
                    item['link'] = f'https://www.mvideo.ru/products/{item.get("nameTranslit")}-{item_id}'
        with open('result/result.json', 'w') as file:
            json.dump(description, file, indent=4, ensure_ascii=False)
        return True
    else:
        return False
