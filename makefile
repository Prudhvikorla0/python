dev:
	docker compose -p rightorigins_v3 -f ./docker/docker-compose.yml -f ./docker/docker-compose-dev.yml up --build

devdjshell:
	docker compose -p rightorigins_v3 -f ./docker/docker-compose.yml -f ./docker/docker-compose-dev.yml exec web python manage.py shell_plus  --settings=rightorigins_v3.settings.local

shell:
	docker compose -p rightorigins_v3 -f ./docker/docker-compose.yml -f ./docker/docker-compose-dev.yml exec web /bin/bash

test:
	docker compose -p rightorigins_v3 -f ./docker/docker-compose.yml -f ./docker/docker-compose-dev.yml exec web python manage.py test  --settings=rightorigins_v3.settings.local

prod:
	docker compose -p rightorigins_v3 -f ./docker/docker-compose.yml -f ./docker/docker-compose-prod.yml up --build -d

down:
	docker compose -p rightorigins_v3 -f ./docker/docker-compose.yml -f ./docker/docker-compose-dev.yml down

dev-logs:
	docker compose -p rightorigins_v3 -f ./docker/docker-compose.yml -f ./docker/docker-compose-dev.yml logs -f

prod-logs:
	docker compose -p rightorigins_v3 -f ./docker/docker-compose.yml -f ./docker/docker-compose-prod.yml logs -f

db:
	docker compose -p rightorigins_v3 -f ./docker/docker-compose.yml -f ./docker/docker-compose-dev.yml exec db -it -u postgres postgres psql

# Without docker
runserver:
	python3 manage.py runserver --settings rightorigins_v3.settings.local 0.0.0.0:8000

makemigrations:
	python3 manage.py makemigrations --settings rightorigins_v3.settings.local

migrate:
	python3 manage.py migrate --settings rightorigins_v3.settings.local

djshell:
	python3 manage.py shell --settings rightorigins_v3.settings.local

celery:
	DJANGO_SETTINGS_MODULE='rightorigins_v3.settings.local' celery -A rightorigins_v3 worker -l info

startdeps:
	docker compose -f ./docker/docker-compose.deps.yml up -d

stopdeps:
	docker compose -f ./docker/docker-compose.deps.yml down