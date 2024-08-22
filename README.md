# ET54

Python class for remote controlling EastTester ET54 series electronic loads.

# Supported models

This *should* work with all of the following devices:

* ET5410
* ET5411
* ET5420
* ET5410A+
* ET5411A+
* ET5420A+

And possibly also with these:

* ET5406A+
* ET5407A+

Testing was carried out on my ET5410A+. However, I have no access to any of the
other models. If you own one of them and are willing to do some testing, please
get in touch.

There are *Mustool* branded version of the ET5410A+ and possibly also of the
other models. These devices run a modified firmware and return an uninformative
model ID (`xxxxxx`) in response to the `*IDN?` SCPI command. To make these
devices work, you need to explicitly provide the model ID when initializing the
device:

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
| Battery mode               | ✓      |  
| Trigger support            | ✓      |
| Transient mode             | ✓      |  
| List mode                  | ✓      |  
| Qualification test mode    | —      |  
| File commands              | —      |
| Load effect testing        | —      |
| Remote compensation        | —      |

Basic functions are working and I'm in the process of
implementing the more involved things.

Trying to set invalid values will raise an exception (e.g. `RuntimeError` or
`ValueError`) based on the load's response and a few checks of my own.

I am pretty confident that the values that you set with this class are
correctly stored by the instrument because that's what all my test cases check
for.  However, I have not yet tested all functionality in enough real-live
circuits to be 100% confident that the load actually always behaves as
expected. If not, that may be a bug on my side or a problem in the device
firmware.

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
    el = ET54("ASRL/dev/ttyUSB1::INSTR")

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

## Some more details

### Connecting
    
This is how you connect to the load:

    from ET54 import ET54
    el = ET54("ASRL/dev/ttyUSB1")

Of course, you need to adapt it to the right device for your case.

## Channels

The load object itself does not do many exciting things. For the actual work,
it has one or two channels (depending on your model). You can access them like
so:

    el.ch1.CR_mode(1000)
    el.ch1.on()

Admittedly, most models only have one channel and the extra `.ch` part can get
annoying. To make things a little shorter, you can assign the channel to a
variable and use that directly:

    ch = el.ch1
    ch.CR_mode(1000)
    ch.on()

## Mode setup

All `*_mode()` methods will put the load into the respective mode and set
all relevant parameters so you don't have to do the configuration separately.
E.g. for CCCV mode:

    el.ch1.CCCV_mode(current=1.5, voltage=24)

or just 
    
    el.ch1.CCCV_mode(1.5, 24)

If, for some reason, you prefer to just set the mode and then configure it
separately, you can use `el.ch1.mode()` followed by the respective setup
commands, instead.

## Reading data

Once the load is set up and running, you can start reading measurement data
from it. There are four parameters you can get:

    el.ch1.read_voltage()
    el.ch1.read_current()
    el.ch1.read_power()
    el.ch1.read_resistance()

## Summary information

You can get all kinds of information form the various methods but if you
would like to see a human-readable summary of the device and its state, you 
can use the `__str__` method of the load object. E.g. by printing it:

    >>> print(el)
    Model:          ET5410A+
    Serial:         08772385097
    Firmware:       V1.00.2213.016
    Hardware:       V1.00.2213.016

    Channel 1
    Input state:    OFF
    Voltage range:  HIGH
    Current range:  HIGH
    OCP:            42.0 A
    OVP:            155.0 V
    OPP:            410.0 W
    mode:           CC
    Current:        2.0 A


## Some principles

The philosophy of the class is that there are no separate getter and setter
methods. Instead, most methods will return the latest setting and set
it if you provide an argument. Method names start with the mode
or functionality.

E.g. Constant current mode:

    el.ch1.CC_mode(2.8)         # switch to CC mode and set current to 2.8A

    el.ch1.CC_current()         # get CC current setting
    el.ch1.CC_current(1.5)      # set CC current to new value

## Reference

The full documentation is contained in the doc-strings of the class. Use
`pydoc` to see all of it:

    python -m pydoc ET54

## Trouble shooting

The SCPI implementation in the instrument is a bit wonky. I spent a lot of time
figuring out some peculiarities and have managed to fully crash the controller
many times. Many of these problems had to do with timing (some commands are
fast, others require some time before you may send a new command). The device
is also very picky about white space. Finally, the SCPI documentation is obscure
in some places and sometimes outright wrong.

It is quite possible that different models and/or firmware or hardware
revisions behave slightly different than my instrument. If you encounter
problems, you can try tweaking a few parameters:

| parameter  | Description                                               |
|----------  |---------------------------------------------------------  |
| `baudrate` | must match baudrate set in device (default: 9600)         |
| `eol_r`    | line terminator for reading from device (default: "\r\n") |
| `eol_w`    | line terminator for writing to device (default: "\n")     |
| `delay`    | delay after read/write operation [s] (default: 0.2)       |
| `timeout`  | timeout [ms] before giving up on `read` requests (default: 1000) |
| `model`    | model ID [ET5410/ET5420/ET541A+/...] <br> only required if `*IDN?` does not return a valid ID e.g. for Mustool branded ET5410A+ |

The most likely candidate to fix weird problems is `delay`. The device manual
does not specify what command frequency or processing time the instrument has
so I used the smallest value that allowed all my test cases to pass.

Example:

    el = ET54(delay=0.5, baudrate=14400)


If you want to play with the device on raw metal and try some SCPI commands
yourself, you can connect to it like so

    tio -e -b 9600 -m INLCRNL,OCRNL /dev/ttyUSB0

You can use other programs like minicom etc. Just make sure to get the weirdly
inconsistent line terminators right.


# Testing

I use pytest to implement a bunch of test cases in order to verify everything
is working as intended. As the tests involve talking to actual hardware, you
need to provide the necessary conditions for some tests to pass:

1. `ET54_test.py`: the input terminals of the load must be shorted so that the
   input voltage and current are 0.00
2. `ET54_test_voltage`: the input terminals of the load must be connected to a
   power supply that provides 12.0 V and can deliver 1.5A.

Install pytest

    python -m pip install pytest

To run the tests:
    
    # Short the input and run:
    pytest -v ET54_test.py

    # connect PSU (12V, >1.5A) an run:
    pytest -v ET54_test_voltage.py

As the load has no external sensing wires, the length and diameter of your test
leads matter. Keep them short and as big as you can. Using the lead
compensation feature of the device before starting the tests may help, too.

Currently, only channel 1 of the load is tested, even if you have a
2-channel device.

# Contributing

If you think you found a bug or you have an idea for a new feature, please open
an issue here on GitHub. Please **do not submit pull-requests before discussing
the issue** you want to address.

If you want to report a bug, please make sure to replicate the erroneous
behavior at least once before opening an issue and provide all information
necessary to replicate the problem (what commands did you use, what was
connected to the load, what did you observe, what did you expect?).

I would very much appreciate help from people who own any of the models listed
above (other than the ET5410A+) – no coding skills required: I just need people
to run the tests on these devices and report the results back to me. Get in
touch if you would like to do that.

