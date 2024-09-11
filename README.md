# taskmanager

This is a Django-based task management application. It uses Django for the backend, PostgreSQL for the database, and Celery with Redis for task scheduling.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8+
- Django 3.2+
- PostgreSQL 13.0+
- Celery 5.0+
- Redis 6.0+

### Local Setup

1. Clone the repository:

```sh
git clone https://github.com/berkaykrc/task-manager-api
```

2. Navigate to the project directory:

```sh
cd taskmanager
```

3. Create a virtual environment and activate it:

```sh
python3 -m venv venv
source .venv/bin/activate
```

4. Install the required packages:

```sh
pip install -r requirements.txt
```

5. Copy the sample environment file and modify it according to your local settings:

```sh
cp taskmanager/taskmanager/.env.dist taskmanager/taskmanager/.env
```

6. Run the Django migrations to set up your models:

```sh
python manage.py migrate
```

## Usage

To start the server, run:

```sh
python manage.py runserver
```

Then visit `http://localhost:8000` in your web browser.

## Running the tests

To run the tests, use:

```sh
python manage.py test
```

## Docker

This project uses Docker to create a reproducible environment that's easy to set up on any machine. The `Dockerfile` and `compose.yaml` files are used to define this environment.

### Dockerfile

The `Dockerfile` defines the environment for a single Django server Docker container. It specifies the base image, the dependencies, and the commands to run when the container starts. It uses the official Python 3.8 slim-buster image as a base image, sets some environment variables, installs the Python dependencies listed in the `requirements.txt` file, and runs the Django server.

### compose.yaml

The `compose.yaml` file defines the services, networks, and volumes for a Docker application. It's used to run multiple Docker containers as a single service. In this project, the `compose.yaml` file defines the services for the Django application, PostgreSQL database, Nginx and, Redis for production.

To start the Docker application, run the following command in the same directory as the `compose.yaml` file:

```sh
docker-compose up 
or
docker compose -f compose.yaml up according to your docker version
```

## Built With

- [Django](https://www.djangoproject.com/) - The web framework used for building the application. It provides tools and functionalities for building secure and scalable web applications.
- [PostgreSQL](https://www.postgresql.org/) - The relational database used for storing application data. It's known for its performance and standards compliance.
- [Celery](https://docs.celeryproject.org/en/stable/) - Used for task scheduling and processing. It allows the application to perform tasks asynchronously and schedule recurring tasks.
- [Redis](https://redis.io/) - Used as a message broker for Celery and as a cache for the Django application. It provides fast in-memory data storage.
- [Nginx](https://nginx.org/) - Used as a web server and reverse proxy. It handles HTTP requests and serves static&media files.
- [django-csp](https://pypi.org/project/django-csp/) - Used for adding Content Security Policy headers to the Django application. It helps to prevent cross-site scripting (XSS) attacks.
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/) - A JSON Web Token authentication plugin for the Django Rest Framework. It's used in this project to handle user authentication. When a user logs in, they receive a JSON Web Token that they can use to authenticate their requests.
- [django-filter](https://django-filter.readthedocs.io/en/stable/) - Used for creating filters in the Django application. It provides a simple way to filter querysets based on user input.
- [django-debug-toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/) - Used for debugging the Django application. It provides a set of panels displaying various debug information.
- [django-cors-headers](https://pypi.org/project/django-cors-headers/) - Used for handling Cross-Origin Resource Sharing (CORS) headers in the Django application. It allows the application to control which domains can access the API.
- [psycopg2-binary](https://pypi.org/project/psycopg2-binary/) - Used as a PostgreSQL adapter for Python. It allows the Django application to connect to the PostgreSQL database.
- [django-redis](https://django-redis.readthedocs.io/en/latest/) - Used as a Redis cache backend for Django. It allows the Django application to use Redis as a cache.