import pytest
from ET54 import ET54

RID = ET54("ASRL/dev/ttyUSB1")
# connect to the device
el = ET54(RID)

print("\nModel: ", el.idn["model"])
print("Firmware: ", el.idn["firmware"])
print("Hardware: ", el.idn["hardware"])

def test_state():
    "setting and getting channel on/off state"
    ch = el.ch1

    ch.on()
    assert ch.get_state() == "ON"

    ch.off()
    assert ch.get_state() == "OFF"

@pytest.mark.parametrize(
    "mode,value",
    [("CV", "CV"),
     ("cc", "CC"),
     ("CP", "CP"),
     ("cr", "CR"),
     ("CCCV", "CCCV"),
     ("CRcv", "CRCV"),
     ("tran", "TRAN"),
     ("LIST", "LIST"),
     ("SHOR", "SHOR"),
     ("batt", "BATT"),
     ("led", "LED"),
    ])
def test_mode(mode, value):
    "setting and getting operation mode"
    ch = el.ch1

    ch.set_mode(mode)
    assert ch.get_mode() == value


@pytest.mark.parametrize(
    "mode,value", 
    [("High", "HIGH"), ("low", "LOW")]
    )
def test_range(mode, value):
    "setting and getting voltage and current range"
    ch = el.ch1

    ch.set_Vrange(mode)
    assert ch.get_Vrange() == value

    ch.set_Crange(mode)
    assert ch.get_Vrange() == value


@pytest.mark.parametrize(
        "Vrange,Crange,value",
        [("low", "low", 0.1),
         ("low", "low", 1.7),
         ("low", "low", 2.8),
         ("low", "high", 1.2),
         ("low", "high", 24.1),
         ("low", "high", 40),
         ("high", "low", 0.1),
         ("high", "low", 1.7),
         ("high", "low", 2.8),
         ("high", "high", 1.2),
         ("high", "high", 24.1),
         ("high", "high", 40),
         ])
def test_OCP(Vrange, Crange, value):
    "setting and getting over current protection value"
    ch = el.ch1
    ch.set_Vrange(Vrange)
    ch.set_Crange(Crange)

    ch.set_OCP(value)
    assert ch.get_OCP() == value

@pytest.mark.parametrize(
        "Vrange,Crange,value",
        [("low", "low", 0.1),
         ("low", "low", 1.7),
         ("low", "low", 2.8),
         ("low", "high", 1.2),
         ("low", "high", 24.1),
         ("low", "high", 40),
         ("high", "low", 0.1),
         ("high", "low", 1.7),
         ("high", "low", 2.8),
         ("high", "high", 1.2),
         ("high", "high", 24.1),
         ("high", "high", 40),
         ])
def test_OPP(Vrange, Crange, value):
    "setting and getting over power protection value"
    ch = el.ch1
    ch.set_Crange(Crange)

    ch.set_OPP(value)
    assert ch.get_OPP() == value

@pytest.mark.parametrize(
        "Vrange,Crange,value",
        [("low", "low", 0.1),
         ("low", "low", 1.7),
         ("low", "low", 2.8),
         ("low", "high", 1.2),
         ("low", "high", 24.1),
         ("low", "high", 40),
         ("high", "low", 0.1),
         ("high", "low", 1.7),
         ("high", "low", 2.8),
         ("high", "high", 1.2),
         ("high", "high", 24.1),
         ("high", "high", 40),
         ])
def test_current(Vrange, Crange, value):
    "setting and getting current"
    ch = el.ch1
    ch.set_Crange(Crange)

    ch.set_current_CC(value)
    assert ch.get_current_CC() == value

    ch.set_current_CCCV(value)
    assert ch.get_current_CCCV() == value

    ch.set_current_LED(value)
    assert ch.get_current_LED() == value

def test_measure():
    "measuring voltage, current, power and resistance"
    ch = el.ch1

    assert ch.read_voltage() < 0.1
    assert ch.read_current() < 0.1
    assert ch.read_power() < 0.1
    assert ch.read_resistance() < 0.1
    assert len(ch.read_all()) == 4

