#!/usr/bin/env bash
set -euo pipefail

cd /root/oneshot_wordle/oneshot_guessle

# update repo to remote main
git fetch --all --prune
git reset --hard origin/main

# build and start services (uses production.yml in repo root)
docker-compose -f production.yml down --remove-orphans
docker-compose -f production.yml pull || true
docker-compose -f production.yml up -d --build

# run migrations and collectstatic
docker-compose -f production.yml run --rm django python manage.py migrate --noinput
docker-compose -f production.yml exec -T django python manage.py collectstatic --noinput