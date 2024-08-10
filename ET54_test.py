from ET54 import ET54

el = ET54("ASRL/dev/ttyUSB1")

def trest_reset():
    el.reset()

def test_state():
    el.ch1.on()
    assert el.ch1.get_state() == "ON"

    el.ch1.off()
    assert el.ch1.get_state() == "OFF"

def test_mode():
    el.ch1.set_mode("CV")
    assert el.ch1.get_mode() == "CV"

    el.ch1.set_mode("cc")
    assert el.ch1.get_mode() == "CC"

    el.ch1.set_mode("CP")
    assert el.ch1.get_mode() == "CP"

    el.ch1.set_mode("CR")
    assert el.ch1.get_mode() == "CR"

    el.ch1.set_mode("CCCV")
    assert el.ch1.get_mode() == "CCCV"

    el.ch1.set_mode("CRCV")
    assert el.ch1.get_mode() == "CRCV"

    el.ch1.set_mode("tran")
    assert el.ch1.get_mode() == "TRAN"

    el.ch1.set_mode("LIST")
    assert el.ch1.get_mode() == "LIST"

    el.ch1.set_mode("shor")
    assert el.ch1.get_mode() == "SHOR"

    el.ch1.set_mode("batt")
    assert el.ch1.get_mode() == "BATT"

    el.ch1.set_mode("led")
    assert el.ch1.get_mode() == "LED"


def test_range():
    el.ch1.set_Vrange("HIGH")
    assert el.ch1.get_Vrange() == "HIGH"

    el.ch1.set_Vrange("low")
    assert el.ch1.get_Vrange() == "LOW"

    el.ch1.set_Crange("high")
    assert el.ch1.get_Crange() == "HIGH"

    el.ch1.set_Crange("low")
    assert el.ch1.get_Crange() == "LOW"

def test_
