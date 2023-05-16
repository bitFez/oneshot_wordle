# Oneshot Guessle

A version of wordle where you only have one chance to guess the day's word!

## TODO
- [ ] Colour the alphabet according to the letters in the guess and clues
- [x] Create page of previous words
- [x] Add each guess to the Guessle_Attempt model
- [x] Limit a user from taking a guess if they have one already in the Guessle_Attempt model
- [x] Create league table of users who are most successful
- [x] create modal for rules
- [x] Create modal for displaying a user's streak data
- [x] Remove the warning card after success / failure and instead add to user's streak modal
- [x] Hide Nav bar using burger menu
- [x] check if the word wordle is copyrighted
    It seems likes it is :-( https://www.gamerevolution.com/news/703678-wordle-archive-removed-new-york-times-trademark-clone
- [x] Come up with a new name for the site
- [x] need to centre the heading without a linebreak
- [ ] Dark / light modes
- [x] Support modal page
- [x] Easy game mode (2 greens, 2 yellows)
- [x] Bonus (Hard) game mode (6 letter words 2 greens, 3 yellows)
- [x] Get a list of 6 letter words for the hard mode game
- Daily Stars
    - [x] 1 star for guessing the main word
    - [x] 1 star for guessing easy word
    - [x] 1 star for guesing bonus / hard word
- Ko-fi Page - 
    - for monthly donators:
        - [ ] ad-free experience
        - [x] unlock bonus / hard daily word
        - [ ] special role on discord
        - [ ] Members are able to suggest special theme days (star trek etc)
- [ ] Create word definitions to results
- [ ] Ads on page
- [ ] Countdown to next guessle
- [ ] Add shadow to bottom of tiles

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
1. build the app using `docker-compose -f local.yml build`
2. make the migrations for the app `docker-compose -f local.yml run --rm django python manage.py makemigrations`
3. Create a Superuser `docker-compose -f local.yml run --rm django python manage.py createsuperuser`
4. Run the server `docker-compose -f local.yml up`
5. At this point it will probably error because you need to load the words DB. in the browser address bar run `localhost:8000/load_words`

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).
