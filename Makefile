.phoney: help test requirements requirements-dev

help:
	@echo The following targets are available at the moment
	@echo 
	@echo "test                 run the test suite"
	@echo "requirements         install required python packages"
	@echo "requirements-dev     install required python packages for testing"

test:
	# run the test suite
	@echo
	@echo "    Connect the electronic load (via USB)."
	@echo "    Short the load input(s) with a test lead."
	@read -p "    Press <ENTER> when done." REPLY
	pytest -v ET54_test.py
	@echo
	@echo "    Remove the short from the output and"
	@echo "    Connect a power source to the load input(s)."
	@echo "    Set the voltage to 12.0V and allow at least 1.5A of current"
	@echo "    Turn on the power supply"
	@read -p "    Press <ENTER> when done." REPLY
	pytest -v ET54_test_voltage.py

requirements:
	# install requireed python modules
	python -m pip install -r requirements.txt

requirements-dev:
	# install requireed python modules for testing
	python -m pip install -r requirements-dev.txt
