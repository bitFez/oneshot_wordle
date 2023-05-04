# Oneshot Wordle

A version of wordle where you only have one chance to guess the day's word!

## TODO
- [ ] Use HTMX to only partially load the last row of the guess form
- [ ] Colour the alphabet according to the letters in the guess and clues
- [ ] Create page of previous words
- [ ] Create league table of users who are most successful
- [ ] create modal for rules
- [ ] Create modal for displaying a user's streak data
- [ ] Remove the warning card after success / failure and instead add to user's streak modal
- [x] Hide Nav bar using burger menu
- [x] check if the word wordle is copyrighted
    It seems likes it is :-( https://www.gamerevolution.com/news/703678-wordle-archive-removed-new-york-times-trademark-clone
- [ ] Come up with a new name for the site
- [x] need to centre the heading without a linebreak


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
- docker-compose -f local.yml run --rm django python manage.py migrate

### Type checks

Running type checks with mypy:

    $ mypy oneshot_wordle

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

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).
