.ONESHELL:

py := poetry run
python := $(py) python

package_dir := app
tests_dir := tests

code_dir := $(package_dir) $(tests_dir)


define setup_env
    $(eval ENV_FILE := $(1))
    @echo " - setup env $(ENV_FILE)"
    $(eval include $(1))
    $(eval export)
endef

.PHONY: reformat
reformat:
	$(py) black $(code_dir)
	$(py) isort $(code_dir) --profile black --filter-files

.PHONY: dev-docker
dev-docker:
	docker compose -f=docker-compose-dev.yml --env-file=.env up

.PHONY: test-docker
test-docker:
	docker compose -f=docker-compose-test.yml --env-file=.env.test up

.PHONY: dev-alembic
dev-alembic:
	$(call setup_env, .env)
	alembic -c alembic.ini  upgrade head

.PHONY: dev-bot
dev-bot:
	$(call setup_env, .env)
	python -m app.tgbot

.PHONY: tests
tests:
	$(call setup_env, .env.test)
	$(py) pytest $(tests_dir) --rootdir .

.PHONY: prod
prod:
	docker compose -f=docker-compose.yml --env-file=.env.dev up
