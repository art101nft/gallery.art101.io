setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

shell:
	FLASK_SECRETS=config.py QUART_APP="gallery:create_app()" .venv/bin/quart shell

dev:
	python3 run.py

prod:
	.venv/bin/hypercorn run

up:
	docker-compose up -d

kill:
	pkill -e -f gallery
