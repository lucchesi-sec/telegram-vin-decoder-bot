.PHONY: run install clean docker-build docker-run

run:
	python -m vinbot

install:
	pip install -r requirements.txt

docker-build:
	docker build -t vin-bot .

docker-run:
	docker run --rm --env-file .env vin-bot

clean:
	rm -rf __pycache__ vinbot/__pycache__ .venv
