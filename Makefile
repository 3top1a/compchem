# This makefile assumes it is ran inside the docker
# container, and is just a quicker way to set up
# the project

.PHONY: run initialize setup_deps setup_invenio reset_db

run:
	invenio run --cert adhoc --host 0.0.0.0

docker: setup_deps run
initialize: setup_deps reset_db setup_invenio

setup_deps:
	uv sync
	mkdir -p .venv/var/instance/
	cp invenio.cfg .venv/var/instance/invenio.cfg
	cp variables .venv/var/instance/variables

setup_invenio:
	uv run invenio oarepo assets collect .venv/var/instance/watch.list.json
	uv run invenio webpack clean create
	uv run invenio webpack install --legacy-peer-deps
	uv run invenio webpack build

reset_db:
	uv run invenio db destroy --yes-i-know || true
	uv run invenio db init create
	uv run invenio index destroy --force --yes-i-know || true
	uv run invenio index init
	uv run invenio oarepo cf init
	uv run invenio index queue init purge
	uv run invenio files location create --default 'default-location' file:///app/.venv/var/instance/data
	uv run invenio oarepo fixtures load
	uv run invenio users create admin@example.com --password=admin123 --active
	uv run invenio roles create admin
	uv run invenio access allow superuser-access role admin
	uv run invenio roles add admin@example.com admin
	@echo "Admin user: admin@example.com / password: admin123"

