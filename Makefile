setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

shell:
	bash manage.sh shell

dev:
	python3 run.py

huey:
	.venv/bin/huey_consumer gallery.tasks.huey -w 1

prod:
	.venv/bin/hypercorn run

up:
	docker-compose up -d

kill:
	pkill -e -f gallery
