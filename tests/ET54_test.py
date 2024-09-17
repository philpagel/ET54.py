import pytest
from ET54 import ET54
from .testconfig import *

# Define parameters for setting voltage, current, power or resistance
heading = "V,I,P,R"
parameters = [
    (24.2, 14.0, 340.2, 1.74),
    (96.8, 4.0, 387.2, 24.2),
    (120, 2.2, 264.0, 54.5),
]


el = ET54(RID)

for ch in el.Channels:
    ch.off()
    ch.CC_mode(0.1)
    # most tests assum `high` range, so set it
    ch.Vrange = "high"
    ch.Crange = "high"

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

    for ch in el.Channels:
        ch.CC_mode(0.1)

        ch.input = "on"
        assert ch.input == "ON"

        ch.input = "OFF"
        assert ch.input == "OFF"

        with pytest.raises(RuntimeError):
            ch.input = "invalid"

        ch.on()
        assert ch.input == "ON"

        ch.off()
        assert ch.input == "OFF"


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
    ],
)
def test_mode(mode, value):
    "setting and getting operation mode"

    for ch in el.Channels:
        ch.mode = mode
        assert ch.mode == value


def test_mode_invalid():
    "set an invalid mode"

    for ch in el.Channels:
        with pytest.raises(ValueError):
            ch.mode = "invalid"


@pytest.mark.parametrize("mode", ["MAN", "EXT", "TRG"])
def test_trigmode(mode):
    "get/set trigger mode"

    for ch in el.Channels:
        ch.trigger_mode = mode
        assert ch.trigger_mode == mode


@pytest.mark.parametrize("mode,value", [("low", "LOW"), ("High", "HIGH")])
def test_range(mode, value):
    "setting and getting voltage and current range"

    for ch in el.Channels:
        ch.Vrange = mode
        assert ch.Vrange == value

        ch.Crange = mode
        assert ch.Crange == value


def test_range_invalid():
    "test invalid range value"

    for ch in el.Channels:
        with pytest.raises(ValueError):
            ch.Vrange = "invalid"
            ch.Crange = "invalid"


@pytest.mark.parametrize("value", [0.5, 1.3, 2.9])
def test_OCP(value):
    for ch in el.Channels:
        ch.OCP = value
        assert ch.OCP == value


def test_OCP_invalid():
    for ch in el.Channels:
        with pytest.raises(RuntimeError):
            ch.OCP = -10


@pytest.mark.parametrize("value", [1.0, 3.4, 7.5, 18.5])
def test_OVP(value):
    for ch in el.Channels:
        ch.OVP = value
        assert ch.OVP == value


def test_OVP_invalid():
    for ch in el.Channels:
        with pytest.raises(RuntimeError):
            ch.OVP = -10


@pytest.mark.parametrize("value", [5.0, 50, 120])
def test_OPP(value):
    for ch in el.Channels:
        ch.OPP = value
        assert ch.OPP == value


def test_OPP_invalid():
    for ch in el.Channels:
        with pytest.raises(RuntimeError):
            ch.OPP = -10


@pytest.mark.parametrize(heading, parameters)
def test_CCmode(V, I, P, R):
    for ch in el.Channels:
        ch.CC_mode(I)
        assert ch.CC_current == I
        ch.CC_currenti = 0.1  # change value before next test
        ch.CC_current == 0.1
        ch.CC_current = I
        assert ch.CC_current == I


@pytest.mark.parametrize(heading, parameters)
def test_CVmode(V, I, P, R):
    for ch in el.Channels:
        ch.CV_mode(V)
        assert ch.CV_voltage == V
        ch.CV_voltage = 0.1
        ch.CV_voltage = V
        assert ch.CV_voltage == V


@pytest.mark.parametrize(heading, parameters)
def test_CPmode(V, I, P, R):
    for ch in el.Channels:
        ch.CP_mode(P)
        assert ch.CP_power == P
        ch.CP_power = 0.1
        ch.CP_power = P
        assert ch.CP_power == P


@pytest.mark.parametrize(heading, parameters)
def test_CRmode(V, I, P, R):
    for ch in el.Channels:
        ch.CR_mode(R)
        assert ch.CR_resistance == R
        ch.CR_resistance = 0.1
        ch.CR_resistance = R
        assert ch.CR_resistance == R


@pytest.mark.parametrize(heading, parameters)
def test_CCCVmode(V, I, P, R):
    for ch in el.Channels:
        ch.CCCV_mode(I, V)
        assert ch.CCCV_current == I
        assert ch.CCCV_voltage == V
        ch.CCCV_current = 0.1
        ch.CCCV_current = I
        assert ch.CCCV_current == I
        ch.CCCV_voltage = V
        assert ch.CCCV_voltage == V


@pytest.mark.parametrize(heading, parameters)
def test_CRCVmode(V, I, P, R):
    for ch in el.Channels:
        ch.CRCV_mode(R, V)
        assert ch.CRCV_resistance == R
        assert ch.CRCV_voltage == V
        ch.CRCV_voltage = 0.1
        ch.CRCV_voltage = V
        assert ch.CRCV_voltage == V
        ch.CRCV_resistance = R
        assert ch.CRCV_resistance == R


@pytest.mark.parametrize(
    "mode,value,cutoff,cutoff_value",
    [
        ("CC", (2.0, 1.5, 1.10), "Voltage", (2.0, 1.5, 1.0)),
        ("CC", 5.5, "Time", 5),
        ("CC", 3.8, "Energy", 0.6),
        ("cc", 1.2, "Capacity", 0.7),
        ("CR", 500, "Energy", 0.5),
        ("cr", 700, "Capacity", 0.3),
    ],
)
def test_BATTmode(mode, value, cutoff, cutoff_value):
    for ch in el.Channels:
        ch.BATT_mode(mode=mode, value=value, cutoff=cutoff[0], cutoff_value=cutoff_value)
        mode = mode.upper()
        assert ch.BATT_submode == mode
        if mode == "CC":
            assert ch.BATT_current == value
        elif mode == "CR":
            assert ch.BATT_resistance == value
        else:
            raise RuntimeError(f"Invalid submode {mode}.")
        assert ch.BATT_cutoff == cutoff
        assert ch.BATT_cutoff_value == cutoff_value


def test_BATTmode_expand():
    "Test the auto expansion of triples"

    for ch in el.Channels:
        ch.BATT_mode(mode="CC", value=1.25, cutoff="V", cutoff_value=2.5)
        assert ch.BATT_current == (1.25, 1.25, 1.25)
        assert ch.BATT_cutoff_value == (2.5, 2.5, 2.5)

        ch.BATT_mode(mode="CC", value=(1.3, 0.97), cutoff="V", cutoff_value=(4.1, 3.7))
        assert ch.BATT_current == (1.3, 0.97, 0.97)
        assert ch.BATT_cutoff_value == (4.1, 3.7, 3.7)


@pytest.mark.parametrize(
    "mode,trigmode,value,width",
    [
        ("CC", "COUT", (1, 3.8), (50, 100)),
        ("cc", "PULS", (2, 8), (100, 200)),
        ("CC", "Trig", (3, 9.5), (500, 250)),
        ("CC", "COUT", (7.5, 11.7), (2000, 500)),
        ("cV", "COUT", (2.1, 3.9), (50, 100)),
        ("Cv", "PULS", (2.2, 8.1), (100, 200)),
        ("CV", "TriG", (3.4, 9.4), (500, 250)),
        ("CV", "COuT", (7.3, 11.2), (2000, 500)),
    ],
)
def testTRANSIENTmode(mode, trigmode, value, width):
    "test TRANSIENT mode setup"

    for ch in el.Channels:
        ch.TRANSIENT_mode(mode=mode, trigmode=trigmode, value=value, width=width)
        assert ch.TRANSIENT_submode == mode.upper()
        assert ch.TRANSIENT_trigmode == trigmode.upper()
        if mode.upper() == "CC":
            assert ch.TRANSIENT_current == value
        else:
            assert ch.TRANSIENT_voltage == value
        assert ch.TRANSIENT_width == width


@pytest.mark.parametrize(
        "params", 
        [
            [
                {
                    "num": 1,
                    "mode": "CV",
                    "value": 11.0,
                    "delay": 20,
                    "comp": "RESISTANCE",
                    "maxval": 13.0,
                    "minval": 9.2,
                    },
                {
                    "num": 2,
                    "mode": "CC",
                    "value": 3.3,
                    "delay": 690,
                    "comp": "VOLTAGE",
                    "maxval": 3.5,
                    "minval": 3.0,
                    },
                ],
            ]
        )
def testLISTmode_dict(params):
    "test LIST mode setup"

    for ch in el.Channels:
        ch.LIST_mode("AUTO", ())
        ch.LIST_mode("trigger", ())
        
        ch.LIST_mode("AUTO", params)
        assert ch.LIST_rows[:2] == params
        
        ch.LIST_mode("TRIGGER", params)
        assert ch.LIST_rows[:2] == params

def testLISTmode_list():
    for ch in el.Channels:
        # num, mode, value, delay, comp, max, min
        ch.LIST_mode("AUTO",
            [
                (1, "CC", 4.5, 30, "VOLTAGE", 15.0, 8.5),
                (2, "CV", 13.5, 60, "CURRENT", 1, 0.1),
                (3, "CV", 18.5, 45, "voltage", 2, 0.2),
                (4, "SHORT", 18.5, 45, "voltage", 1, 0.0),
            ]
        )
        
        ch.LIST_mode("AUTO", ())
        ch.LIST_mode("trigger", ())

def testLISTmode_loop():
    for ch in el.Channels:
        ch.mode = "LIST"
        ch.LIST_loop = "ON"
        assert ch.LIST_loop == "ON"
        ch.LIST_loop = "Off"
        assert ch.LIST_loop == "OFF"

def testLISTmode_stepmode():
    for ch in el.Channels:
        ch.mode = "LIST"
        ch.LIST_stepmode = "auto"
        assert ch.LIST_stepmode == "AUTO"
        ch.LIST_stepmode = "TRIGGER"
        assert ch.LIST_stepmode == "TRIGGER"
        
def testLISTmode_steps():
    for ch in el.Channels:
        ch.mode = "LIST"
        ch.LIST_steps = 7
        assert ch.LIST_steps == 7
        ch.LIST_steps = 9
        assert ch.LIST_steps == 9

def testLISTmode_result():
    "test the retrieving results does not crash"
    for ch in el.Channels:
        ch.mode = "LIST"
        ch.LIST_result

@pytest.mark.parametrize(
        "mode,threshold,threshold_value,compare,limits,start_end,step,time",
        [
            ("CC", "VTH", 1.5, "INCURR", (0.5, 1.2), (0, 5), 0.5, 5),
            ("CP", "VMIN", 2.5, "INVOLT", (2, 5), (1.5, 3.5), 1, 5),
        ]
        )
def testSCANmode(mode,threshold,threshold_value,compare,limits,start_end,step,time):
    "Basic test if setup is refected in parameters"
    for ch in el.Channels:
        ch.SCAN_mode(mode, threshold, threshold_value, compare, limits, start_end, step, time)
        assert ch.SCAN_submode == mode
        assert ch.SCAN_threshold == threshold
        assert ch.SCAN_threshold_value == threshold_value
        assert ch.SCAN_compare == compare
        assert ch.SCAN_limits == limits
        assert ch.SCAN_start_end == start_end
        assert ch.SCAN_step == step
        assert ch.SCAN_steptime == time

@pytest.mark.parametrize(
        "Vrange, Crange, Prange, result",
        [
            ((4.0,12), (1,1.5), (4.1, 13), "NONE"),
            ((4.5,5.3), (0.8,1.1), (4.2, 6), "NONE"),
            #((0,32), (0,5), (0, 200), "PASS"),
        ]
        )
def testQUALImode(Vrange, Crange, Prange, result):
    for ch in el.Channels:
        ch.Vrange = "high"
        ch.Crange = "high"
        ch.mode = "CC"
        ch.QUALI_mode(Vrange, Crange, Prange)
        assert ch.QUALI_state == "ON"
        assert ch.QUALI_Vrange == Vrange
        assert ch.QUALI_Crange == Crange
        assert ch.QUALI_Prange == Prange
        ch.QUALI_state = "OFF"
        assert ch.QUALI_state == "OFF"
        assert ch.QUALI_result == result

def test_measure():
    """measuring voltage, current, power and resistance
    This requires that the input terminals are *shorted*!
    If they are left floating, or voltage is applies the test will fail!
    """

    for ch in el.Channels:
        el.ch1.CC_mode(1.0)
        el.ch1.on()
        assert ch.read_voltage() <= 0.01
        assert ch.read_current() <= 0.01
        assert ch.read_power() <= 0.01
        assert ch.read_resistance() <= 0.01
        (V, I, P, R) = ch.read_all()
        assert V <= 0.01
        assert I <= 0.01
        assert P <= 0.01
        assert R <= 0.01

        el.ch1.off()
