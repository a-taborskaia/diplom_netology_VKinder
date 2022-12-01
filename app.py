from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
# Получение токена пользователя или сообщества
def get_token(use_group: bool):
    file = 'group' if use_group else 'user'
    with open(file + '.txt', 'r') as f:
        token = f.readline()
    return token
#
class VBot:
    def __init__(self, token):
        self.token = token
        self.vk = vk_api.VkApi(token=self.token)
        self.longpoll = VkLongPoll(self.vk)
    # Отправка сообщения
    def write_msg(self, user_id, message, attachment=''):
        self.vk.method('messages.send', {'user_id': user_id,
                                    'random_id': randrange(10 ** 7),
                                    'message': message,
                                    'attachment': attachment})
    #
class VKinder:
    def __init__(self, token):
        self.token = token
        self.vk = vk_api.VkApi(token=self.token)
    # Получение данных о пользователе, написавшем сообщение
    def get_user_data(self, user_id):
        response = self.vk.method('users.get', {'user_ids': user_id, 'fields': 'bdate, city, relation, sex'})
        return response
    # Поиск пользователей, подходящих для знакомства
    def user_search(self, sex, age, city):
        sex = '2' if sex == 1 else '1'
        response = self.vk.method('users.search', {'count': '1000',
                                                   'fields': 'bdate, city, relation, sex',
                                                   'city': city,
                                                   'sex': sex,
                                                   'status': '1',
                                                   'age_from': age,
                                                   'age_to': age, })
        return response
    # Поиск трех лучших фотографий
    def photo_search(self, user_id):
        id_photo = []
        response = self.vk.method('photos.get', {'owner_id': user_id,
                                            'album_id': 'profile',
                                            'extended': '1',
                                            'photo_sizes': '1'})
        if response.get('count') > 0:
            sorted_photo = sorted(response['items'], key=lambda d: d['likes']['count'] + d['comments']['count'],
                                  reverse=True)
            for photo in sorted_photo[:3]:
                id_photo.append(f'''photo{photo['owner_id']}_{photo['id']}''')
            return id_photo
    # Поиск города
    def city_search(self, request):
        response = self.vk.method('database.getCities', {'country_id': '1', 'q': request})
        return response
