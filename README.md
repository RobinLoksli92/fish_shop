# Телеграм-магазин морепродуктов
Онлайн-магазин морепродуктов реализован через телеграм бота.
### Что используется
1. [Телеграм-бот](https://tlgrm.ru/docs/bots).
2. Для сохранения состояния пользователя в магазине используется база данных [REDIS](https://redislabs.com/).
3. Для организации структуры магазина (CMS) используется  [Elastic Path Commerce Cloud](https://www.elasticpath.com/elastic-path-commerce-cloud).

### Что необходимо
1. Python3 должен быть уже установлен. 
2. Рекомендуется использовать [virtualenv/venv](https://docs.python.org/3/library/venv.html) для изоляции проекта.
3. Затем используйте pip (или pip3, есть конфликт с Python2) для установки зависимостей:
```python
pip install -r requirements.txt
```
4. Создайте файл `.env` и пропишите в нем переменные окружения:
- MOLTIN_CLIENT_ID - id клиента Commerce Cloud API ([подробнее здесь](https://documentation.elasticpath.com/commerce-cloud/docs/developer/get-started/your-first-api-request.html));
- TELEGRAM_TOKEN - токен бота телеграм (получить у `@BotFather`);
- REDIS_HOST - адрес базы данных [REDIS](https://redislabs.com/);
- REDIS_PORT - номер порта для подключения к базе данных [REDIS](https://redislabs.com/);
- REDIS_USERNAME - имя для подключения к базе данных [REDIS](https://redislabs.com/);
- REDIS_PASSWORD - пароль для подключения к базе данных [REDIS](https://redislabs.com/);
5. Запустите бота командой:
```python
python bot.py
```
### Функционал бота
Для начала работы с ботом пользователь вводит команду `/start`, после чего возможно:
- посмотреть каталог товаров
- посмотреть описание товара
- добавлять/удалять товары в корзине
- перейти к оплате товара

