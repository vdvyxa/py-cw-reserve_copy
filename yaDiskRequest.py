import requests
import os

#####################################################################
#####################################################################

class YaDiskRequest:
    # Коснструктор
    # PARAMS
    #   TOKEN      - метка авторизации для Ya.Disk (необязательно)
    #   TOKEN_FILE - имя файла, в котором содержится метка авторизации 
    #                (по умолчанию - 'token')
    def __init__(self, token = '', token_file = 'ya_token'):
        self.token = token
        self.token_file = token_file
        
        # Получение токена из файла, если не задан явно
        if not self.token: 
            # формирование абсолютного пути
            root_path = os.getcwd()
            full_path = os.path.join(root_path, token_file)
            # считывание из файла метки и сохранение в классе (self.token)
            with open(full_path) as f_token:
                self.token = f_token.read()       

#####################################################################

    # Формирование заголовков для HTTP-запросов
    # (туда добавляется информация об авторизации)
    # RETURN
    #   словарь с данными заголовка {}
    def _make_header(self):
        return {
            'Content-type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

#####################################################################

    # Внутренний метод для получения ссылки, 
    # по которой будут загружаться файла на Ya.Disk
    # PARAMS
    #   DISK_FILE_PATH - путь на Ya.Disk, куда будут загружаться файлы
    # RETURN 
    #   URL или '' (если ошибка)
    def _get_upload_link(self, disk_file_path):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {
            'path': disk_file_path,
            'overwrite': True
        }
        resp = requests.get(upload_url, headers=self._make_header(), params=params)
        # URL находится по ключу 'href' в JSON-ответе
        if resp.ok:
            return resp.json().get('href', {})
        return ''

#####################################################################

    # Метод загрузки всех файлов из папки file_path 
    # на Ya.Disk в папку destination_path
    # PARAMS
    #   FILE_PATH        - путь к файлам на компьютере
    #   DESTINATION_PATH - путь на Ya.Disk, куда будут загружаться файлы 
    #                      (по умолчанию - '')
    # RETURN 
    #   количество успешно загруженных файлов
    def upload_files(self, file_path, destination_path = ''):
        # получение url для загрузки файлов на Ya.Disk
        upload_url = self._get_upload_link(destination_path)

        # Если URL не пришел - нет смысла загружать (ошибка, возможно, в авторизации)
        if not upload_url:
            return 0

        # формирование полного пути до файлов
        root_path = os.getcwd()
        full_path = os.path.join(root_path, file_path)
        # Список файлов по пути full_path
        files = os.listdir(full_path)
        # счетчик загруженных файлов
        count_uploaded = 0
        
        # в цикле отправляем по одному файлу на upload_url
        for file in files:
            resp = requests.put(upload_url, data=open(os.path.join(full_path, file), "rb"))
            # проверка на успех загрузки файла
            if resp.ok:
                count_uploaded += 1
        # возвращаем число успешно загруженных файлов
        return count_uploaded            
            
