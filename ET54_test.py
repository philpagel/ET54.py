import pytest
from ET54 import ET54

el = ET54("ASRL/dev/ttyUSB1")
print("\nModel: ", el.idn["model"])
print("Firmware: ", el.idn["firmware"])
print("Hardware: ", el.idn["hardware"])

def test_state():
    ch = el.ch1

    ch.on()
    assert ch.get_state() == "ON"

    ch.off()
    assert ch.get_state() == "OFF"

@pytest.mark.parametrize(
    "mode,value",
    [
        ("CV", "CV"),
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
    ]
        )
def test_mode(mode, value):
    ch = el.ch1

    ch.set_mode(mode)
    assert ch.get_mode() == value


@pytest.mark.parametrize(
    "mode,value", 
    [("High", "HIGH"), ("low", "LOW")]
    )
def test_range(mode, value):
    ch = el.ch1

    ch.set_Vrange(mode)
    assert ch.get_Vrange() == value

    ch.set_Crange(mode)
    assert ch.get_Vrange() == value


@pytest.mark.parametrize(
        "Crange,value",
        [("low", 0.1),
         ("low", 1.7),
         ("low", 2.8),
         ("high", 1.2),
         ("high", 24.1),
         ("high", 40),
         ])
def test_OCP(Crange, value):
    ch = el.ch1
    ch.set_Crange(Crange)

    ch.set_OCP(value)
    assert ch.get_OCP() == value

@pytest.mark.parametrize(
        "Crange,value",
        [("low", 0.1),
         ("low", 1.7),
         ("low", 2.8),
         ("high", 1.2),
         ("high", 24.1),
         ("high", 40),
         ])
def test_current(Crange, value):
    ch = el.ch1
    ch.set_Crange(Crange)

    ch.set_current_CC(value)
    assert ch.get_current_CC() == value

    ch.set_current_CCCV(value)
    assert ch.get_current_CCCV() == value

    ch.set_current_LED(value)
    assert ch.get_current_LED() == value

def test_measure():
    ch = el.ch1

    assert ch.read_voltage() < 0.5
    assert ch.read_current() < 0.5
    assert ch.read_power() < 0.5
    assert ch.read_resistance() < 0.5
    assert len(ch.read_all()) == 4

