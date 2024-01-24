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

### Installation

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
python3 -m venv env
source env/bin/activate
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

## Built With

- [Django](https://www.djangoproject.com/) - The web framework used
- [PostgreSQL](https://www.postgresql.org/) - The database used
- [Celery](https://docs.celeryproject.org/en/stable/) - Used for task scheduling
- [Redis](https://redis.io/) - The message broker for Celery
- [Nginx](https://nginx.org/) - Used as a web server and reverse proxy
