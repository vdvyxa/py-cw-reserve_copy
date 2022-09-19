from operator import ge
import os
from pprint import pprint
import requests

from VKrequest import VKRequest
from yaDiskRequest import YaDiskRequest


#####################################################################
#####################################################################

# Формат данных по фото:
# { 'id', 'owner_id', 'album_id', 'text', 'date',
#   'likes': {'count', 'user_likes'}, 
#   'sizes':[{}]
# } 
#   Массив 'sizes' содержит записи следующего формата:
#       {'url', 'width', 'height', 'type'}
#           Поле 'type' (строка, точнее 1 символ):
#               's' — Пропорциональная копия изображения с максимальной стороной 75px;
#               'm' — Пропорциональная копия изображения с максимальной стороной 130px;
#               'x' — Пропорциональная копия изображения с максимальной стороной 604px;
#               'o' — Если соотношение "ширина/высота" исходного изображения меньше или равно 3:2, то пропорциональная копия с максимальной стороной 130px. Если соотношение "ширина/высота" больше 3:2, то копия обрезанного слева изображения с максимальной стороной 130px и соотношением сторон 3:2.
#               'p' — Если соотношение "ширина/высота" исходного изображения меньше или равно 3:2, то пропорциональная копия с максимальной стороной 200px. Если соотношение "ширина/высота" больше 3:2, то копия обрезанного слева и справа изображения с максимальной стороной 200px и соотношением сторон 3:2.
#               'q' — Если соотношение "ширина/высота" исходного изображения меньше или равно 3:2, то пропорциональная копия с максимальной стороной 320px. Если соотношение "ширина/высота" больше 3:2, то копия обрезанного слева и справа изображения с максимальной стороной 320px и соотношением сторон 3:2.
#               'r' — Если соотношение "ширина/высота" исходного изображения меньше или равно 3:2, то пропорциональная копия с максимальной стороной 510px. Если соотношение "ширина/высота" больше 3:2, то копия обрезанного слева и справа изображения с максимальной стороной 510px и соотношением сторон 3:2
#               'y' — Пропорциональная копия изображения с максимальной стороной 807px;
#               'z' — Пропорциональная копия изображения с максимальным размером 1080x1024;
#               'w' — Пропорциональная копия изображения с максимальным размером 2560x2048px.
# Example:
#   sizes: [{
#           url: 'https://pp.vk.me/c633825/v633825034/7369/wbsAsrooqfA.jpg',
#           width: 130,
#           height: 87,
#           type: 'm'
#          }

#####################################################################

# Функция определения наибольшего размера фото
# PARAMS
#   PHOTO - словарь с данными о фото (формат VK)
# RETURN
#   словарь со следущими значениями:
#   { 'size': буква-идентификатор размера фото
#     'url': url для скачивания фото выбранного размерешния
#   }
def get_max_photo_size(photo):
    result = {}
    max = 0
    # цикл по массивам фоток
    for sizes in photo.get('sizes', []):
        # если размер очередной фотки больше сохраненного в max
        if sizes['width'] * sizes['height'] > max:
            # сохраняем новый максимальный размер фотки
            max = sizes['width'] * sizes['height']
            # сохраняем саму фотку с максимальным размером
            result = {
                'size': sizes['type'],
                'url': sizes['url']
            }

    return result

#####################################################################

# Функция определения расширения файла по его URL
# PARAMS
#   URL - URL для скачивания файла
# RETURN
#   расширение файла (строка)
def get_photo_extension(url):
    # разделяем строку по точкам('.') и берем последнюю часть ([-1])
    ext = url.split('.')[-1]
    # разделяем строку по вопросу ('?' и берем первую часть(до первого знака вопроса)
    # - это и есть само расширение файла
    ext = ext.split('?')[0]
    
    return ext

#####################################################################

# Функция получения имени файла по данным из ВК
# формат имени: "лайки_дата.расширение"
# PARAMS
#   PHOTO - данные о фото (формат ВК) (словарь)
#   URL - URL фото, которое надо сохранить
# RETURN
#   имя сохраненного файла (без пути)
def get_photo_filename(photo, url):
    filename = f'{photo["likes"]["count"]}_{photo["date"]}.{get_photo_extension(url)}'
    return filename

#####################################################################

# Функция сохранения фото с максимальным разрешением во временной папке
# PARAMS
#   PHOTO - данные о фото (формат ВК) (словарь)
#   TMP_FOLDER - папка, в которой сохранять файл
# RETURN словарь
#   {'filename', 'url', 'size'}
#   ИЛИ пусто {} (если файл не удалось скачать)
def save_max_photo(photo, tmp_folder):
    result = {}
    # поиск фото с максимальным разрешением
    photo_size = get_max_photo_size(photo)
    # имя файла
    filename = get_photo_filename(photo, photo_size.get('url',''))

    # получаем полный путь
    root_path = os.getcwd()
    # абсолютный путь файла
    file_full_path = os.path.join(root_path, tmp_folder, filename)

    # скачивание файла по URL
    data = requests.get(photo_size['url'])
    # проверка на ошибку
    if data.ok:
        # сохранение файла
        with open(file_full_path, 'wb') as f: 
            f.write(data.content)
        # сохранение результата
        result = {
            'filename': filename,
            'url': photo_size['url'],
            'size': photo_size['size']
        }

    return result 


#####################################################################

# Функция сохранения всех фото во временной папке
# PARAMS
#   DATA - список с полученными фото (формат ВК)
#   TMP_FOLDER - временная папка, куда сохранять файлы (по умолчанию, 'temp')
# RETURN
#   итоговый список в формате:
#   [ {
#       'filename': имя файла
#       'size': буква-идентификатор размера фото
#       'url': url для скачивания фото выбранного размерешния
#   },
#   {...},
#   ...
# ]
def parse_data_to_files(data, tmp_folder = 'temp'):
    result = []
    
    # цикл по всем фото
    for photo in data:
        # сохранение фотот с макасимальным разрешением
        # и получение сведений об этом фото
        saved_photo = save_max_photo(photo, tmp_folder)
        result += [saved_photo]

    return result

#####################################################################

# Функция создания папки
# PARAMS
#   FOLDER - папка (по умолчанию, 'temp')
# RETURN
#   TRUE или FALSE (если ошибка создания)
def create_folder(folder = 'temp'):
    # получаем полный путь
    root_path = os.getcwd()
    # проверка, что папки еще нет
    if not os.path.isdir(os.path.join(root_path, folder)):
        os.mkdir(os.path.join(root_path, folder))
    return True

#####################################################################

# Функция удаления всех файлов из папки и самой папки
# PARAMS
#   FOLDER - папка (по умолчанию, 'temp')
# RETURN
#   TRUE или FALSE (если ошибка удаления)
def delete_folder(folder = 'temp'):
    # получаем полный путь
    root_path = os.getcwd()
    # получаем список всех файлов по указанному пути
    files = os.listdir(os.path.join(root_path, folder))

    # в цикле удаляем каждый файл
    for file in files:
        # если встретили подкаталог - удаляем его
        if os.path.isdir(os.path.join(root_path, folder, file)):
            delete_folder(os.path.join(folder, file))
        os.remove(os.path.join(root_path, folder, file))
    # в конце удаяем саму папку
    os.rmdir(os.path.join(root_path, folder))
    
    # если папки больше нет - возвращаем TRUE
    return not os.path.isdir(os.path.join(root_path, folder))

#####################################################################

# Функция получения числа файлов в указанной папке
# PARAMS
#   PATH - папка, в которой лежат файлы
# RETURN
#   число файлов в папке
def get_files_count(path):
    files = []
    # формирование полного пути до файлов
    root_path = os.getcwd()
    full_path = os.path.join(root_path, path)
    # Список файлов по пути full_path
    try:
        files = os.listdir(full_path)
    except FileNotFoundError:
        print(f'Error {__name__} - Путь: {full_path} не существует!')
    return len(files)

#####################################################################
#####################################################################

if __name__ == '__main__':
    # необходимые данные для авторизации ВК
    vk_user_id = ''
    vk_token = ''
    # необходимые данные для авторизации YaDisk
    ya_token = ''
    # временная папка для хранения фото
    temp_folder = 'temp'
    # папка на YaDisk, куда будут загружаться фото
    ya_folder = 'vdvyxa'

    # создание объектов по работе с VK и YaDisk
    vk_request = VKRequest(vk_user_id, vk_token, token_file="vk_token.txt")
    ya_request = YaDiskRequest(ya_token, token_file="ya_token.txt")
    # ID пользователя VK, у которого запрашиваем фото
    # (указываем себя)
    vk_user_id = vk_request.user_id
    # получение фото из ВК
    photos = vk_request.get_user_photos(vk_user_id)

    print(f'{len(photos)} photos loaded from VK.')
 
    #pprint(photos)
    
     # создание временной папки
    create_folder(temp_folder)
    # обработка данных и сохранение фото во временной папке
    datainfo = parse_data_to_files(photos, temp_folder)
    
    # подсчет количества полученных файлов с фото
    files_count = get_files_count(temp_folder)
    
    print(f'{files_count} files saved in {temp_folder}.')

    # загрузка файлов с фото на YaDisk
    uploaded_count = ya_request.upload_files(temp_folder, ya_folder)

    print(f'{uploaded_count} files uploaded to Ya.Disk.')
 
    # Вывод информации на экран
    print(f'Totat {len(photos)} photos, {files_count} files saved and {uploaded_count} uploaded.')
    
    print('\nDATAINFO')
    pprint(datainfo)

    # Удаление временной папки - очистка следов
    delete_folder(temp_folder)

