SCALE = 2000
IS_DEBUG = True

# конфигурация PNG файлов, где
# name - уникальный идентификатор изображения
# display_name - имя, которое будет размещено на изображении
# xlim и ylim - массив с 2 элементами (предел по X и Y в проекции)
PNG_CONFIG = [
    {
        'name': 'novosibirsk',
        'display_name': 'Новосибирская область',
        'xlim': (-300000, 350000),
        'ylim': (-280000, 240000),
        'mask_shapefile': '/home/marat/Downloads/Agro/Vectors/Novosibirsk/novosib_agro.shp'
    }
]

# входые данные и папка с выходными
INPUT_DIR = '/media/marat/Quack/Projects/GDAL_Data/NPP/'
OUTPUT_DIR = '/home/marat/Documents'

# дополнительный точки на карте (Томск уже есть по-умолчанию и показан просто как пример)
# MAP_POINTS = [
#     (84.948197, 56.484680, 'Томск')
# ]

# папка с БД файлом
# CONFIG_DIR = ''
