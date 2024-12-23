# Trip Weather Analyser

**Trip Weather Analyser** — это телеграм-бот, который помогает пользователям планировать свои поездки, предоставляя прогноз погоды для нескольких точек маршрута. 

## Возможности
- Создание маршрута из нескольких точек.
- Получение прогноза погоды для каждой точки маршрута.
- Простота использования через Telegram.

## Технологический стек
- **Python** — основной язык разработки.
- **Aiogram** — асинхронный фреймворк для работы с Telegram Bot API.
- **Yandex Weather API** — для получения прогноза погоды.
- **Yandex Geocode API** — для обработки географических координат.

## Команды
- `/start` - Приветственное сообщение
- `/help` - Список команд
- `/weather` - Прогноз погоды для путешествия

## Установка и запуск

### 1. Клонирование репозитория
Склонируйте репозиторий на ваш компьютер:
```bash
git clone https://github.com/Gjils/trip-weather-analyser.git
cd trip-weather-analyser
```


### 2. Создание виртуального окружения
Создайте и активируйте виртуальное окружение для изоляции зависимостей проекта:
``` bash
# На Windows
python -m venv venv
venv\Scripts\activate

# На macOS и Linux
python3 -m venv venv
source venv/bin/activate
```
### 3. Установка зависимостей
Убедитесь, что у вас установлен Python 3.7 или новее. Затем установите необходимые зависимости:
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
Создайте файл `.env` в корневой папке проекта и добавьте в него следующие переменные:
```
WEATHER_KEY="YOUR_KEY"
GEOCODE_KEY="YOUR_KEY"
BOT_TOKEN="YOUR_KEY"
```

### 5. Дополнительные файлы
- **`commands.txt`**: В корне проекта находится текстовый файл `commands.txt`, содержащий описание всех команд для BotFather, необходимых для настройки вашего бота.
- **`profile_picture.png`**: Файл `profile_picture.png` содержит аватар для вашего бота, который можно загрузить через BotFather.

### 6. Запуск бота
Для запуска бота выполните команду:
```bash
python main.py
```

Бот будет готов к использованию в вашем Telegram.

## Примечания
- Получить ключ API для Yandex Weather можно на [Yandex Weather Api](https://yandex.ru/dev/)
- Получить ключ API для Yandex Geocoder можно на [Yandex Maps Api](https://yandex.ru/maps-api/products).
- Токен для телеграм-бота можно создать с помощью [BotFather](https://core.telegram.org/bots).