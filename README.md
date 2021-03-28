# Интернет-магазин (API) по доставке конфет "Сласти от всех напастей".


## Установка


1) Склонируйте [репозиторий](https://github.com/kesha1225/CandyDeliveryAppApi)

2) ```cd CandyDeliveryAppApi```

3) Создайте виртуальное окружение (если его нет) - ```python3 -m virtualenv venv``` 
   и активируйте его - ```source venv/bin/activate```


2) Установите менеджер пакетов poetry - ```pip install poetry```

3) Установите зависимости - ```poetry install```



### Запуск


#### API
Для запуска API после установки в активированном виртуальном окружении 
запустите
```gunicorn app:app --bind localhost:8080 --worker-class aiohttp.GunicornWebWorker```

#### Тесты
Для запуска тестов после установки в активированном виртуальном окружении 
запустите ```pytest tests/```