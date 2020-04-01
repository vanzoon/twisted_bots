SHELL = /bin/bash

run:
	twistd -n shittybot
cov:
	coverage run --branch --source talkback `which trial` tests/*.py
	coverage report
	coverage html

.PHONY: run cov
