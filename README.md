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

This is work in progress. Basic functionality is implemented, many things are
still missing.  Hang on until I get it somewhat more complete and stable.


# Example script

    #!/bin/env python3
    import time, datetime
    from ET54 import ET54

    # connect to the load
    el = ET54("ASRL/dev/ttyUSB1")

    # set ranges
    el.set_Vange("high")
    el.set_Cange("high")

    # start in constant current mode
    el.ch1.mode("CC")
    el.ch1.set_currentCC(3)
    el.ch1.on()
    
    # monitor voltage, current and power for a minute
    print("timestamp, V, I, P")
    for i in range(60):
        print(", ".join([str(x) for x in [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            el.ch1.read.voltage(),
            el.ch1.read.curent(),
            el.ch1.read.power(),
        ]]))
        time.sleep(1)

    # turn off the load channel
    el.ch1.off()

