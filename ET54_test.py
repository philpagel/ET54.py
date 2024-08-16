import pytest
from ET54 import ET54
        
# Define parameters for setting voltage, current, power or resistance

heading = "V,I,P,R"
parameters = [
         (24.2, 14.0, 340.2,  1.74),
         (96.8,  4.0, 387.2,  24.2),
         ( 120,  2.2, 264.0,  54.5),
         ]

RID = "ASRL/dev/ttyUSB1"
el = ET54(RID)
ch = el.ch1

print("\nModel: ", el.idn["model"])
print("Firmware: ", el.idn["firmware"])
print("Hardware: ", el.idn["hardware"])

def test_write():

    # invalid command
    with pytest.raises(RuntimeError):
        el.write("FOOBAR:12")
    # failed command
    with pytest.raises(RuntimeError):
        el.write("VOLT1:10000")

def test_input_state():
    "setting and getting channel on/off state"

    ch.input("on")
    assert ch.input() == "ON"

    ch.input("OFF")
    assert ch.input() == "OFF"

    with pytest.raises(RuntimeError):
        assert ch.input("invalid")

    ch.on()
    assert ch.input() == "ON"

    ch.off()
    assert ch.input() == "OFF"

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

    ch.mode(mode)
    assert ch.mode() == value

def test_mode_invalid():
    "set an invalid mode"

    with pytest.raises(ValueError):
        ch.mode('invalid')

@pytest.mark.parametrize(
    "mode,value", 
    [("low", "LOW"), ("High", "HIGH")]
    )
def test_range(mode, value):
    "setting and getting voltage and current range"

    ch.Vrange(mode)
    assert ch.Vrange() == value

    ch.Crange(mode)
    assert ch.Crange() == value

def test_range_invalid():
    "test invalid range value"
    
    with pytest.raises(ValueError):
        ch.Vrange("invalid")
        ch.Crange("invalid")

@pytest.mark.parametrize("value", [0.5, 1.3, 2.9])
def test_OCP(value):
    "setting and getting OCP value"
    
    ch.OCP(value)
    assert ch.OCP() == value

def test_OCP_invalid():
    with pytest.raises(RuntimeError):
        ch.OCP(-10)

@pytest.mark.parametrize("value", [1.0, 3.4, 7.5, 18.5])
def test_OVP(value):
    "setting and getting OVP value"

    ch.OVP(value)
    assert ch.OVP() == value

def test_OVP_invalid():
    with pytest.raises(RuntimeError):
        ch.OVP(-10)

@pytest.mark.parametrize("value", [5.0, 50, 120])
def test_OPP(value):
    "setting and getting OPP value"

    ch.OPP(value)
    assert ch.OPP() == value

def test_OPP_invalid():
    with pytest.raises(RuntimeError):
        ch.OPP(-10)

@pytest.mark.parametrize(heading,parameters)
def test_CCmode(V, I, P, R):
    "setting and getting current in CC mode"

    ch.CC_mode(I)
    assert ch.CC_current() == I
    assert ch.CC_current(0.1) == 0.1
    assert ch.CC_current(I) == I
    assert ch.CC_current() == I

@pytest.mark.parametrize(heading,parameters)
def test_CVmode(V, I, P, R):
    "setting and getting voltage in CV mode"

    ch.CV_mode(V)
    assert ch.CV_voltage() == V
    assert ch.CV_voltage(0.1) == 0.1
    assert ch.CV_voltage(V) == V
    assert ch.CV_voltage() == V

@pytest.mark.parametrize(heading,parameters)
def test_CPmode(V, I, P, R):
    "setting and getting power in CP mode"

    ch.CP_mode(P)
    assert ch.CP_power() == P
    assert ch.CP_power(0.1) == 0.1
    assert ch.CP_power(P) == P
    assert ch.CP_power() == P

@pytest.mark.parametrize(heading,parameters)
def test_CRmode(V, I, P, R):
    "setting and getting resistance in CR mode"
    
    ch.CR_mode(R)
    assert ch.CR_resistance() == R 
    assert ch.CR_resistance(0.1) == 0.1
    assert ch.CR_resistance(R) == R
    assert ch.CR_resistance() == R

@pytest.mark.parametrize(heading,parameters)
def test_CCCVmode(V, I, P, R):
    "setting and getting voltage and current in CC+CV mode"

    ch.CCCV_mode(I, V)
    assert ch.CCCV_current() == I
    assert ch.CCCV_voltage() == V
    assert ch.CCCV_current(0.1) == 0.1
    assert ch.CCCV_voltage(0.1) == 0.1
    assert ch.CCCV_current(I) == I
    assert ch.CCCV_current() == I
    assert ch.CCCV_voltage(V) == V
    assert ch.CCCV_voltage() == V

@pytest.mark.parametrize(heading,parameters)
def test_CRCVmode(V, I, P, R):
    "setting and getting voltage and current in CC+CR mode"

    ch.CRCV_mode(R, V)
    assert ch.CRCV_resistance() == R
    assert ch.CRCV_voltage() == V
    assert ch.CRCV_voltage(0.1) == 0.1
    assert ch.CRCV_voltage(V) == V
    assert ch.CRCV_voltage() == V
    assert ch.CRCV_resistance(R) == R
    assert ch.CRCV_resistance() == R

def test_measure():
    """measuring voltage, current, power and resistance
    This requires tha the input terminals are *shorted*!
    If they are left floating, the test will fail!
    """

    el.ch1.on()
    assert ch.read_voltage() <= 0.01
    assert ch.read_current() <= 0.01
    assert ch.read_power() <= 0.01
    assert ch.read_resistance() <= 0.01
    (V,I,P,R) = ch.read_all()
    assert V <= 0.01
    assert I <= 0.01
    assert P <= 0.01
    assert R <= 0.01

    el.ch1.off()

