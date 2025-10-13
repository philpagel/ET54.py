# Running the test suite

I use `pytest` for testing, so make sure that it's installed before moving
forward.

As the tests interact with a physical device, they only work if one of the
supported electronic load models is actually connected to the computer running
the tests. The load must be wired up differently for the different test files,
so you cannot just run all at once (`pythest ./`). Instead, run them one by one
as described in the following.

## General setup

1. Go to the text directory.  
```
cd src/test/
```
2. Connect the load to your computer and power it up.
3. Edit `testconfig.py` to match your situation.


## General test w/o power source

Before running these tests, please short the input terminals of the load with a
test lead. This is required for some readout tests to run successfully.

Run the tests

    pytest ET54_test.py

If you want to record the test results – e.g. when reporting a problem or when
confirming that this works on a model I don't have, please redirect `STDOUT` to
a file:

    pytest ET54_test.py > pytest1.log

## Test with power source attached

Before running these tests, connect the load to a lab power supply that is set
to 12.0V and a current limit of >1.5A. Then turn on the PSU output and run the tests:

    pytest ET54_test_voltage.py

If you want to record the test results – e.g. when reporting a problem or when
confirming that this works on a model I don't have, please redirect `STDOUT` to
a file:

    pytest ET54_test_voltage.py > pytest2.log



