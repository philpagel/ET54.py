# ET54

Python class for remote controlling EastTester ET54 series electronic loads.

# Supported models

This *should* work with all of the following devices:

* ET5410
* ET5411
* ET5410A+
* ET5420A+
* ET5411A+

Testing was carried out on my ET5410A+. However, I have no access to any of the
other models. If you own one of them and are willing to do some testing, please
get in touch.

## Mustool ET5410A+

There are *Mustool* branded version of the ET5410A+ and possibly also of the
other models. These devices run a modified firmware and return an empty model
ID (`xxxxxx`) in response to the `*IDN?` SCPI command. To make these devices
work, you need to explicitly provide the model ID when initializing the device:

    from ET54 import ET54
    el = ET54("ASRL/dev/ttyUSB0", model="ET5410A+")


# Status

| Feature                    | Status |
|--------------------------- |------- |
| Input on/off               | ✓      |
| Voltage and current ranges | ✓      |
| V/A/R/P readout            | ✓      |  
| OCP, OVP, OPP              | ✓      |
| CC mode                    | ✓      |
| CV mode                    | ✓      |
| CP mode                    | ✓      |
| CR mode                    | ✓      |
| CC+CV mode                 | ✓      |
| CC+CR mode                 | ✓      |
| Short mode                 | ✓      |  
| LED mode                   | ✓      |  
| Battery mode               | —      |  
| Transient mode             | —      |  
| List mode                  | —      |  
| Qualification test mode    | —      |  
| Trigger support            | —      |
| File commands              | —      |

Basic functions are working and I'm in the process of
implementing the more involved things.


# Dependencies

The class requires `pyserial`, `pyvisa` and `pyvisa-py`, all of which can be
installed with pip:

    python -m pip install -r requirements.txt

If you want to run the automated tests you will also need `pytest`.

# Usage

## In a Nutshell

Here is a little example script that illustrates how things work:

    #!/bin/env python3
    import time, datetime
    from ET54 import ET54

    # connect to the load
    el = ET54("ASRL/dev/ttyUSB1")

    # set ranges
    el.ch1.Vrange("high")
    el.ch1.Crange("high")

    # set protections
    el.ch1.OVP(24.5)
    el.ch1.OCP(4)
    el.ch1.OPP(85)

    # start in constant current mode (3.1A)
    el.ch1.CC_mode(3.1)
    el.ch1.on()
    
    # monitor voltage, current, power and resistance for a minute
    print("timestamp, V, I, P, R")
    for i in range(60):
        print(", ".join([str(x) for x in [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            el.ch1.read_voltage(),
            el.ch1.read_current(),
            el.ch1.read_power(),
            el.ch1.read_resistance(),
        ]]))
        time.sleep(1)

    # turn off the load channel
    el.ch1.off()


## Some principles

The philosophy of the class is that there are no separate getter and setter
methods. Instead, most methods will return the latest setting and set
it if you provide an argument. Method names start with the mode
or functionality.

E.g. Constant current mode:

    el.CC_mode(2.8)         # switch to CC mode and set current to 2.8A

    el.CC_curent()          # get CC current setting
    el.CC_current(1.5)      # set CC current to new value


## Reference

The full documentation is contained in the doc-strings of the class. Use
`pydoc` to see all of it:

    python -m pydoc ET54


# Testing

I use pytest to implement a bunch of test cases in order to verify everything
is working as intended. As the tests involve talking to actual hardware, you
need to provide the necessary conditions for some tests to pass:

1. `ET54_test.py`: the input terminals of the load must be shorted so that the
   input voltage is 0.0V.
2. `ET54_test_voltage`: the input terminals of the load must be connected to a
   power supply that provides 12.0 V and can deliver 1.5A.

Install pytest

    python -m pip install pytest

To run the tests:

    make test

Or if you don't have `make` on your machine:
    
    # Short the input and run:
    pytest -v ET54_test.py

    # connect PSU (12V, >1.5A) an run:
    pytest -v ET54_test_voltage.py

As the load has no external sensing wires, the length and diameter of your test
leads matters. Keep them short and as big as you can. Using the lead
compensation feature of the device before startung the tests may help, too.

Currently, only channel 1 of the load is tested, even if you have a
2-channel device.

# Contributing

If you think you found a bug or you have an idea for a new feature, please open
an issue here on GitHub. Please **do not submit pull-requests before discussing
the issue** you want to address.

I would very much appreciate help from people who own any of the models listed
above (other than the ET5410A+) – no coding skills required: I just need people
to run the tests on these devices and report the results back to me. Get in
touch if you would like to do that.

