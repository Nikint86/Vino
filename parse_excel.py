from collections import defaultdict
import pandas as pd
from pprint import pprint

df = pd.read_excel('wine2.xlsx', sheet_name='Лист1')

products = defaultdict(list)

for index, row in df.iterrows():
    product = {
        'Название': row['Название'],
        'Сорт': row['Сорт'] if pd.notna(row['Сорт']) else '',
        'Цена': row['Цена'],
        'Картинка': row['Картинка']
    }

    products[row['Категория']].append(product)

print("Продукция на винодельне Розы:")
print("=" * 50)
pprint(dict(products)) 