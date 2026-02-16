import pandas as pd
from pprint import pprint
import math

df = pd.read_excel('wine2.xlsx', sheet_name='Лист1')

products = {}

for index, row in df.iterrows():
    category = row['Категория']

    product = {
        'Название': row['Название'],
        'Сорт': row['Сорт'] if pd.notna(row['Сорт']) else '',
        'Цена': row['Цена'],
        'Картинка': row['Картинка']
    }

    if category not in products:
        products[category] = []

    products[category].append(product)


print("=" * 50)
pprint(products)