import pytest, time
from ET54 import ET54
from .testconfig import *

el = ET54(RID)

def test_measure():
    """measuring voltage, current, power and resistance
    This test requires that the load is connected to a
    power supply delivering 12.0V @ > 1.5A
    """

    for ch in el.Channels:
        ch.Vrange = "low"
        ch.Crange = "low"   
        ch.CC_mode(1.5)
        ch.on()
        time.sleep(0.5) # wait a moment for the current to stabilize

        assert abs(ch.read_voltage() - 12.0) < 0.2
        assert abs(ch.read_current() - 1.5) < 0.2
        assert abs(ch.read_power() - 18) < 0.2
        assert abs(ch.read_resistance() - 8.0) < 0.2
        
        (I,V,P,R) = ch.read_all()
        assert abs(V - 12.0) < 0.2
        assert abs(I - 1.5) < 0.2
        assert abs(P - 18.0) < 0.2
        assert abs(R - 8.0) < 0.2
        
        ch.off()
