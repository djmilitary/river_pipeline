import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime 

# Блок 1: Создание или загрузка списка данных о реках из CSV файла
try:
    river_df = pd.read_csv('river_data.csv')
except FileNotFoundError:
    river_df = pd.DataFrame(columns=['check_date', 'water_level', 'water_temp'])

# Блок 2: Получение новых данных о реке
url = 'https://allrivers.info/gauge/dubna-verbilki'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
req = requests.get(url, headers=headers)
soup = BeautifulSoup(req.text, 'lxml')

river_data = {}

date_pattern = re.compile(r'\d+\s\w+\s\d{4}\s\d{2}:\d{2}')
for item in soup.find_all('div', class_='param'):
    text = item.get_text(strip=True)
    if 'Дата проверки' in text:
        date_match = date_pattern.search(text)
        if date_match:
            river_data['check_date'] = date_match.group()
            break

water_level_pattern = re.compile(r'\d+\sсм')
for item in soup.find_all('div', class_='param'):
    text = item.get_text(strip=True)
    if 'Уровень воды' in text:
        water_level_match = water_level_pattern.search(text)
        if water_level_match:
            river_data['water_level'] = int(re.search(r'\d+', water_level_match.group()).group())
            break

for item in soup.find_all('div', class_='param'):
    text = item.get_text(strip=True)
    if 'Температура воды' in text:
        water_temp = re.search(r'-?\d+\.\d+', text)
        if water_temp:
            river_data['water_temp'] = float(water_temp.group())
            break

# Блок 3: Добавление новых данных к существующему DataFrame и сохранение в файл
river_df = pd.concat([river_df, pd.DataFrame([river_data])], ignore_index=True)
river_df.drop_duplicates(inplace=True)
river_df = river_df.dropna(subset=['check_date'])
river_df.to_csv('river_data.csv', index=False)

# Блок 4: Журнал логов
# Получаем текущую дату и время
current_date = datetime.now()

# Округляем секунды до двух цифр после запятой
formatted_date = current_date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]

# Создаем DataFrame с отформатированной датой и временем
now = pd.DataFrame({'log_date': [formatted_date]})
# Проверяем, существуют ли файл и заголовки
file_exists = os.path.isfile('river_log.csv')
if not file_exists:
    now.to_csv('river_log.csv', index=False)  # Создаем файл с заголовком
else:
    now.to_csv('river_log.csv', mode='a', header=False, index=False)  # Добавляем данные без заголовка

