import datetime
from vk_api.longpoll import VkEventType

from sql_ORM import Session, write_db
from app import get_token, VBot, VKinder

vkinder = VKinder(token=get_token(False))
vbot = VBot(token=get_token(True))
users={}

def search_users(sex, age, city, user_id):
    response = vkinder.user_search(sex, age, city)
    # оставляем кандидатов с открытой страницей
    if response['count'] > 0:
        session = Session()
        open_items = [item for item in response['items'] if item['is_closed'] == False]
        count_users = 0
        #  берем трёх кандидатов из фильтрованного списка и формируем набор данных
        for item in open_items:
            if write_db(user_id=user_id, user_search=item['id'], session=session):
                message = f'''{item['first_name']} {item['last_name']} \n https://vk.com/id{str(item['id'])}'''
                attachment = ','.join(vkinder.photo_search(item['id']))
                vbot.write_msg(user_id, message, attachment)
                count_users += 1
                if count_users == 3:
                    break
    else:
        vbot.write_msg(user_id, 'Партнеры не найдены...')

for event in vbot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request.lower() in ['привет', 'hi', 'start', 'начать', 'ок', 'пуск']:
                # Получаем данные о пользователе - пол, город, дату рождения. На основании этих данных будем строить поиск.
                users = vkinder.get_user_data(user_id=event.user_id)
                users = users[0]

                if len(users.get('bdate', '0')) > 5:
                   users['age'] = (int(datetime.datetime.now().year) - int(users['bdate'][-4:]))

                if users.get('city', '0') == '0':
                    vbot.write_msg(event.user_id, message = "Укажите ваш город")
                elif users.get('age', '0') == '0':
                    vbot.write_msg(event.user_id, message = "Укажите ваш возраст")
                else:
                    vbot.write_msg(event.user_id, message = "Начинаю поиск партнеров. Подождите пару секунд...")
                    search_users(users['sex'], users['age'], users['city']['id'], user_id=event.user_id)

            # Получаем недостающие данные
            elif not request == 'hi' and users.get('id') == event.user_id:
                if users.get('city', '0') == '0':
                    cities = vkinder.city_search(request)           # Находим город
                    if cities.get('count') == 0:
                        vbot.write_msg(event.user_id, 'Не могу найти такой город, попробуйте ввести еще раз, либо укажите ближайший крупный город.')
                    else:
                       #  Берем первый город в списке. Надо бы сделать перебор регионов для правильности...
                        city = cities.get('items')[0]
                        users['city'] = {'id': city.get('id'), 'title': city.get('title')}
                        if users.get('age', '0') == '0':
                            vbot.write_msg(event.user_id, message = 'Укажите ваш возраст')
                        else:
                            vbot.write_msg(event.user_id, message = 'Начинаю поиск партнеров. Подождите пару секунд...')
                            search_users(users['sex'], users['age'], users['city']['id'], user_id=event.user_id)

                elif users.get('age', '0') == '0':
                    if request.isdigit():
                        users['age'] = request
                        vbot.write_msg(event.user_id, 'Начинаю поиск партнеров. Подождите пару секунд...')
                        search_users(users['sex'], users['age'], users['city']['id'], user_id=event.user_id)
                    else:
                        vbot.write_msg(event.user_id, 'Введите возраст цифрами.')
                # Если данные о пользователе все есть, но он снова написал сообщение - сбрасываем все и начинаем сначала
                else:
                    users.clear()
                    vbot.write_msg(event.user_id, 'Что-то пошло не так, давайте начнем с начала... Напишите: start или начать...')

            else:
                vbot.write_msg(event.user_id, 'Не понял вашего вопроса... Для поиска партнеров напишите: start или начать...')
