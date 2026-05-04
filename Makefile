.PHONY: install test seed run build lint clean

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

clean:
	python -c "from pathlib import Path; import shutil; [shutil.rmtree(path, ignore_errors=True) for path in Path('.').rglob('__pycache__')]"
