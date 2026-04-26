#!/bin/bash
# Utils tool bash command for resetting Database

VERSION="v1__init_db"

echo "Setup.. Database version ${VERSION}"
docker compose exec -T db mariadb -uroot -ppassword -e "DROP DATABASE IF EXISTS template;"
docker compose exec -T db mariadb -uroot -ppassword -e "create database template;"
docker compose exec -T db mariadb -uroot -ppassword template < ./snapshots/${VERSION}.sql
echo "Setup Database successfully"
docker compose restart
exit 0
