# Oneshot Guessle
A version of wordle where you only have one chance to guess the day's word!


[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

### Setting Up Your Users

-   To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

-   To create a **superuser account**, use this command:

        $ docker-compose -f local.yml run --rm django python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### make migrations

- docker-compose -f local.yml run --rm django python manage.py makemigrations
or docker-compose -f production.yml run --rm django python manage.py makemigrations
- docker-compose -f local.yml run --rm django python manage.py migrate

💡 You can also run both together if you are having problems. eg:

docker-compose -f production.yml run --rm django sh -c "python manage.py makemigrations && python manage.py migrate"

### Type checks

Running type checks with mypy:

    $ mypy oneshot_guessle

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

## Deployment

The following details how to deploy this application.
1. build the app using `docker-compose -f local.yml build` # This will include updating requirements and push to docker container.
2. make the migrations for the app `docker-compose -f local.yml run --rm django python manage.py makemigrations`
3. Create a Superuser `docker-compose -f local.yml run --rm django python manage.py createsuperuser`
4. Run the server `docker-compose -f local.yml up`
5. At this point it will probably error because you need to load the words DB. in the browser address bar run `localhost:8000/load_words`

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).
