import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time


fueltype_list = ['Дизель', 'Бензин', 'Газ / Бензин', 'Гібрид']
gearbox_converter = {'Автомат': 2, 'Ручна / Механіка': 1, 'Типтронік':3, 'Варіатор': 4, 'Робот': 5, }

parser_path = 'parser'
site_url = 'https://auto.ria.com/uk/car'




class AntiParserError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

        

def get_data(mark='kia', model='sorento', page_number=20, file_dir='parser'):
    data_container = []
    main_url = '{}/{}/{}/'.format(site_url, mark, model)
    for i in range(1, page_number):
        time.sleep(10)
        part_page = f'?page={i}'
        url = main_url + part_page
        response = requests.get(url)
        # Проверяем успешность запроса

        if response.status_code == 200:
            page_content = response.content
            soup = BeautifulSoup(page_content, 'html.parser')
            try:
                page_cars = soup.find('div', class_='standart-view').find_all('section', class_='ticket-item')
            except AttributeError as at:
                
                raise NameError('Parser works')
            else:
                # Проверяем, что нашли тег
                for car in page_cars:
                    time.sleep(1)
                    for_adding = {}
                    
                    year = car.find('div', class_='content').find('a', class_='address').text
                    engine_ftype_oddmeter_gearbox = car.find('ul', class_='unstyle characteristic').text                    
                    price = car.find('div', class_='price-ticket').find('span', class_=['bold size22 green', 'bold green size22']).text
                    #print(price)
                    #print(engine_ftype_oddmeter_gearbox)
                    # print(year)

                    engine_ftype_oddmeter_gearbox = engine_ftype_oddmeter_gearbox.strip()
                    if 'Електро' not in engine_ftype_oddmeter_gearbox:
                        year = year.strip()
                        price = price.strip()



                        for_adding['year'] = datetime.now().year - int(year[-4:])           #ГОД
                        for_adding['price'] = int(''.join(price.split()))                  #Цена

                        efog_lst = engine_ftype_oddmeter_gearbox.split('   ')
                        if efog_lst[0] == 'без пробігу':
                            for_adding['oddmeter'] = 0
                        else:
                            for_adding['oddmeter'] = int(efog_lst[0].split(' ')[0])*1000                          #пробег
                        work_lst = efog_lst[2].replace(',', '').split(' ')

                        if len(work_lst) < 3:
                            continue
                        elif len(work_lst) == 5:
                            for_adding['fueltype'] = ''.join(work_lst[:3])
                            for_adding['engine_V'] = float(work_lst[3])


                        else:
                            try:
                                for_adding['engine_V'] = float(work_lst[1])         #Обьем двигателя
                            except ValueError as v:
                                continue
                            else:
                                for_adding['fueltype'] = work_lst[0]         #тип топлива, не используется при обучении

                        
                        if gearbox_converter.get(efog_lst[-1]):
                            for_adding['transmission'] = gearbox_converter[efog_lst[-1]]  #Коробка передач
                        else:
                            continue                

                        data_container.append(for_adding)
                    else:
                        # raise ElectroCarError('Введена модель електрокара')
                        continue
                

                
            # Получаем содержимое страницы
        elif response.status_code == 404:
            #print('Pages are over')
            break
        else:
            print(f"Ошибка при запросе: {response.status_code}")
            raise AntiParserError('Сайт проводит технические работы, перезапустим сбор данных')

    with open(f'{file_dir}/{mark}_{model}.json', 'w') as file:
        '''Сменить на переменные'''
        json.dump(data_container, file, indent=4, ensure_ascii=False)


# try:
#     get_data(mark='tesla', model='model 3', page_number=25, file_dir='.')
# except NameError as name:
#     time.sleep(15)
#     print('restart parser')
#     get_data(mark='tesla', model='model 3', page_number=15, file_dir='.')
# except ElectroCarError as e:
#     print('right')
# finally:
#     print('Program end ')


'''

1. Год выпуска
2. Пробег
3. Обьем двигателя
4. Коробка передач (автомат 1, механика 0)
5. Тип бензина (Дизель 0, бензин 1)
6. Цена


'''
