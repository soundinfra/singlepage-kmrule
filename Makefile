build: style types test

update_latest:
	echo `date` > public/latest.txt

publish:
	./publish.py --token=`cat .soundinfra_token` kmrule.com

publish_dryrun:
	./publish.py --dryrun -v --token=`cat .soundinfra_token` kmrule.com

publish_verbose:
	./publish.py -v --token=`cat .soundinfra_token` kmrule.com

publish_clean:
	./publish.py --clean --token=`cat .soundinfra_token` kmrule.com

test_put: update_latest publish

test:
	python3 -m unittest discover

types:
	mypy src tests

clean:
	rm -rf **/__pycache__
	rm -rf **/*.pyc

style:
	flake8
