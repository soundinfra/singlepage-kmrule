build: style types test

update_latest:
	echo `date` > public/latest.txt

update_multiple:
	echo `date` > public/one.txt
	echo `date` > public/two.txt
remove_latest:
	rm -f public/latest.txt

publish:
	./publish.py --token=`cat .soundinfra_token` kmrule.com

publish_dryrun:
	./publish.py --dryrun -v --token=`cat .soundinfra_token` kmrule.com

publish_verbose:
	./publish.py -v --token=`cat .soundinfra_token` kmrule.com

publish_clean:
	./publish.py --clean --token=`cat .soundinfra_token` kmrule.com

test_multiple: update_multiple publish_verbose

test_put: update_latest publish

test_clean: update_latest publish remove_latest publish_clean

test:
	coverage run -m unittest discover
	coverage html
	coverage report --fail-under=90

types:
	mypy src tests

clean:
	rm -rf **/__pycache__
	rm -rf **/*.pyc

style:
	flake8
