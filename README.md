# FoodGram - коллекция кулинарных рецептов
[![Main FoodGram workflow](https://github.com/zmlkf/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/zmlkf/foodgram-project-react/actions/workflows/main.yml)

## Описание
FoodGram - это продуктовый помощник, хранящий в себе коллекцию рецептов, позволяющий всем пользователям просмативать рецепты блюд. А для тех, кто зарегистрирован, появляется возможность публиковать свои собсвенные рецепты, подписываться на других авторов этой платформы, добавлять любые рецепты в избранное и в корзину(из которой потом, нажатием одной кнопки, можно будет получить список всех необходимых ингредиентов). 
## Стек примененных технологий
1. Python 
Высокоуровневый язык программирования, широко используемый для веб-разработки, анализа данных, искусственного интеллекта и многих других областей. 

2. Django 
Мощный фреймворк для веб-разработки на Python. Django обеспечивает быстрое создание безопасных и масштабируемых веб-приложений благодаря своей архитектуре, включающей ORM (Object-Relational Mapping) для работы с базой данных, систему маршрутизации URL, систему администрирования и многие другие функции.

3. Nginx
Высокопроизводительный веб-сервер и прокси-сервер, который обеспечивает обработку запросов от клиентов и маршрутизацию их к соответствующим веб-приложениям или сервисам. Nginx также может использоваться для обслуживания статических файлов, балансировки нагрузки и других задач.

4. Gunicorn 
WSGI (Web Server Gateway Interface) сервер для Python веб-приложений. Gunicorn используется для запуска и управления веб-приложениями Django, обеспечивая их стабильную работу и масштабируемость.

5. Docker 
Платформа для разработки, доставки и запуска приложений в контейнерах. Docker обеспечивает унифицированный способ упаковки приложений и их зависимостей, что делает процесс развертывания и масштабирования приложений проще и более надежным.

6. GitHub Actions
Сервис автоматизации задач на основе событий, предоставляемый GitHub. GitHub Actions позволяет создавать и настраивать рабочие процессы для вашего репозитория на GitHub, такие как тестирование, сборка, развертывание и многие другие операции, которые могут быть выполнены автоматически при определенных событиях в репозитории.

## Развернуть проект локально
1. Клонировать репозиторий:

```bash
git clone https://github.com/zmlkf/foodgram-project-react 
```
2. Перейти в директорию проекта
```bash
cd foodgram-project-react
```
3. Создать файл .env и прописать в нем константы
```bash
POSTGRES_DB= - имя базы данных
POSTGRES_USER= - имя пользователя
POSTGRES_PASSWORD= - пароль
DEBUG='True'
```
4. Выпольнить последовательно команды
```bash
sudo docker compose -f docker-compose.yml up -d
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /static/static/
```
5. Проект и документация станут доступны по
```bash
[http://localhost/](http://localhost/)
[http://localhost/api/docs/](http://localhost/api/docs/)
```

## Проект достпун по адресу [https://foodgramm-zmlkf.ddns.net/](https://foodgramm-zmlkf.ddns.net/)
Логин и пароль администратора

- zmlkf@gmail.com

- zmlkfpassword

Логин и пароль обычного пользователя

- petrovich@omail.ru

- parolparol

## Документация доступна по адресу  [https://foodgramm-zmlkf.ddns.net/api/docs/redoc.html](https://foodgramm-zmlkf.ddns.net/api/docs/redoc.html)




## Автор
Roman Zemliakov [GitHub](https://github.com/zmlkf)
