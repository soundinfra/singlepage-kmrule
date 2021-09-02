test:
	python3 -m unittest discover

types:
	mypy src tests

clean:
	rm -rf __pycache__

build: types test