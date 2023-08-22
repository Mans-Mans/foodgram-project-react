### Почта админа: mans@mans.ru
### Пароль админа: mans
### Описание проекта фудграм - https://mans-foodgram.sytes.net

**Возможности проекта фудграм**
* Делиться рецептами.
* Находить интересные рецепты для себя.
* Подписываться на интересных авторов.
* Сохранять рецепты в избранных.
* Добавлять рецепты в корзину.
* Скачивать список ингредиентов с корзины.
* Для просмотра рецептов не нужна регистация.
* Для создания рецепта, подписки на авторов, скачивания списка ингредиентов необходима регистрация.
* Доступна система смены пароля.

### Стек технолигий
* Python3.10.6
* Django
* djangorestframework
* Nginx
* Gunicorn
* React
* Certbot
* Docker

### Как запустить проект локально:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/yandex-praktikum/kittygram_backend.git
```

```
cd foodgram_backend
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py makemigrations
python3 manage.py migrate
```

Импортировать ингредиенты в базу данных

```
python3 manage.py import
```

Результатом успешной загрузки будет сообщение:

```
$ Данные успешно загружены
```

Запустить проект:

```
python3 manage.py runserver
```
### Как запустить проект в контейнере:
Клонировать репозиторий:

```
git clone https://github.com/yandex-praktikum/kittygram_backend.git
```

Создать файл .env по примеру:

```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
```

Сбилдить и запустить контейнеры:

```
docker compose up --build
```

Перейти в контейнер бэкэнда:

```
docker compose exec -it foodgram-project-react-backend-1 bash
```

Выполнить миграции, собрать статику, создать суперпользователя, импортировать данные

```
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
python manage.py import
```

### Примеры запросов на сайте :
* https://mans-foodgram.sytes.net - главная страница с рецептами
* https://mans-foodgram.sytes.net/signin - страница авторизации
* https://mans-foodgram.sytes.net/signup - страница регистрации
* https://mans-foodgram.sytes.net/subscriptions - страница ваших подписок
* https://mans-foodgram.sytes.net/recipes/create - страница создания рецепта

### Автор проекта - Миндугулов Мансур
