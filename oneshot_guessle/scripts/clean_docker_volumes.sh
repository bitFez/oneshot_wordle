#!/usr/bin/env bash
set -euo pipefail

# List dangling docker volumes that are safe to remove and optionally delete them.
# Default excludes protect common DB volumes (postgres, pgdata, mysql, redis, etc.).
# Usage:
#   ./scripts/clean_docker_volumes.sh         # dry-run (list candidates)
#   ./scripts/clean_docker_volumes.sh --force # delete candidates after confirmation
#   ./scripts/clean_docker_volumes.sh --exclude pgdata,postgres --force

FORCE=0
EXCLUDE=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --force) FORCE=1; shift ;;
    --exclude) IFS=',' read -r -a arr <<< "$2"; EXCLUDE+=("${arr[@]}"); shift 2 ;;
    --help) echo "Usage: $0 [--force] [--exclude a,b,c]"; exit 0 ;;
    *) echo "Unknown arg $1"; exit 1 ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "docker CLI not found in PATH" >&2; exit 1
fi

DEFAULT_EXCLUDES=(postgres pgdata postgresql pg_ mongo mysql db redis)
EXCLUDES=("${DEFAULT_EXCLUDES[@]}" "${EXCLUDE[@]:-}")

echo "Finding dangling volumes..."
mapfile -t dangling < <(docker volume ls --filter dangling=true --format '{{.Name}}')

if [ ${#dangling[@]} -eq 0 ]; then
  echo "No dangling volumes found."; exit 0
fi

candidates=()
for v in "${dangling[@]}"; do
  skip=0
  for p in "${EXCLUDES[@]}"; do
    if [[ -n "$p" && "${v,,}" == *"${p,,}"* ]]; then
      skip=1; break
    fi
  done
  if [ $skip -eq 0 ]; then candidates+=("$v"); fi
done

if [ ${#candidates[@]} -eq 0 ]; then
  echo "No candidate volumes (dangling & not excluded)."; exit 0
fi

echo "Candidates to inspect:"
index=0
declare -A sizes
for v in "${candidates[@]}"; do
  index=$((index+1))
  # measure size via ephemeral container (alpine expected available or will be pulled)
  size=$(docker run --rm -v "$v":/v alpine sh -c "du -sh /v 2>/dev/null || echo 0" 2>/dev/null || echo "<err>")
  size=${size%/v}
  sizes["$v"]="$size"
  printf "[%d] %s — %s\n" "$index" "$v" "$size"
done

if [ $FORCE -eq 0 ]; then
  echo "\nDry run — no volumes removed. Re-run with --force to delete the above volumes."; exit 0
fi

read -p "Remove these ${#candidates[@]} volumes? Type 'yes' to confirm: " yn
if [ "$yn" != "yes" ]; then echo "Aborted."; exit 0; fi

for v in "${candidates[@]}"; do
  echo "Removing $v..."
  docker volume rm "$v" || echo "Failed to remove $v"
done

echo "Done."
