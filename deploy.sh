#!/usr/bin/env bash
set -euo pipefail
set -x
trap 'echo "ERROR: command failed at line ${LINENO}: ${BASH_COMMAND}"' ERR

cd /root/oneshot_wordle/oneshot_guessle

# update repo to remote main
git fetch --all --prune
git reset --hard origin/main

# build and start services (uses production.yml in repo root)
echo "Bringing down existing services"
docker-compose -f production.yml down --remove-orphans
echo "Pulling images (best-effort)"
docker-compose -f production.yml pull || true
echo "Building and starting services"
docker-compose -f production.yml up -d --build

# run migrations and collectstatic
echo "Running migrations"
docker-compose -f production.yml run --rm django python manage.py migrate --noinput
echo "Collecting static files"
set +e
docker-compose -f production.yml exec -T django python manage.py collectstatic --noinput --verbosity 2
collectstatic_status=$?
set -e
if [ "$collectstatic_status" -ne 0 ]; then
	echo "Collectstatic failed (exit ${collectstatic_status}); dumping recent django container logs"
	docker-compose -f production.yml logs --no-color --tail=200 django || true
	exit $collectstatic_status
fi

# clean up unused docker resources to free up disk space
# removes dangling images, stopped containers, unused networks, and build cache
echo "Pruning Docker resources"
docker system prune -f --volumes