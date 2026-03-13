# This makefile assumes it is ran inside the docker
# container, and is just a quicker way to set up
# the project

.PHONY: run initialize setup_deps setup_invenio reset_db

run:
	invenio run --cert adhoc --host 0.0.0.0

initialize: setup_deps reset_db setup_invenio

setup_deps:
	uv sync
	mkdir -p .venv/var/instance/
	cp invenio.cfg .venv/var/instance/invenio.cfg
	cp variables .venv/var/instance/variables

setup_invenio:
	invenio oarepo assets collect .venv/var/instance/watch.list.json
	invenio webpack clean create
	invenio webpack install --legacy-peer-deps
	invenio webpack build

reset_db:
	invenio db init
	invenio alembic upgrade heads
	invenio index init
	invenio index queue init purge
	invenio oarepo fixtures load
	invenio users create admin@example.com --password=admin --active
	invenio roles create admin
	invenio access allow superuser-access role admin
	invenio roles add admin@example.com admin
	@echo "Admin user: admin@example.com / password: admin"

