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

def write_msg_photo(user_id, message, photos):
    save_photo(photos)
    pic = []
    for photo in ['1.jpeg', '2.jpeg', '3.jpeg']:
        with open(photo, 'rb') as img_file:
            upload_image = vk_upload.photo_messages(photos = img_file, peer_id = user_id)[0]
            pic.append('photo{}_{}'.format(upload_image['owner_id'], upload_image['id']))
    # resp = vk_upload.photo_messages(photos = ['1.jpeg', '2.jpeg', '3.jpeg'], peer_id = user_id)[0]
    # # att = list()
    # for ph in resp:
    #     att.append('photo{}_{}'.format(ph['owner_id'], ph['id']))
    pprint(pic)
    vk_group.method('messages.send', {'user_id': user_id,
                                      'message': message,
                                      'attachment': ','.join(pic),
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
        photos = get_best_photo(item['id'])
        write_msg_photo(user_id, message, photos)


        # attachment = get_best_photo(item['id'])
        # write_msg(user_id, message, '')
        # for att in attachment:
        #     write_msg(user_id, '', att)

# Сохраняем фото пользователей перед отправкой
def save_photo(url_photo):
    # url = 'https://sun9-50.userapi.com/impf/9AE-9IoP7erZKVcw6naTd1JhfWwK82FY4WOqlg/koKQnDTatZU.jpg?size=604x604&quality=96&sign=0f1fc3b2d086386af0930e83589c9892&c_uniq_tag=Eg0VyOV4rjZDzTuS10ScfJ_eFmYbjWE5rRdnbUuYUMg&type=album'
    # urllib.request.urlretrieve(url, f'12.jpeg')
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

        for ph in sorted_photo[:3]:
            for photo in ph['sizes']:
                if photo['type'] == 'x':
                    id_photo.append(photo['url'])
            # id_photo.append(f'''https://vk.com/id{photo['owner_id']}?z=photo{photo['owner_id']}_{photo['id']}''')
        # save_photo(id_photo)
        # pprint(id_photo)
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
                # save_photo()
                # write_msg_photo(event.user_id)
                if len(users.get('bdate', '0')) > 5:
                   users['age'] = age_in_bdate(users['bdate'])

                if users.get('city', '0') == '0':
                   message = "Укажите ваш город"
                   pprint(users)
                elif users.get('age', '0') == '0':
                   #  переделать возраст, если дата рождения вида: 11.10 - символов 5, а 27.2 - 4...

                   message = "Укажите ваш возраст"
                   # pprint(users)
                else:
                   # pprint(users)
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
