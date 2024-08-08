# ET54xx.py

Python class for remote controlling EastTester ET54 series electronic loads.

# Supported models

This *should* work with all of the following devices:

* ET5410
* ET5411
* ET5410A+
* ET5420A+
* ET5411A+

However, I only have two different ET5410A+ models and cannot test the others.
I'd be grateful for input from people who own any of the other models.

## Mustool ET5410A+

There are *Mustool* branded version of the ET5410A+ and possibly also of the
other models. These devices run a modified firmware and do not respond with a
model ID to the `IDN?` command (they show model number 'XXXXXX'). In
order to make these devices work, you need to explicitly provide the model ID
when initializing the device:

    import ET54xxx
    el = ET54xx.ET53xx("ASRL/dev/ttyUSB0", model="ET5410A+")


# Status

So far, basic functionality is supported but advanced features are still missing.

# Example script

    #!/bin/env python3
    import time, datetime
    from ET54 import ET54

    # connect to the load
    el = ET54("ASRL/dev/ttyUSB0")

    # set range (high|low)
    el.set_Vange("high")
    el.set_Cange("high")

    # start in constant current mode
    el.ch1.mode.CC(2.5)
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

