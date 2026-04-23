#!/usr/bin/env bash
set -euo pipefail
set -x
trap 'echo "ERROR: command failed at line ${LINENO}: ${BASH_COMMAND}"' ERR

cd /root/oneshot_wordle/oneshot_guessle

# update repo to remote main
git fetch --all --prune
git reset --hard origin/main

# Sync selected runtime secrets from root .env (written by CI) into
# the production Django env file consumed by docker-compose.
if [ -f ".env" ]; then
	python3 - <<'PY'
from pathlib import Path

source = Path(".env")
target = Path(".envs/.production/.django")
managed = {
	"BLUESKY_DAILY_POST_ENABLED",
	"BLUESKY_HANDLE",
	"BLUESKY_APP_PASSWORD",
	"BLUESKY_SERVICE_URL",
	"BLUESKY_MAIN_GAME_URL",
}

def parse_env_lines(lines):
	result = {}
	for raw in lines:
		line = raw.strip()
		if not line or line.startswith("#") or "=" not in line:
			continue
		k, v = line.split("=", 1)
		result[k.strip()] = v
	return result

src_values = parse_env_lines(source.read_text(encoding="utf-8").splitlines())
target_lines = target.read_text(encoding="utf-8").splitlines() if target.exists() else []

preserved = []
for line in target_lines:
	if "=" not in line:
		preserved.append(line)
		continue
	key = line.split("=", 1)[0].strip()
	if key not in managed:
		preserved.append(line)

for key in sorted(managed):
	if key in src_values:
		preserved.append(f"{key}={src_values[key]}")

target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("\n".join(preserved) + "\n", encoding="utf-8")

print("Synced Bluesky vars into .envs/.production/.django:")
for key in sorted(managed):
	print(f"  {key}: {'set' if bool(src_values.get(key, '')) else 'missing'}")
PY
fi

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