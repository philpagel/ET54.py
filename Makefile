RELEASE="0.1"

help:
	@echo "The following make targets are available:\n"
	@echo "   test         run automated test suite. Requires device to be connected."
	@echo "   build        build python package"
	@echo "   clean        clean up package and cruft"
.PHONEY: help

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


build: 
	python3 -m build
.PHONEY: build

clean:
	rm -rf dist
	rm -rf src/ET54.egg-info
	rm -rf src/ET54/__pycache__
	rm -rf src/tests/__pycache__
.PHONEY: clean
