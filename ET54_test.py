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
    "mode", ["MAN", "EXT", "TRG"]
    )
def test_trigmode(mode):
    "get/set trigger mode"
    
    ch.trigger_mode(mode)
    assert ch.trigger_mode() == mode

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
    ch.CC_current(0.1)  # change value before next test
    ch.CC_current() == 0.1
    ch.CC_current(I) == I
    assert ch.CC_current() == I

@pytest.mark.parametrize(heading,parameters)
def test_CVmode(V, I, P, R):

    ch.CV_mode(V)
    assert ch.CV_voltage() == V
    ch.CV_voltage(0.1)
    ch.CV_voltage(V)
    assert ch.CV_voltage() == V

@pytest.mark.parametrize(heading,parameters)
def test_CPmode(V, I, P, R):

    ch.CP_mode(P)
    assert ch.CP_power() == P
    ch.CP_power(0.1)
    ch.CP_power(P)
    assert ch.CP_power() == P

@pytest.mark.parametrize(heading,parameters)
def test_CRmode(V, I, P, R):
    
    ch.CR_mode(R)
    assert ch.CR_resistance() == R 
    ch.CR_resistance(0.1)
    ch.CR_resistance(R)
    assert ch.CR_resistance() == R

@pytest.mark.parametrize(heading,parameters)
def test_CCCVmode(V, I, P, R):

    ch.CCCV_mode(I, V)
    assert ch.CCCV_current() == I
    assert ch.CCCV_voltage() == V
    ch.CCCV_current(0.1)
    ch.CCCV_current(I)
    assert ch.CCCV_current() == I
    ch.CCCV_voltage(V)
    assert ch.CCCV_voltage() == V

@pytest.mark.parametrize(heading,parameters)
def test_CRCVmode(V, I, P, R):

    ch.CRCV_mode(R, V)
    assert ch.CRCV_resistance() == R
    assert ch.CRCV_voltage() == V
    ch.CRCV_voltage(0.1)
    ch.CRCV_voltage(V)
    assert ch.CRCV_voltage() == V
    ch.CRCV_resistance(R)
    assert ch.CRCV_resistance() == R

@pytest.mark.parametrize(
        "mode,value,cutoff,cutoff_value", [
            ("CC", (2.0, 1.5, 1.10), "Voltage", (2.0, 1.5, 1.0)),
            ("CC", 5.5, "Time", 5),
            ("CC", 3.8, "Energy", 0.6),
            ("cc", 1.2, "Capacity", 0.7),
            ("CR", 500, "Energy", 0.5),
            ("cr", 700, "Capacity", 0.3),
            ])
def test_BATTmode(mode, value, cutoff, cutoff_value):
    
    ch.BATT_mode(mode=mode, value=value, cutoff=cutoff[0], cutoff_value=cutoff_value)
    mode = mode.upper()
    assert ch.BATT_submode() == mode
    if mode == "CC":
        assert ch.BATT_current() == value
    elif mode =="CR":
        assert ch.BATT_resistance() == value
    else:
        raise RuntimeError(f"Invalid submode {mode}.")
    assert ch.BATT_cutoff() == cutoff
    assert ch.BATT_cutoff_value() == cutoff_value

def test_BATTmode_expand():
    "Test the auto expansion of triples"

    ch.BATT_mode(mode="CC", value=1.25, cutoff="V", cutoff_value=2.5)
    assert ch.BATT_current() == (1.25, 1.25, 1.25)
    assert ch.BATT_cutoff_value() == (2.5, 2.5, 2.5)

    ch.BATT_mode(mode="CC", value=(1.3, 0.97), cutoff="V", cutoff_value=(4.1, 3.7))
    assert ch.BATT_current() == (1.3, 0.97, 0.97)
    assert ch.BATT_cutoff_value() == (4.1, 3.7, 3.7)


@pytest.mark.parametrize(
        "mode,trigmode,value,width",[
            ("CC", "COUT", (1, 3.8), (50, 100)),
            ("cc", "PULS", (2, 8), (100, 200)),
            ("CC", "Trig", (3, 9.5), (500, 250)),
            ("CC", "COUT", (7.5, 11.7), (2000, 500)),
            ("cV", "COUT", (2.1, 3.9), (50, 100)),
            ("Cv", "PULS", (2.2, 8.1), (100, 200)),
            ("CV", "TriG", (3.4, 9.4), (500, 250)),
            ("CV", "COuT", (7.3, 11.2), (2000, 500)),
            ]
        )
def testTRANSIENTmode(mode, trigmode, value, width):
    "test TRANSIENT mode setup"

    ch.TRANSIENT_mode(mode=mode, trigmode=trigmode, value=value, width=width)
    assert ch.TRANSIENT_submode() == mode.upper()
    assert ch.TRANSIENT_trigmode() == trigmode.upper()
    if mode.upper() == "CC":
        assert ch.TRANSIENT_current() == value
    else:
        assert ch.TRANSIENT_voltage() == value
    assert ch.TRANSIENT_width() == width

def test_measure():
    """measuring voltage, current, power and resistance
    This requires tha the input terminals are *shorted*!
    If they are left floating, the test will fail!
    """

    el.ch1.CC_mode(1.0)
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

