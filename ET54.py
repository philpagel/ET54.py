"""
Controlling East Tester ET54 series electronic loads
"""

import sys, time, pyvisa

class ET54:
    "ET54 series electronic load"

    def __init__(self, RID, model=False):
        rm = pyvisa.ResourceManager()
        self.connection = rm.open_resource(RID)
        self.connection.read_termination = "\r\n"
        self.connection.write_termination = "\n"
        #self.connection.baud_rate=9600
        self.delay = 0.1   # delay after write

        tmp = self.connection.query("*IDN?").split()
        self.idn = dict()
        if len(tmp) == 4:
            (self.idn['model'],
            self.idn['SN'],
            self.idn['firmware'],
            self.idn['hardware'])  = tmp
        elif len(tmp) == 3 and tmp[0] == "XXXXXX":
            # handle Mustool branded device
            self.idn['model'] = tmp[0]
            self.idn['SN'] = None
            self.idn['firmware'] = tmp[1]
            self.idn['hardware'] = tmp[2]
        else:
            raise RuntimeError(f"Unable to parse device identification: '{tmp}'")
        if model:
            # Override model ID. Required for Mustool devices to work
            self.idn["model"] = model

        if self.idn["model"] in ("ET5410", "ET5410A+", "ET5411", "ET5411A+"):
            self.ch1 = channel("1", self.write, self.query)
        elif self.idn["model"] == "ET5420A+":
            self.ch1 = channel("1", self.write, self.query)
            self.ch2 = channel("2", self.write, self.query)
        else:
            raise RuntimeError(f"Instrument ID '{self.idn['model']}' not supported.")

    def __del__(self):
        self.connection.close()

    def __str__(self):
        ret =  f"""{Model:      self.idn['model']} electronic load
Serial:         {self.idn['SN']}
Firmware:       {self.idn['firmware']}
Hardware:       {self.idn['hardware']}
"""
        ret += self.ch1.__str__()
        
        return ret

    def write(self, command):
        "Write command to connection and check status"

        ret = self.connection.query(command)
        time.sleep(self.delay)
        if ret == "Rexecu success":
            return 0
        elif ret == "Rcmd err":
            raise RuntimeError(f"Unknown SCPI command '{command}' ('{ret}')")
        elif ret == "Rexecu err":
            raise RuntimeError(f"SCPI command '{command}' failed ('{ret}')")
        else:
            raise RuntimeError(f"SCPI command '{command}' returned unknown response ('{ret}')")
    
    def query(self, command):
        "Write command to connection and return answer value"

        value = self.connection.query(command)
        if value == "Rcmd err":
            print(f"Command failed ({value})", file=sys.stderr)
            return None
        else:
            return value

    def close(self):
        "close connection to instument"
        self.connection.close()


class channel:
    "Electronic load channel"

    def __init__(self, name, write, query):
        self.name = name
        self.write = write
        self.query = query

    def __str__(self):
        mode = self.mode()

        ret = f"""Channel:            {self.name}
Input state:        {self.input()}
Voltage range:      {self.Vrange()}
Current range:      {self.Crange()}
OCP:                {self.OCP()}
OVP:                {self.OVP()}
OPP:                {self.OPP()}

mode:               {mode}

"""

        # XXX:
        match self.mode():
            case "CC":
                ret += f"Current:           {self.CC_current()}"
            case "CV":
                ret += f"Voltage:           {self.CV_voltage()}"
            case "CP":
                ret += f"Power:             {self.CP_power()}"
            case "CR":
                ret += f"Resistance:        {self.CP_resistance()}"
            case "CCCV":
                ret += f"Current:           {self.CCVC_current()}"
                ret += f"Voltage:           {self.CCCV_voltage()}"
            case "CRCV":
                ret += f"Resistance:        {self.CRCV_resistance()}"
                ret += f"Voltage:           {self.CRCV_voltage()}"
            case "LED":
                ret += f"Current:           {self.LED_current()}"
                ret += f"Voltage:           {self.LED_voltage()}"
                ret += f"Coefficient:       {self.LED_coefficient()}"
            case "SHOR":
                pass
            case "BATT":
                pass
            case "TRAN":
                pass
            case "LIST":
                pass
        return ret
    
    ############################################################ 
    # input state

    def input(self, value=None):
        "get/set input state (ON|OFF)"

        if value is not None:
            if value.upper() in ("ON", "OFF"):
                self.write(f"Ch{self.name}:SW {value}")
            else:
                raise RuntimeError(f"invaliid input state '{value}'")
        return self.query(f"Ch{self.name}:SW?")

    def on(self):
        "turn input on"
        self.write(f"Ch{self.name}:SW ON")

    def off(self):
        "turn input off"
        self.write(f"Ch{self.name}:SW OFF")

    ############################################################ 
    # mode and ranges

    def mode(self, mode=None):
        "get/set channel mode (CC|CV|CP|CR|CCCV|CRCV|TRAN|LIST|SHOR|BATT|LED)"
        
        if mode is not None:
            mode = mode.upper()
            if mode in ("CC", "CV", "CP", "CR", "CCCV", "CRCV", "TRAN", "LIST", "SHOR", "BATT", "LED"):
                self.write(f"Ch{self.name}:MODE {mode}")
            else:
                raise ValueError(f"Mode must be in ['CC', 'CV', 'CP', 'CR', 'CCCV', 'CRCV', 'TRAN', 'LIST', 'SHOR', 'BATT', 'LED']")
        return self.query(f"Ch{self.name}:MODE?")

    def Vrange(self, Vrange=None):
        "get/set voltage range (high|low)"

        if Vrange is not None:
            if Vrange.lower() in ("high", "low"):
                self.write(f"LOAD{self.name}:VRANge {Vrange}")
            else:
                raise ValueError(f"Voltage range must be 'high' or 'low'")
        return self.query(f"LOAD{self.name}:VRANGE?")
    
    def Crange(self, Crange=None):
        "get/set current range to (high|low)"

        if Crange is not None:
            if Crange.lower() in ("high", "low"):
                self.write(f"LOAD{self.name}:CRANge {Crange}")
            else:
                raise ValueError(f"current range must be 'high' or 'low'")
        return self.query(f"LOAD{self.name}:CRANGE?")
    

    ############################################################ 
    # protection
    
    def OVP(self, value=None):
        "get/set OVP voltage [V]"

        if value is not None:
            self.write(f"VOLT{self.name}:VMAX {value}")
        return  _tofloat(self.query(f"VOLT{self.name}:VMAX?"))

    def OCP(self, value=None):
        "get/set OCP current [A]"

        if value is not None:
            self.write(f"CURR{self.name}:IMAX {value}")
        return  _tofloat(self.query(f"CURR{self.name}:IMAX?"))

    def OPP(self, value=None):
        "get/set OPP power [W]"
        
        if value is not None:
            self.write(f"POWE{self.name}:PMAX {value}")
        return  _tofloat(self.query(f"POWE{self.name}:PMAX?"))
    
    ############################################################ 
    # CC mode

    def CC_mode(self, current=None):
        """Put instrument into constant current (CC) mode
        and set CC current if given"""
        self.write(f"Ch{self.name}:MODE CC")
        if current is not None:
            self.CC_current(current)

    def CC_current(self, current=None):
        "get/set the current value for CC mode [A]"

        if current is not None:
            self.write(f"CURR{self.name}:CC {current}")
        return _tofloat(self.query(f"CURR{self.name}:CC?"))

    ############################################################
    # CV mode

    def CV_mode(self, voltage=None):
        """Put instrument into constant voltage (CV) mode
        and set CV voltage if given
        """

        self.write(f"Ch{self.name}:MODE CV")
        if voltage is not None:
            self.CV_voltage(voltage)

    def CV_voltage(self, voltage=None):
        "get/set the voltage value for CV mode [V]"

        if voltage is not None:
            self.write(f"VOLT{self.name}:CV {voltage}")
        return _tofloat(self.query(f"VOLT{self.name}:CV?"))
    
    ############################################################
    # CP mode
    
    def CP_mode(self, power=None):
        """Put instrument into constant power (CP) mode
        Optionally set power"""

        self.write(f"Ch{self.name}:MODE CP")
        if power is not None:
            self.CP_power(power)

    def CP_power(self, power=None):
        "get/set the power value for CP mode [W]"

        if power is not None:
            self.write(f"POWE{self.name}:CP {power}")
        return _tofloat(self.query(f"POWE{self.name}:CP?"))

    ############################################################
    # CR mode
    
    def CR_mode(self, resistance=None):
        "Put instrument into constant resistance (CR) mode"

        self.write(f"Ch{self.name}:MODE CR")
        if resistance is not None:
            self.CR_resistance(resistance)

    def CR_resistance(self, resistance=None):
        "get/set the resistance value for CR mode [Ω]"

        if resistance is not None:
            self.write(f"RESI{self.name}:CR {resistance}")
        return _tofloat(self.query(f"RESI{self.name}:CR?"))


    ############################################################
    # CC+CV mode

    def CCCV_mode(self, current=None, voltage=None):
        """Put instrument into constant current and constant voltage (CC+CV) mode
        and set current, voltage if given"""

        self.write(f"Ch{self.name}:MODE CCCV")
        if current is not None:
            self.CCCV_current(current)
        if voltage is not None:
            self.CCCV_voltage(voltage)
    
    def CCCV_current(self, current=None):
        "get/set the current value for CC+CV mode"

        if current is not None:
            self.write(f"CURR{self.name}:CCCV {current}")
        return _tofloat(self.query(f"CURR{self.name}:CCCV?"))
    
    def CCCV_voltage(self, voltage=None):
        "get/set the voltage value for CC+CV mode [V]"

        if voltage is not None:
            self.write(f"VOLT{self.name}:CCCV {voltage}")
        return _tofloat(self.query(f"VOLT{self.name}:CCCV?"))
    
    ############################################################
    # CR+CV mode

    def CRCV_mode(self, resistance=None, voltage=None):
        """Put instrument into constant resistance and constant voltage (CR+CV) mode
        and set voltage, resistance if given"""

        self.write(f"Ch{self.name}:MODE CRCV")
        if voltage is not None:
            self.CRCV_voltage(voltage)
        if resistance is not None:
            self.CRCV_resistance(resistance)
    
    def CRCV_resistance(self, resistance=None):
        "get/set the current value for CR+CV mode [A]"

        if resistance is not None:
            self.write(f"RESI{self.name}:CRCV {resistance}")
        return _tofloat(self.query(f"RESI{self.name}:CRCV?"))

    def CRCV_voltage(self, voltage=None):
        "get/set the voltage value for CR+CV mode [V]"

        if voltage is not None:
            self.write(f"VOLT{self.name}:CRCV {voltage}")
        return _tofloat(self.query(f"VOLT{self.name}:CRCV?"))

    ############################################################
    # short mode
    def SHORT_mode(self):
        "Put instrument into SHORT circuit mode"
        self.write(f"Ch{self.name}:MODE SHORT")

    ############################################################
    # LED mode

    def LED_mode(self, V0=None, I0=None, coef=None):
        "Put instrument into LED mode"

        self.write(f"Ch{self.name}:MODE LED")
        if V0 is not None:
            self.LED.voltage(V0)
        if I0 is not None:
            self.LED.current(I0)
        if coef is not None:
            self.LED_coefficient(coef)

    def LED_voltage(self, value=None):
        "get/set the V0 voltage value for LED mode"

        if value is not None:
            self.write(f"VOLT{self.name}:LED {value}")
        return _tofloat(self.query(f"VOLT{self.name}:LED?"))

    def LED_current(self, value=None):
        "get/set the I_0 current value for LED mode"

        if value is not None:
            self.write(f"CURR{self.name}:LED {value}")
        return _tofloat(self.query(f"CURR{self.name}:LED?"))

    def LED_coefficient(self, value=None):
        """get/set the coefficient for LED mode

        Used in determining the behaviour of the led simulation:
        Rd = (Vo / Io) * Coeff
        Vf = Vo * (1 - Coeff)
        """

        if value is not None:
            self.write(f"LED{self.name}:COEF {value}")
        return _tofloat(self.query(f"LED{self.name}:COEF?"))

    ############################################################
    # battery mode

    def BATTERY_mode(self, mode=None, resistance=None, current=None,
                     cutoff=None, cutoff_value=None):
        """Put instrument into BATTERY mode
       
        Battery mode supports two different operation modes (CC and CR) and
        four cutoff conditions that govern when the load will turn off:

        mode:       {CC|CR}

        cutoff:     V: voltage
                    T: time
                    E: energy
                    C: capacity

        current:    CC current value for CC mode

        resistance: resistance value for CR mode
        
        cutoff_value:
                    Value(s) at which the load is turned off or switches to a
                    different current.

                    Depending on the cutoff mode, this is one of the follwoing.
                    
                    For `cutoff={T|E|C}`: a single float defining the cutoff-value:

                        time [s]
                        energy [Wh]
                        Capacity [Ah]

                    For `cutoff=V`: a list of three tupples, each of which
                    contains a (current, voltage) pair indicating a current to
                    draw until voltage trops to the voltage cutoff.
                    E.g.:

                    [
                        (2.00, 15.00),  # 2.00A until we reach 15.00V
                        (1.50, 12.00),  # 1.50A until we reach 12.00V
                        (1.00, 10.00),  # 1.0ßA until we reach 10.00V and turn off
                    ]
                    
        """

        self.write(f"Ch{self.name}:MODE BATT")
        if mode is not None:
            if mode.upper() in ("CC", "CV"):
                self.write("BATT:MODE {mode}")
            else:
                raise RuntimeError("Invalid battery discharge mode '{mode}'.")
        if cutoff is not None:
            if cutoff.upper() in ("V", "T", "C", "E"):
                self.write(f"BATT:BCUT ")
   
    def BATTCC_currents(self):
        "return discharge currents"

        return (
            self.query(f"CURR:BCC1?"),
            self.query(f"CURR:BCC1?"),
            self.query(f"CURR:BCC1?"),
            )

    def BATTCC_current(self, I):
        "set the three discharge currents for Battery CC mode"

        if len(I) != 3:
            raise RuntimError("Three discharge currents must be supplied.")
        else:
            self.write(f"CURR:BCC1 {I[0]}")
            self.write(f"CURR:BCC2 {I[1]}")
            self.write(f"CURR:BCC3 {I[2]}")

    def BATTCC_voltages(self):
        "return cutoff currents"

        return (
            self.query(f"VOLT:BCC1?"),
            self.query(f"VOLT:BCC1?"),
            self.query(f"VOLT:BCC1?"),
            )

    def BATTCC_Voltage(self, V):
        "set the three cutoff voltages for Battery CC mode"

        if len(I) != 3:
            raise RuntimError("Three cutoff voltages must be supplied.")
        else:
            self.write(f"VOLT:BCC1 {V[0]}")
            self.write(f"VOLT:BCC2 {V[1]}")
            self.write(f"VOLT:BCC3 {V[2]}")
    

    ############################################################
    # list mode

    def LIST_mode(self):
        "Put instrument into LIST mode"
        self.write(f"Ch{self.name}:MODE LIST")

    # XXX: to be implemented

    ############################################################
    # transient mode
    
    def TRANSIENT_mode(self):
        "Put instrument into TRANSIENT mode"
        self.write(f"Ch{self.name}:MODE TRAN")

    # XXX: to be implemented

    
    ############################################################
    # Qualifiction test mode
    
    # XXX: to be implemented


    ############################################################
    # Trigger support
    
    # XXX: to be implemented


    ############################################################ 
    # measuring

    def read_voltage(self):
        "read (measure) input voltage [V]"
        return _tofloat(self.query(f"MEAS{self.name}:VOLTAGE?"))

    def read_current(self):
        "read (measure) input current [A]"
        return _tofloat(self.query(f"MEAS{self.name}:CURRENT?"))

    def read_power(self):
        "read (measure) input power [W]"
        return _tofloat(self.query(f"MEAS{self.name}:POWER?"))

    def read_resistance(self):
        "read (measure) resistance [W]"
        return _tofloat(self.query(f"MEAS{self.name}:RESISTANCE?"))

    def read_all(self):
        "read (measure) output values: Volts [V], current [A], Power[W] Resistance[Ω]"
        return _tofloats(self.query(f"MEAS{self.name}:ALL?"))


# support functions
def _tofloat(value):
    "strip leading 'R' and convert to float"

    if value.startswith("R"):
        value = value[1:]
    return float(value)

def _tofloats(value):
    "strip leading 'R' split and convert all to float"
    
    if value.startswith("R"):
        value = value[1:].split()

    return [float(x) for x in value]


