.PHONY: install test seed run build lint docker-build docker-run ci clean

install:
	pip install -r requirements.txt

test:
	pytest -q

seed:
	python seed.py

run:
	flask --app app run --debug

build: test
	python -m compileall app.py models.py seed.py

lint:
	python -m py_compile app.py models.py seed.py

docker-build:
	docker build -t internal-tool-directory .

docker-run:
	docker run --rm -p 5000:5000 internal-tool-directory

ci:
	pytest -q tests/test_security_owasp.py

clean:
	python -c "from pathlib import Path; import shutil; [shutil.rmtree(path, ignore_errors=True) for path in Path('.').rglob('__pycache__')]"
