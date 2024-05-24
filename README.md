# FoodGram - collection of culinary recipes
[![Main FoodGram workflow](https://github.com/zmlkf/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/zmlkf/foodgram-project-react/actions/workflows/main.yml)

## Description
FoodGram is a grocery assistant that stores a collection of recipes, allowing all users to browse dish recipes. And for those who are registered, there is an opportunity to publish their own recipes, subscribe to other authors on this platform, add any recipes to favorites and to the cart (from which, by pressing a single button, you can get a list of all the necessary ingredients).

## Stack of applied technologies
1. Python
A high-level programming language widely used for web development, data analysis, artificial intelligence, and many other fields.

2. Django
A powerful web development framework in Python. Django enables rapid development of secure and scalable web applications due to its architecture, including ORM (Object-Relational Mapping) for working with databases, URL routing system, administration system, and many other features.

3. Nginx
A high-performance web server and proxy server that handles requests from clients and routes them to the appropriate web applications or services. Nginx can also be used to serve static files, load balancing, and other tasks.

4. Gunicorn
A WSGI (Web Server Gateway Interface) server for Python web applications. Gunicorn is used to run and manage Django web applications, ensuring their stable operation and scalability.

5. Docker
A platform for developing, shipping, and running applications in containers. Docker provides a unified way to package applications and their dependencies, making the process of deploying and scaling applications easier and more reliable.

6. GitHub Actions
An event-driven task automation service provided by GitHub. GitHub Actions allows you to create and customize workflows for your GitHub repository, such as testing, building, deploying, and many other operations that can be automatically performed on certain events in the repository.

## Deploy the project locally
1. Clone the repository:

```bash
git clone git@github.com:zmlkf/foodgram.git
```
2. Navigate to the project directory
```bash
cd foodgram
```
3. Create a .env file and define constants in it
```bash
POSTGRES_DB= - database name
POSTGRES_USER= - username
POSTGRES_PASSWORD= - password
DEBUG='True'
```
4. Execute the following commands sequentially
```bash
sudo docker compose -f docker-compose.yml up -d
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /static/static/
```
5. The project and documentation will be available at
```bash
[http://localhost/](http://localhost/)
[http://localhost/api/docs/](http://localhost/api/docs/)
```

## Project available at [https://foodgramm-zmlkf.ddns.net/](https://foodgramm-zmlkf.ddns.net/)

## Documentation available at [https://foodgramm-zmlkf.ddns.net/api/docs/redoc.html](https://foodgramm-zmlkf.ddns.net/api/docs/redoc.html)

## Author
Roman Zemliakov [GitHub](https://github.com/zmlkf)
