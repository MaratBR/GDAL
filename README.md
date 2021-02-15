# GDAL VIIRS

Библиотека на python для привязки, изменения проекции 
и ковертации VIIRS датасетов в tiff.

## Установка

```
git clone http://rcpod.space:3000/MaratBR/VIIRSProcessor
cd VIIRSProcessor
pip3 install -r ./requirements.txt
```

Для работы требуется библиотека pyproj версии 3, которая в 
свою очередь требует proj версии 7.2+

### Использование

Обработка карт и продуктов одновременно:
```
python3 processor.py
```

Обработка только карт:
```
python3 maps_processor.py
```

Обработка продуктов:
```
python3 products_processor.py
```