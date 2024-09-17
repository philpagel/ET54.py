#!/bin/env python3
import time, datetime
from ET54 import ET54

# connect to the load
el = ET54("ASRL/dev/ttyUSB1::INSTR")

# set ranges
el.ch1.Vrange = "high"
el.ch1.Crange = "high"

# set protections
el.ch1.OVP = 24.5
el.ch1.OCP = 4
el.ch1.OPP = 85

# start in constant current mode (3.1A)
el.ch1.CC_mode(3.1)
el.ch1.on()

# switch to CCCV mode
el.ch1.CCCV_mode(2.5, 13.5)
# and change the current on the way
el.ch1.CCCV.current = 1.25

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
