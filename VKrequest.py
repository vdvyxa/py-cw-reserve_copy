import requests
import os

#####################################################################
#####################################################################

class VKRequest:
    # Коснструктор
    # PARAMS
    #   USER_ID    - ID пользователя, от имени которого будут отправляться запросы в ВК
    #   TOKEN      - метка авторизации для Ya.Disk (необязательно)
    #   TOKEN_FILE - имя файла, в котором содержится USER_ID (1я строка) и токен (2я строка) 
    #                (по умолчанию - 'token')
    def __init__(self, user_id = '', token = '', token_file = 'vk_token'):
        self.user_id = user_id
        self.token = token
        self.token_file = token_file
        
        # Получение токена из файла, если не задан явно
        if not self.token or not self.user_id: 
            # формирование абсолютного пути
            root_path = os.getcwd()
            full_path = os.path.join(root_path, token_file)
            # считывание из файла метки и сохранение в классе (self.token)
            with open(full_path) as f_token:
                self.user_id = f_token.readline().strip()
                self.token = f_token.readline().strip()

#####################################################################

    # Формирование заголовков для HTTP-запросов
    # (туда добавляется информация об авторизации)
    # RETURN
    #   словарь с данными заголовка {}
    def _make_header(self):
        return {
            'Content-type': 'application/json',
        }

#####################################################################

    # Формирование обязательных параметров для любого запроса в ВК API
    # (авторизация и access_token)
    # RETURN
    #   словарь с данными параметров {}
    def _make_params(self):
        return {
            'access_token': self.token,
            'v': '5.131'
        }

#####################################################################


    # Возвращает фото с указанной учетной записи и указанного альбома
    # PARAMS
    #   USER_ID - ID пользователя в VK
    #   PHOTOS_COUNT - количество получаемых фото (по умолчанию, 5)
    #   ALBUM - из какого альбома ('wall', 'profile', 'saved') (по умолчанию, 'wall')
    # RETURN
    # { Словарь следующего типа:
    # { 'count',
    #   'items': [
    #              { 'id', 'owner_id', 'album_id', 'comments', 'date', 'text',
    #                'likes': {'count', 'user_likes'},
    #                'sizes': [
    #                            { 'height', 'width', 'type', 'url'}
    #                         ]
    #              }
    #            ]
    def get_user_photos(self, user_id, photos_count = 5, album = 'wall'):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id': user_id,    # ID пользователя, чьи фотографии хотим получить
            'extended': 1,          # вернуть доп.информацию (число лайков, репостов)
            'count': photos_count,  # число фотографий
            'photo_sizes': 1,       # получать информацию о размерах фото в специальном формате\
            'album_id': album
        }
        response = requests.get(url, headers = self._make_header(), params={**self._make_params(), **params})
        if response.ok:
            return response.json()['response']
        return False

   
#####################################################################
#####################################################################
