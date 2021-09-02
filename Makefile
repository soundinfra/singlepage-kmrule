build: style types test

test:
	python3 -m unittest discover

types:
	mypy src tests

clean:
	rm -rf **/__pycache__
	rm -rf **/*.pyc

style:
	flake8
