build: style types test

publish:
	./publish.py kmrule.com --token=`cat .soundinfra_token`

test:
	python3 -m unittest discover

types:
	mypy src tests

clean:
	rm -rf **/__pycache__
	rm -rf **/*.pyc

style:
	flake8
