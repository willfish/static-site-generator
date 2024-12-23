default: build
	cd public && python -m http.server 8888

build:
	python src/main.py

test:
	python -m unittest discover -s src
