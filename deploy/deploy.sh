#!/usr/bin/env bash
set -e

cd /var/www/barkova_app

git pull origin main
docker compose down
docker compose up -d --build
docker image prune -f