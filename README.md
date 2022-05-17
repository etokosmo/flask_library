# Библиотека книг

## Цели проекта

* Создать Веб приложение на Python+Flask для учета книг в библиотеке.
* Приложение выполняет CRUD операции над базой данных.

> Код написан в учебных целях.

## Стек технологий

* Сериализация (входных и выходных данных) на Marshmallow
* База данных sqlite3
* Flask-SQLAlchemy
* Миграции Alembic

## Конфигурации

* Python version: 3.10
* Libraries: requirements.txt

## Запуск

- Скачайте код
- Через консоль установите виртуальное окружение командой:

```bash
python3 -m venv env
```

- Активируйте виртуальное окружение командой:

```bash
source env/bin/activate
```

- Установите библиотеки командой:

```bash
pip install -r requirements.txt
```

- Запустите сайт командой:

```bash
python3 app.py
```

# Методы
```
url: /library/
method: GET
Возвращает все книги.
```
```
url: /library/
method: POST
Добавляет книгу.
```
```
url: /library/int:book_id/ 
method: GET
Возвращает книгу по id.
```
```
url: /library/string:author/ 
method: GET
Возвращает все книги автора.
```
```
url: /library/int:book_id/ 
method: PATCH
Обновляет данные по книге по id.
```
```
url: /library/int:book_id/
method: DELETE
Удаляет книгу по id.
```

Тело для POST/PATCH запроса:
```
{
    "author": {
        "name": "Сидоров"
    },
    "title": "Книга 3"
}
```
