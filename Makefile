all:
	sudo python2 setup.py

test:
	python2 test/searchTest.py
	python2 test/download.py

