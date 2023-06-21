## Проект Foodgram

Foodgram - продуктовый помощник, на этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект доступен по [адресу](https://htt://158.160.9.20)

Документация к API доступна [здесь](https://htt://158.160.9.20/api/docs/)

В документации описаны возможные запросы к API и структура ожидаемых ответов. Для каждого запроса указаны уровни прав доступа.

### Как развернуть проект на удаленном сервере:

- Клонировать репозиторий:
```
git@github.com:stupidcabbage/foodgram-project-react.git
```

- Установить на сервере Docker, Docker Compose:

- Перейти в директорию infra и запустить контейнеры.
```
sudo docker compose up -d
```

- После успешной сборки выполнить миграции:
```
sudo docker compose exec web python manage.py migrate
```

- Создать суперпользователя:
```
sudo docker compose exec web python manage.py createsuperuser
```

- Собрать статику:
```
sudo docker compose exec web python manage.py collectstatic --noinput
```

- Наполнить базу данных содержимым из файла data/ingredients.json:
```
sudo docker compose exec web python manage.py upload_data
```

- Для остановки контейнеров Docker:
```
sudo docker compose down -v      # с их удалением
sudo docker compose stop         # без удаления
```

### Примеры запросов к API:

Получение списка всех пользователей (GET):

```
http://localhost/api/users/
```
Получение списка всех тэгов:

```
http://localhost/api/tags/
```

Получение списка всех рецептов:

```
http://localhost/api/v1/recipes/
```