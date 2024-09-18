VERSION="0.0.1"

help:
	@echo "The following make targets are available:\n"
	@echo "   dep          install dependencies (requirements)"
	@echo "   dep-dev      install dependencies for packaging"
	@echo "   test         run automated test suite. Requires device to be connected."
	@echo "   build        build python package"
	@echo "   install      install python package"
	@echo "   pypi         upload package to pypi"
	@echo "   clean        clean up package and cruft"
.PHONEY: help


dep:
	python -m pip install -r requirements.txt
.PHONEY: dep


test:
	@echo "Please follow these steps:\n"
	@echo "    1. Short the device inputs with a test lead."
	@echo "    2. Connect the device via usb"
	@echo "    3. edit 'src/tests/testconfig.py' so it matches your USB device"
	@echo "    4. Turn on the load\n"
	@echo "Hit ENTER to start the test suite"
	@read RESPONSE
	pytest -v src/tests/ET54_test.py
	@echo "Please follow these steps:\n"
	@echo "    1. Remove the shorting test lead."
	@echo "    2. Connect the load to a power supply set to 12.0V (>1.5A)."
	@echo "Hit ENTER to start the test suite"
	@read RESPONSE
	pytest -v src/tests/ET54_test_voltage.py
.Phoney: test


dep-dev:
	python -m pip install -r requirements-dev.txt --upgrade
.PHONEY: dep-dev

build: 
	python -m build
.PHONEY: build


install: 
	python -m pip install dist/et54-$(VERSION).tar.gz
.PHONEY: install


pypi:
	twine upload dist/*
.PHONEY: pypi


clean:
	rm -rf dist
	rm -rf src/ET54.egg-info
	rm -rf src/ET54/__pycache__
	rm -rf src/tests/__pycache__
.PHONEY: clean
