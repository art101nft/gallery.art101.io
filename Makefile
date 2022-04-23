setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

shell:
	bash manage.sh shell

dev:
	bash manage.sh run

prod:
	bash manage.sh prod

up:
	docker-compose up -d

huey:
	.venv/bin/huey_consumer gallery.tasks.huey -w 8

kill:
	pkill -e -f gallery
