from random import randrange
import urllib
import datetime

from pprint import pprint
import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType

def get_token(use_group: bool):
  if use_group:
      file = 'group'
  else:
      file = 'user'
  with open(file + '.txt', 'r') as f:
    token = f.readline()
  return token

vk_user = vk_api.VkApi(token=get_token(use_group = False))
vk_group = vk_api.VkApi(token=get_token(use_group = True))
longpoll = VkLongPoll(vk_group)
vk_upload = VkUpload(vk_group)
users={}

def write_msg(user_id, message, attachment):
    vk_group.method('messages.send', {'user_id': user_id,
                                      'random_id': randrange(10 ** 7),
                                      'message': message,
                                      'attachment': attachment})

def write_msg_photo(user_id):
    with open('1.jpeg', 'wb') as img_file:
        upload_image = upload.photo_messages(photos = img_file, peer_id = user_id)[0]
        pic = 'photo{}_{}'.format(upload_image['owner_id'], upload_image['id'])
    # resp = vk_upload.photo_messages(photos = ['1.jpeg', '2.jpeg', '3.jpeg'], peer_id = user_id)[0]
    # # att = list()
    # for ph in resp:
    #     att.append('photo{}_{}'.format(ph['owner_id'], ph['id']))
    vk_group.method('messages.send', {'user_id': user_id,
                                      'message': ' - ',
                                      'attachment': pic,
                                      'random_id': randrange(10 ** 7)})

def search_users(sex, age, city, user_id):
    if sex == 1:
       sex = '2'
    else:
       sex = '1'
    response = vk_user.method('users.search', {'count': '1000',
                                               'fields': 'bdate, city, relation, sex',
                                               'city': city,
                                               'sex': sex,
                                               'status': '1',
                                               'age_from': age,
                                               'age_to': age,})
    # оставляем кандидатов с открытой страницей
    if response['count'] > 0:
        open_items = [item for item in response['items'] if item['is_closed'] == False]
    #     тут надо вставить проверку на показ по id из БД

    #  берем первые три кандидата из фильтрованного списка и формируем набор данных

    for item in open_items[:3]:
        message = f'''{item['first_name']} {item['last_name']} \n https://vk.com/id{str(item['id'])}'''
        # надо это разбить на отдельные сообщения, так отправляется третье по популярности фото...
        attachment = get_best_photo(item['id'])
        write_msg(user_id, message, '')
        for att in attachment:
            write_msg(user_id, '', att)

# Сохраняем фото пользователей перед отправкой
def save_photo(url_photo):
    n = 0
    for url in url_photo:
        n += 1
        urllib.request.urlretrieve(url, f'{str(n)}.jpeg')

def get_best_photo(id):
    id_photo = []
    photos = vk_user.method('photos.get', {'owner_id': id,
                                   'album_id': 'profile',
                                   'extended': '1',
                                   'photo_sizes': '1'})
    if photos.get('count') > 0:
        sorted_photo = sorted(photos['items'], key = lambda d: d['likes']['count'] + d['comments']['count'], reverse=True)

        for photo in sorted_photo[:3]:
            id_photo.append(f'''https://vk.com/id{photo['owner_id']}?z=photo{photo['owner_id']}_{photo['id']}''')
            pprint(id_photo)
        return id_photo

def age_in_bdate(bdate):
    return (int(datetime.datetime.now().year) - int(bdate[-4:]))

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request.lower() in ['привет', 'hi', 'start', 'начать', 'ок', 'пуск']:
                # Получаем данные о пользователе - пол, город, дату рождения. На основании этих данных будем строить поиск.
                users = vk_user.method('users.get', {'user_ids': event.user_id, 'fields': 'bdate, city, relation, sex'})
                users = users[0]
                if len(users.get('bdate', '0')) > 5:
                   users['age'] = age_in_bdate(users['bdate'])

                if users.get('city', '0') == '0':
                   message = "Укажите ваш город"
                   pprint(users)
                elif users.get('age', '0') == '0':
                   #  переделать возраст, если дата рождения вида: 11.10 - символов 5, а 27.2 - 4...

                   message = "Укажите ваш возраст"
                   pprint(users)
                else:
                   pprint(users)
                   message = "Начинаю поиск партнеров. Подождите пару секунд..."
                   search_users(users['sex'], users['age'], users['city']['id'], event.user_id)
                write_msg(event.user_id, message, attachment='')

            # Получаем недостающие данные
            elif not request == 'hi' and users.get('id') == event.user_id:
                if users.get('city', '0') == '0':               # Находим город
                    cities = vk_user.method('database.getCities', {'country_id': '1', 'q': request})
                    if cities.get('count') == 0:
                       write_msg(event.user_id, "Не могу найти такой город, попробуйте ввести еще раз, либо укажите ближайший крупный город.", '')
                    else:
                       #  Берем первый город в списке. Надо бы сделать перебор регионов для правильности...
                       city = cities.get('items')[0]
                       users['city'] = {'id': city.get('id'), 'title': city.get('title')}
                       if users.get('age', '0') == '0':
                           message = "Укажите ваш возраст"
                       else:
                           message = "Начинаю поиск партнеров. Подождите пару секунд..."
                           search_users(users['sex'], users['age'], users['city']['id'], event.user_id)
                       write_msg(event.user_id, message, attachment='')


                elif users.get('age', '0') == '0':
                    if request.isdigit():
                        users['age'] = request
                        write_msg(event.user_id, "Начинаю поиск партнеров. Подождите пару секунд...", '')
                        search_users(users['sex'], users['age'], users['city']['id'], event.user_id)
                    else:
                        write_msg(event.user_id, "Введите возраст цифрами.", '')
                # Если данные о пользователе все есть, но он снова написал сообщение - сбрасываем все и начинаем сначала
                else:
                    users.clear()
                    write_msg(event.user_id, "Что-то пошло не так, давайте начнем с начала... Напишите: start или начать...", '')

            else:
                write_msg(event.user_id, "Не понял вашего вопроса... Для поиска партнеров напишите: start или начать...", '')
