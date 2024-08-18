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
ch.off()
ch.CC_mode()

# most tets assum `high` range, so set it
ch.Vrange("high")
ch.Crange("high")


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

    ch.CC_mode()

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
    
    ch.OCP(value)
    assert ch.OCP() == value

def test_OCP_invalid():
    with pytest.raises(RuntimeError):
        ch.OCP(-10)

@pytest.mark.parametrize("value", [1.0, 3.4, 7.5, 18.5])
def test_OVP(value):

    ch.OVP(value)
    assert ch.OVP() == value

def test_OVP_invalid():
    with pytest.raises(RuntimeError):
        ch.OVP(-10)

@pytest.mark.parametrize("value", [5.0, 50, 120])
def test_OPP(value):

    ch.OPP(value)
    assert ch.OPP() == value

def test_OPP_invalid():
    with pytest.raises(RuntimeError):
        ch.OPP(-10)

@pytest.mark.parametrize(heading,parameters)
def test_CCmode(V, I, P, R):

    ch.CC_mode(I)
    assert ch.CC_current() == I
    assert ch.CC_current(0.1) == 0.1
    assert ch.CC_current(I) == I
    assert ch.CC_current() == I

@pytest.mark.parametrize(heading,parameters)
def test_CVmode(V, I, P, R):

    ch.CV_mode(V)
    assert ch.CV_voltage() == V
    assert ch.CV_voltage(0.1) == 0.1
    assert ch.CV_voltage(V) == V
    assert ch.CV_voltage() == V

@pytest.mark.parametrize(heading,parameters)
def test_CPmode(V, I, P, R):

    ch.CP_mode(P)
    assert ch.CP_power() == P
    assert ch.CP_power(0.1) == 0.1
    assert ch.CP_power(P) == P
    assert ch.CP_power() == P

@pytest.mark.parametrize(heading,parameters)
def test_CRmode(V, I, P, R):
    
    ch.CR_mode(R)
    assert ch.CR_resistance() == R 
    assert ch.CR_resistance(0.1) == 0.1
    assert ch.CR_resistance(R) == R
    assert ch.CR_resistance() == R

@pytest.mark.parametrize(heading,parameters)
def test_CCCVmode(V, I, P, R):

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

    ch.CRCV_mode(R, V)
    assert ch.CRCV_resistance() == R
    assert ch.CRCV_voltage() == V
    assert ch.CRCV_voltage(0.1) == 0.1
    assert ch.CRCV_voltage(V) == V
    assert ch.CRCV_voltage() == V
    assert ch.CRCV_resistance(R) == R
    assert ch.CRCV_resistance() == R

def test_BATTmode():
    
    ch.BATT_mode(mode="CC", value=[2.0,1.5,1.0], 
                 cutoff="V", cutoff_value=[15, 12, 10])
    assert ch.BATT_current() == [2.0, 1.5, 1.0]
    assert ch.BATT_cutoff() == "Voltage"
    assert ch.BATT_cutoff_value() == [15, 12, 10]

    ch.BATT_mode(mode="CC", value=1.25, cutoff="V", cutoff_value=2.5)
    assert ch.BATT_current() == [1.25] * 3
    assert ch.BATT_cutoff() == "Voltage"
    assert ch.BATT_cutoff_value() == [2.5] * 3

    ch.BATT_mode(mode="CC", value=[1.3, 0.97], cutoff="V", cutoff_value=[4,3,1])
    assert ch.BATT_current() == [1.3, 0.97, 0.97]
    assert ch.BATT_cutoff() == "Voltage"
    assert ch.BATT_cutoff_value() == [4, 3, 1]

    ch.BATT_mode(mode="CC", value=5.5, cutoff="T", cutoff_value=5)
    assert ch.BATT_current() == 5.5
    assert ch.BATT_cutoff() == "Time"
    assert ch.BATT_cutoff_value() == 5

    ch.BATT_mode(mode="CC", value=3.8, cutoff="E", cutoff_value=0.6)
    assert ch.BATT_current() == 3.8
    assert ch.BATT_cutoff() == "Energy"
    assert ch.BATT_cutoff_value() == 0.6

    ch.BATT_mode(mode="CC", value=1.2, cutoff="C", cutoff_value=0.7)
    assert ch.BATT_current() == 1.2
    assert ch.BATT_cutoff() == "Capacity"
    assert ch.BATT_cutoff_value() == 0.7

    ch.BATT_mode(mode="CR", value=500, cutoff="E", cutoff_value=0.5)
    assert ch.BATT_resistance() == 500
    assert ch.BATT_cutoff() == "Energy"
    assert ch.BATT_cutoff_value() == 0.5

    ch.BATT_mode(mode="CR", value=700, cutoff="C", cutoff_value=0.3)
    assert ch.BATT_resistance() == 700
    assert ch.BATT_cutoff() == "Capacity"
    assert ch.BATT_cutoff_value() == 0.3

def test_measure():
    """measuring voltage, current, power and resistance
    This requires tha the input terminals are *shorted*!
    If they are left floating, the test will fail!
    """

    el.ch1.on()
    assert ch.read_voltage() <= 0.02
    assert ch.read_current() <= 0.02
    assert ch.read_power() <= 0.02
    assert ch.read_resistance() <= 0.02
    (V,I,P,R) = ch.read_all()
    assert V <= 0.02
    assert I <= 0.02
    assert P <= 0.02
    assert R <= 0.02

    el.ch1.off()

