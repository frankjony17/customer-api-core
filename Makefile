# Include the .env file
include .env

SHELL := /bin/bash

.PHONY: export-vars
export-vars:
	@while IFS= read -r line; do export $$line; done < <(grep -E '^(POSTGRES_USER|POSTGRES_PASS|POSTGRES_NAME|POSTGRES_PORT|APP_PORT|APP_HOST|APP_NAME|ENVIRONMENT|NETWORK_NAME|LOG_MAX_SIZE|LOG_MAX_FILE)=' .env | sed 's/#.*//')
	$(eval DOCKER_COMPOSE_FILENAME=$(if $(filter $(ENVIRONMENT),production),docker-compose.yml,docker-compose.dev.yml))

.PHONY: install
## Poetry lock and install
install:
	@poetry lock --no-update
	@poetry install

.PHONY: update
## Poetry Update
update:
	@poetry update

.PHONY: pytest
## Run pytest
pytest: export-vars
	@echo "Running pytest"
	poetry run pytest -vvv --cov=${APP_NAME} --cov-fail-under=90

.PHONY: pytest-report
## Run pytest
pytest-report: export-vars
	@echo "Running pytest"
	poetry run pytest -vv --cov=${APP_NAME} --cov-report=term-missing --cov-fail-under=90

.PHONY: clean
## Clean project python cache files
clean:
	@echo "Cleaning Python cache files"
	find . -type f -name '*.py[co]' -exec rm -f {} +
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@echo "Cache cleared!"

.PHONY: check
## Tool for static code analysis
check: mypy bandit ruff-check

flake: export-vars
	@echo "Running Flake8"
	poetry run flake8 ./${APP_NAME} ./tests

pylint: export-vars
	@echo "Running Pylint"
	poetry run pylint ./${APP_NAME}/

mypy: export-vars
	@echo "Running Mypy"
	poetry run mypy ./${APP_NAME}/

bandit: export-vars
	@echo "Running Bandit"
	poetry run bandit -v -r ./${APP_NAME}/ -c "pyproject.toml"

ruff-check: export-vars
	@echo "Running Ruff Check"
	poetry run ruff check --fix ./${APP_NAME}/ ./tests


.PHONY: format
## Tool For Style Guide Enforcement
format: ruff-format

ruff-format: export-vars
	@echo "Running Ruff Format"
	poetry run ruff format ./${APP_NAME}/ ./tests ./migrations

isort: export-vars
	@echo "Running isort"
	poetry run isort ./${APP_NAME} ./tests ./migrations

black: export-vars
	@echo "Running Black"
	poetry run black ./${APP_NAME} ./tests ./migrations --line-length=99


.PHONY: migrations
## Run migrations
migrations:
	@poetry run alembic upgrade heads

.PHONY: run
## Run local service
run: export-vars
	@poetry run uvicorn ${APP_NAME}.main:app --host ${APP_HOST} --port ${APP_PORT} --reload
.PHONY: run

.PHONY: postgres
## Local Postgres Database
postgres: export-vars create-network
	@docker run -d --name local-postgres \
	-e POSTGRES_USER=${POSTGRES_USER} \
	-e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
	-e POSTGRES_DB=${POSTGRES_DB} \
	-e PGPORT=${POSTGRES_PORT} \
	-p ${POSTGRES_PORT}:${POSTGRES_PORT} \
	-v db_data:/var/lib/postgresql/data \
	--log-driver json-file \
	--log-opt max-size=${LOG_MAX_SIZE} \
	--log-opt max-file=${LOG_MAX_FILE} \
	--health-cmd="pg_isready --username ${POSTGRES_USER} --dbname ${POSTGRES_DB}" \
	--health-interval=10s \
	--health-start-period=3s \
	--network=${NETWORK_NAME} \
	-it --rm postgres:15.2-alpine

### DOCKER COMPOSE TARGETS
.PHONY: build
## Build services
build: export-vars
	@docker compose -f ${DOCKER_COMPOSE_FILENAME} build

.PHONY: create-network
## Prepare the external network to be used with compose
create-network: export-vars
	@if [ -z "$$(docker network ls | grep ${NETWORK_NAME})" ]; then \
		docker network create ${NETWORK_NAME}; \
	fi

.PHONY: up
## Run services with compose
up: export-vars create-network
	docker compose -f ${DOCKER_COMPOSE_FILENAME} up -d --remove-orphans

.PHONY: up_api
## Run services with compose
up_api: export-vars create-network
	docker compose -f ${DOCKER_COMPOSE_FILENAME} up python-microservice-template-api-core -d --remove-orphans

.PHONY: down
## Tear down services with compose
down: export-vars
	docker compose -f ${DOCKER_COMPOSE_FILENAME} down
	docker container prune -f
	docker network prune -f
	docker volume prune -f

.PHONY: compose_clean
## Clean, kill and remove all containers and volumes
compose_clean:
	docker compose kill | true
	docker compose down -v --remove-orphans | true
	docker compose rm -f | true

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
