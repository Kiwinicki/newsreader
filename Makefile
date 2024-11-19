install:
	poetry install --no-root

run:
	poetry run uvicorn newsreader.main:app --reload

test:
	poetry run pytest ./tests -vv

update:
	poetry update

format:
	poetry run ruff format .

check:
	poetry run ruff format --check .
	poetry run mypy newsreader/
