# Интернет-магазин (API) по доставке конфет "Сласти от всех напастей".


> Сервис доступен на http://130.193.55.7

## Установка

1) Обновите пакеты - ```sudo apt update```

2) Поставьте PostgreSQL - ```sudo apt install postgresql postgresql-contrib```

3) Склонируйте [репозиторий](https://github.com/kesha1225/CandyDeliveryAppApi)

4) Смените рабочую директорию ```cd CandyDeliveryAppApi/```

5) Создайте виртуальное окружение (если его нет) и активируйте его
   - ```
     python3 -m virtualenv venv
     source venv/bin/activate
     ```
6) Установите менеджер пакетов poetry - ```pip install poetry```

7) Установите зависимости - ```poetry install```

8) Для локального запуска - ```python __main__.py```


#### API и запуск на прод


> API по умолчанию запущен в сервисе systemd с названием api.service.
> Запрос проксируются наружу с помощью NGINX


Для запуска API на прод после установки в активированном виртуальном окружении 
запустите
```
gunicorn app:app --bind localhost:8080 --worker-class aiohttp.GunicornWebWorker
```

#### Тесты
Для запуска тестов после установки в активированном виртуальном окружении 
запустите ```pytest tests/```

#### База

Сервис использует базу postgresql.
Находится на сервере она на postgresql+asyncpg://postgres:samedov@localhost:5432/api
(Пароль оставлю в ридми, на случай если он вам нужен)


Для сброса базы можно использовать ```python3 update_base.py```


Внешние библиотеки подробно описаны в [pyproject.toml](https://github.com/kesha1225/CandyDeliveryAppApi/blob/master/pyproject.toml)
и [poetry.lock](https://github.com/kesha1225/CandyDeliveryAppApi/blob/master/poetry.lock)


Обработчика 6: GET /couriers/$courier_id реализован

Структура с подробным описанием ошибок каждого некорректного поля,
пришедшего в запросе на couriers/post или orders/post выглядит так:


couriers - стандартный ответ для 400, то есть список айди заказов или курьеров

errors_data - дополнительная информация об ошибках

   * location - местонахождение ошибочного значения
   * msg - Описание ошибки
   * type - Тип ошибки
   
```
{
  "validation_error": {
    "couriers": [
      {
        "id": 1
      },
      {
        "id": 2
      }
    ],
    "errors_data": [
      {
        "location": [
          "data",
          0,
          "working_hours"
        ],
        "msg": "Invalid date - 11:35-shue",
        "type": "value_error"
      },
      {
        "location": [
          "data",
          1,
          "regions",
          1
        ],
        "msg": "ensure this value is greater than or equal to 0",
        "type": "value_error.number.not_ge"
      },
      }]}}

```

