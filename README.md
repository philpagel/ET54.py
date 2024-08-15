# ET54

Python class for remote controlling EastTester ET54 series electronic loads.

# Supported models

This *should* work with all of the following devices:

* ET5410
* ET5411
* ET5410A+
* ET5420A+
* ET5411A+

However, I have two different versions of the ET5410A+ but have no access to
any of the other models. If you own any of the other models and are willing to
do some testing, please get in touch.

## Mustool ET5410A+

There are *Mustool* branded version of the ET5410A+ and possibly also of the
other models. These devices run a modified firmware and return an empty model
ID (`xxxxxx`) in response to the `IDN?` command. To make these devices work,
you need to explicitly provide the model ID when initializing the device:

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
| LED mode                   | ✓      |  
| Short mode                 | ✓      |  
| Battery mode               | —      |  
| Transient mode             | —      |  
| List mode                  | —      |  

So basic functions are working and I'm in the process of
implementing the more involved things.


# Example script

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
            el.ch1.read.voltage(),
            el.ch1.read.current(),
            el.ch1.read.power(),
            el.ch1.read.resistance(),
        ]]))
        time.sleep(1)

    # turn off the load channel
    el.ch1.off()

