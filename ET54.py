"""
Controlling East Tester ET54 series electronic loads

should work with models ET5410, ET5420, ET5411, ET5410A+, ET5420A+, ET5411A+
and maybe even ET5406A+, Et5407A+

tested on ET5410A+
"""

import sys, time, pyvisa

class ET54:
    "ET54 series electronic load"

    def __init__(self, RID, baudrate=9600, eol_r="\r\n", eol_w="\n", delay=0.2, model=None):
        """
        RID         pyvisa ressource ID
        baudrate    must match baudrate set in device (default: 9600)
        eol_r       line terminator for reading from device
        eol_W       line terminator for writing to device
        delay       delay after read/write operation [s]
        model       model ID [ET5410|ET5420|ET5410A+|...] 
                    only required if `*IDN?` does not return a valid ID
                    e.g. for Mustool branded ET5410A+
        """
        rm = pyvisa.ResourceManager()
        self.connection = rm.open_resource(RID)
        self.connection.baud_rate=baudrate
        self.connection.query_delay = delay
        self.connection.read_termination = eol_r
        self.connection.write_termination = eol_w

        tmp = self.connection.query("*IDN?").split()
        self.idn = dict()
        if len(tmp) == 4:
            (
                self.idn["model"],
                self.idn["SN"],
                self.idn["firmware"],
                self.idn["hardware"],
            ) = tmp
        elif len(tmp) == 3 and tmp[0] == "XXXXXX":
            # handle Mustool branded device
            self.idn["model"] = tmp[0]
            self.idn["SN"] = None
            self.idn["firmware"] = tmp[1]
            self.idn["hardware"] = tmp[2]
        else:
            raise RuntimeError(f"Unable to parse device identification: '{tmp}'")
        if model is not None:
            self.idn["model"] = model

        if self.idn["model"].upper() in ("ET5410", "ET5410A+", "ET5411", "ET5411A+"):
            self.ch1 = channel("1", self.write, self.query)
        elif self.idn["model"] == "ET5420A+":
            self.ch1 = channel("1", self.write, self.query)
            self.ch2 = channel("2", self.write, self.query)
        else:
            raise RuntimeError(f"Instrument ID '{self.idn['model']}' not supported.")

    def __del__(self):
        self.connection.close()

    def __str__(self):
        ret = f"""Model:          {self.idn['model']}
Serial:         {self.idn['SN']}
Firmware:       {self.idn['firmware']}
Hardware:       {self.idn['hardware']}
"""
        ret += self.ch1.__str__()

        return ret

    def write(self, command):
        "Write command to connection and check status"

        ret = self.connection.query(command)
        time.sleep(self.connection.query_delay )
        if ret == "Rexecu success":
            return 0
        elif ret == "Rcmd err":
            raise RuntimeError(f"Unknown SCPI command '{command}' ('{ret}')")
        elif ret == "Rexecu err":
            raise RuntimeError(f"SCPI command '{command}' failed ('{ret}')")
        else:
            raise RuntimeError(
                f"SCPI command '{command}' returned unknown response ('{ret}')"
            )

    def query(self, command):
        "Write command to connection and return answer value"

        value = self.connection.query(command)
        time.sleep(self.connection.query_delay)
        if value == "Rcmd err":
            print(f"Command failed ({value})", file=sys.stderr)
            return None
        else:
            return value

    def close(self):
        "close connection to instument"
        self.connection.close()
    
    def beep(self):
        "Beep"
        self.write("SYST:BEEP")

    def unlock(self):
        """unlock the local interface

        After unlocking, buttons on the device work again.
        Sending a SCPI command will lock the device again.
        """
        self.write("SYST:LOCA")

    def fan(self):
        "return fan state"
        return self.query("SELF:FAN?")

class channel:
    "Electronic load channel"

    def __init__(self, name, write, query):
        self.name = name
        self.write = write
        self.query = query

    def __str__(self):
        mode = self.mode()

        ret = f"""
Channel {self.name}
Input state:    {self.input()}
Voltage range:  {self.Vrange()}
Current range:  {self.Crange()}
OCP:            {self.OCP()} A
OVP:            {self.OVP()} V
OPP:            {self.OPP()} W
mode:           {mode}
trigger:        {self.trigger_mode()}
"""

        # XXX:
        match self.mode():
            case "CC":
                ret += f"Current:        {self.CC_current()} A"
            case "CV":
                ret += f"Voltage:        {self.CV_voltage()} V"
            case "CP":
                ret += f"Power:          {self.CP_power()} W"
            case "CR":
                ret += f"Resistance:     {self.CP_resistance()} Ω"
            case "CCCV":
                ret += f"Current:        {self.CCVC_current()} A"
                ret += f"Voltage:        {self.CCCV_voltage()} V"
            case "CRCV":
                ret += f"Resistance:     {self.CRCV_resistance()} Ω"
                ret += f"Voltage:        {self.CRCV_voltage()} V"
            case "LED":
                ret += f"Current:        {self.LED_current()} A"
                ret += f"Voltage:        {self.LED_voltage()} V"
                ret += f"Coefficient:    {self.LED_coefficient()}"
            case "SHOR":
                pass
            case "BATT":
                submode = self.BATT_submode()
                cutoff = self.BATT_cutoff()
                ret += f"submode:        {submode}\n"
                ret += f"cutoff:         {cutoff}\n"
                if submode == "CC":
                        ret += f"current:        {self.BATT_current()} A\n"
                elif submode == "CR":
                        ret += f"resistance      {self.BATT_resistance()} Ω\n"
                if cutoff == "Voltage":
                    ret += f"cutoff_value:   {self.BATT_cutoff_value()} V\n"
                elif cutoff == "Time":
                    ret += f"cutoff_value:   {self.BATT_cutoff_value()} s\n"
                elif cutoff == "Energy":
                    ret += f"cutoff_value:   {self.BATT_cutoff_value()} Wh\n"
                elif cutoff == "Capacity":
                    ret += f"cutoff_value:   {self.BATT_cutoff_value()} Ah\n"
            case "TRAN":
                submode = self.TRANSIENT_submode()
                ret += f"submode:        {submode}\n"
                ret += f"trigmode:       {self.TRANSIENT_trigmode()}\n"
                if submode == "CC":
                    ret += f"current:        {self.TRANSIENT_current()} V\n"
                elif submode == "CV":
                    ret += f"voltage:        {self.TRANSIENT_voltage()} A\n"
                ret += f"pulse width:    {self.TRANSIENT_width()} s\n"
                
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
                raise RuntimeError(f"invalid input state '{value}'")
        else:
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
        """get/set channel mode (CC|CV|CP|CR|CCCV|CRCV|TRAN|LIST|SHOR|BATT|LED)
        
        For setting up different modes better use the `*_mode()` methods that
        allow configuring each mode at the same time."""

        if mode is not None:
            mode = mode.upper()
            if mode in (
                "CC",
                "CV",
                "CP",
                "CR",
                "CCCV",
                "CRCV",
                "TRAN",
                "LIST",
                "SHOR",
                "BATT",
                "LED",
            ):
                self.write(f"Ch{self.name}:MODE {mode}")
            else:
                raise ValueError(
                    f"Mode must be in ['CC', 'CV', 'CP', 'CR', 'CCCV', 'CRCV', 'TRAN', 'LIST', 'SHOR', 'BATT', 'LED']"
                )
        else:
            return self.query(f"Ch{self.name}:MODE?")

    def Vrange(self, Vrange=None):
        "get/set voltage range (high|low)"

        if Vrange is not None:
            if Vrange.lower() in ("high", "low"):
                self.write(f"LOAD{self.name}:VRANge {Vrange}")
            else:
                raise ValueError(f"Voltage range must be 'high' or 'low'")
        else:
            return self.query(f"LOAD{self.name}:VRANGE?")

    def Crange(self, Crange=None):
        "get/set current range to (high|low)"

        if Crange is not None:
            if Crange.lower() in ("high", "low"):
                self.write(f"LOAD{self.name}:CRANge {Crange}")
            else:
                raise ValueError(f"current range must be 'high' or 'low'")
        else:
            return self.query(f"LOAD{self.name}:CRANGE?")

    ############################################################
    # protection

    def OVP(self, value=None):
        "get/set OVP voltage [V]"

        if value is not None:
            self.write(f"VOLT{self.name}:VMAX {value}")
        else:
            return _tofloat(self.query(f"VOLT{self.name}:VMAX?"))

    def OCP(self, value=None):
        "get/set OCP current [A]"

        if value is not None:
            self.write(f"CURR{self.name}:IMAX {value}")
        else:
            return _tofloat(self.query(f"CURR{self.name}:IMAX?"))

    def OPP(self, value=None):
        "get/set OPP power [W]"

        if value is not None:
            self.write(f"POWE{self.name}:PMAX {value}")
        else:
            return _tofloat(self.query(f"POWE{self.name}:PMAX?"))

    def protection(self):
        """return protection state
        
        NONE    No protection has been triggered
        OV      OCP triggered
        OC      OCP triggered
        OP      OPP triggered
        LRV     reverse voltage protection triggered
        OT      Overtemp protection triggered
        """
        return self.query(f"LOAD{self.name}:ABNO?")

    ############################################################
    # CC mode

    def CC_mode(self, current):
        """Put instrument into constant current (CC) mode
        and set CC current"""
        self.write(f"Ch{self.name}:MODE CC")
        self.CC_current(current)

    def CC_current(self, current=None):
        "get/set the current value for CC mode [A]"

        if current is not None:
            self.write(f"CURR{self.name}:CC {current}")
        else:
            return _tofloat(self.query(f"CURR{self.name}:CC?"))

    ############################################################
    # CV mode

    def CV_mode(self, voltage):
        """Put instrument into constant voltage (CV) mode
        and set CV voltage
        """

        self.write(f"Ch{self.name}:MODE CV")
        self.CV_voltage(voltage)

    def CV_voltage(self, voltage=None):
        "get/set the voltage value for CV mode [V]"

        if voltage is not None:
            self.write(f"VOLT{self.name}:CV {voltage}")
        else:
            return _tofloat(self.query(f"VOLT{self.name}:CV?"))

    ############################################################
    # CP mode

    def CP_mode(self, power):
        """Put instrument into constant power (CP) mode
        and set power"""

        self.write(f"Ch{self.name}:MODE CP")
        if power is not None:
            self.CP_power(power)

    def CP_power(self, power=None):
        "get/set the power value for CP mode [W]"

        if power is not None:
            self.write(f"POWE{self.name}:CP {power}")
        else:
            return _tofloat(self.query(f"POWE{self.name}:CP?"))

    ############################################################
    # CR mode

    def CR_mode(self, resistance):
        "Put instrument into constant resistance (CR) mode"

        self.write(f"Ch{self.name}:MODE CR")
        self.CR_resistance(resistance)

    def CR_resistance(self, resistance=None):
        "get/set the resistance value for CR mode [Ω]"

        if resistance is not None:
            self.write(f"RESI{self.name}:CR {resistance}")
        else:
            return _tofloat(self.query(f"RESI{self.name}:CR?"))

    ############################################################
    # CC+CV mode

    def CCCV_mode(self, current, voltage):
        """Put instrument into constant current and constant voltage (CC+CV) mode
        and set current, voltage"""

        self.write(f"Ch{self.name}:MODE CCCV")
        self.CCCV_current(current)
        self.CCCV_voltage(voltage)

    def CCCV_current(self, current=None):
        "get/set the current value for CC+CV mode"

        if current is not None:
            self.write(f"CURR{self.name}:CCCV {current}")
        else:
            return _tofloat(self.query(f"CURR{self.name}:CCCV?"))

    def CCCV_voltage(self, voltage=None):
        "get/set the voltage value for CC+CV mode [V]"

        if voltage is not None:
            self.write(f"VOLT{self.name}:CCCV {voltage}")
        else:
            return _tofloat(self.query(f"VOLT{self.name}:CCCV?"))

    ############################################################
    # CR+CV mode

    def CRCV_mode(self, resistance, voltage):
        """Put instrument into constant resistance and constant voltage (CR+CV) mode
        and set voltage, resistance"""

        self.write(f"Ch{self.name}:MODE CRCV")
        self.CRCV_voltage(voltage)
        self.CRCV_resistance(resistance)

    def CRCV_resistance(self, resistance=None):
        "get/set the current value for CR+CV mode [A]"

        if resistance is not None:
            self.write(f"RESI{self.name}:CRCV {resistance}")
        else:
            return _tofloat(self.query(f"RESI{self.name}:CRCV?"))

    def CRCV_voltage(self, voltage=None):
        "get/set the voltage value for CR+CV mode [V]"

        if voltage is not None:
            self.write(f"VOLT{self.name}:CRCV {voltage}")
        else:
            return _tofloat(self.query(f"VOLT{self.name}:CRCV?"))

    ############################################################
    # short mode
    def SHORT_mode(self):
        "Put instrument into SHORT circuit mode"
        self.write(f"Ch{self.name}:MODE SHORT")

    ############################################################
    # LED mode

    def LED_mode(self, V0, I0, coef):
        "Put instrument into LED mode"

        self.write(f"Ch{self.name}:MODE LED")
        self.LED.voltage(V0)
        self.LED.current(I0)
        self.LED_coefficient(coef)

    def LED_voltage(self, value=None):
        "get/set the V0 voltage value for LED mode"

        if value is not None:
            self.write(f"VOLT{self.name}:LED {value}")
        else:
            return _tofloat(self.query(f"VOLT{self.name}:LED?"))

    def LED_current(self, value=None):
        "get/set the I_0 current value for LED mode"

        if value is not None:
            self.write(f"CURR{self.name}:LED {value}")
        else:
            return _tofloat(self.query(f"CURR{self.name}:LED?"))

    def LED_coefficient(self, value=None):
        """get/set the coefficient for LED mode

        Used in determining the behaviour of the led simulation:
        Rd = (Vo / Io) * Coeff
        Vf = Vo * (1 - Coeff)
        """

        if value is not None:
            self.write(f"LED{self.name}:COEF {value}")
        else:
            return _tofloat(self.query(f"LED{self.name}:COEF?"))

    ############################################################
    # battery mode

    def BATT_mode(self, mode, value, cutoff, cutoff_value):
        """Put instrument into BATT mode

        Battery mode supports two different operation (sub)modes (CC and CR)
        and four cutoff conditions that govern when the load will turn off:

        mode:       {CC|CR}

        value:      current value [A] (CC mode)
                      or
                    resistance value [Ω] (CR mode)
                    
                    If `cutoff == 'V'` AND `mode == 'CC'`: 
                        list of up to 3 current values that
                        are set once the respective cutoff_value
                        has been reached.

        cutoff:     type of cutoff condition. One of

                    V: voltage
                    T: time
                    E: energy
                    C: capacity

        cutoff_value:
                    Value(s) at which the load is turned off or switches to a
                    different current.

                    Most of the time, a single float defining the cutoff-value:
                        
                        Voltage [V]
                        Time [s]
                        Energy [Wh]
                        Capacity [Ah]

                    If  `cutoff == 'V'` AND `mode == 'CC'`: 
                        A list of up to three voltage cutoffs that
                        trigger switching to the next current value once reached
                        
                        E.g.:
                        value=[2.0, 1.5, 1.0]
                        cutoff_value=[15, 12, 10]

                        State  Current     Voltage     Description
                        ---------------------------------------------------
                        3      2.0         15.0,       2.0A if V > 15.0V
                        2      1.5         12.0,       1.5A if V > 12.0V
                        1      1.0         10.0,       1.0A if V > 10.0V then off
        """

        self.write(f"Ch{self.name}:MODE BATT")
        self.BATT_submode(mode)
        self.BATT_cutoff(cutoff)
        match mode.upper():
            case "CC":
                self.BATT_current(value)
            case "CR":
                self.BATT_resistance(value)
            case _:
                raise ValueError(f"Invalid BATT submode '{mode}'.")
        self.BATT_cutoff_value(cutoff_value)
        
    def BATT_submode(self, mode=None):
        "get/set BATTERY submode (CC|CR)"

        if mode is not None:
            mode = mode.upper()
            if mode in ("CC", "CR"):
                self.write(f"BATT{self.name}:MODE {mode}")
            else:
                raise RuntimeError("Invalid battery discharge mode '{mode}'.")
        else:
            return self.query(f"BATT{self.name}:MODE?")

    def BATT_current(self, current=None):
        "get/set BATTERY mode CC current"
        
        cutoff = self.BATT_cutoff()
        if current is not None:
            if cutoff == "Voltage":
                current = value_extend(current, 3)
                self.write(f"CURR{self.name}:BCC1 {current[0]}")
                self.write(f"CURR{self.name}:BCC2 {current[1]}")
                self.write(f"CURR{self.name}:BCC3 {current[2]}")
            else:
                self.write(f"CURR{self.name}:BCC {current}")
        if cutoff == "Voltage":

            return (
                        _tofloat(self.query(f"CURR{self.name}:BCC1?")),
                        _tofloat(self.query(f"CURR{self.name}:BCC2?")),
                        _tofloat(self.query(f"CURR{self.name}:BCC3?")),
                        )
        else:
            return _tofloat(self.query(f"CURR{self.name}:BCC?"))

    def BATT_resistance(self, resistance=None):
        "get/set BATTERY mode CR resistance"

        if resistance is not None:
            self.write(f"RESI{self.name}:BCR {resistance}")
        else:
            return _tofloat(self.query(f"RESI{self.name}:BCR?"))

    def BATT_cutoff(self, cutoff=None):
        """get/set BATTERY mode cutoff type
        
        Uses single letters for setting but will return
        words:
        
        set get
        ---------------
        V   Voltage [V]
        T   Time [s]
        E   Energy [Wh]
        C   Capacity [Ah]
        """

        if cutoff is not None:
            self.write(f"BATT{self.name}:BCUT {cutoff}")
        else:
            return self.query(f"BATT{self.name}:BCUT?")

    def BATT_cutoff_value(self, value=None):
        "get/set BATTERY mode cutoff value"

        cutoff = self.BATT_cutoff()
        if value is not None:
            match cutoff:
                case "Voltage":
                    value = value_extend(value, 3)
                    self.write(f"VOLT{self.name}:BCC1 {value[0]}")
                    self.write(f"VOLT{self.name}:BCC2 {value[1]}")
                    self.write(f"VOLT{self.name}:BCC3 {value[2]}")
                case "Time":
                    self.write(f"TIME{self.name}:BTT {value}")
                case "Capacity":
                    self.write(f"BATT{self.name}:BTC {value}")
                case "Energy":
                    self.write(f"BATT{self.name}:BTE {value}")

        else:
            match cutoff: 
                case "Voltage":
                    submode = self.query(f"BATT{self.name}:MODE?")
                    if submode == "CC":
                        return (
                                _tofloat(self.query(f"VOLT{self.name}:BCC1?")),
                                _tofloat(self.query(f"VOLT{self.name}:BCC2?")),
                                _tofloat(self.query(f"VOLT{self.name}:BCC3?")),
                                )
                    elif submode == "CR":
                        return self.query(f"CURR{self.name}:BCC?") 
                    else:
                        raise ValueError(f"Invalid BATT mode cutoff")
                case "Time":
                    return _tofloat(self.query(f"TIME{self.name}:BTT?"))
                case "Capacity":
                    return _tofloat(self.query(f"BATT{self.name}:BTC?"))
                case "Energy":
                    return _tofloat(self.query(f"BATT{self.name}:BTE?"))

    def BATT_capacity():
        "get the battery discharge capacity value [Ah]"
        return self.query(f"BATT{self.name}:CAPA?")
    
    def BATT_energy():
        "get the battery discharge energy value [Wh]"
        return self.query(f"BATT{self.name}:CAPA?")

    def BATT_cutoff_level(self, level=None):
        """get/set cutoff level (1|2|3)

        only works in CC mode with voltage cutoff. 
        Will force the 1st/2nd/3rd cutoff level without requiring
        the voltage to drop to the respective cutoff value.
        Level 3 is the default state!
        """

        if level is not None:
            self.write(f"BATT{self.name}:BAEN {level}")
        else:
            return _toint(self.query(f"BATT{self.name}:BAEN?"))

    ############################################################
    # transient mode

    def TRANSIENT_mode(self, mode, trigmode, value, width):
        """Put instrument into TRANSIENT mode (aka Dynamic mode)
       
        The load will switch between two states A and B depending on mode 
        and trigmode

        mode:       sub-mode (CC|CV)
        trigmode:   trigger setting (CONT|TRIG|PULS)
        value:      values for transient states (low and high) in V or A,
                    depending on mode
        width:      Pulse width for the two states [s]
        """
        
        self.write(f"Ch{self.name}:MODE TRAN")
        self.TRANSIENT_submode(mode.upper())
        self.TRANSIENT_trigmode(trigmode)
        match mode.upper():
            case "CC":
                self.TRANSIENT_current(value)
            case "CV":
                self.TRANSIENT_voltage(value)
            case _:
                raise ValueError(f"Invalid TRANSIENT submode {mode}")
        self.TRANSIENT_width(width)
           
    def TRANSIENT_submode(self, mode=None):
        "get/set TRANSIENT sub-mode (CC|CV)"
       
        if mode is not None:
            mode = mode.upper()
            if mode in ["CC", "CV"]:
                self.write(f"TRAN{self.name}:STATE {mode}")
            else:
                raise ValueError(f"Invalid TRANSIENT sub-mode '{mode}'.")
        else:
            return self.query(f"TRAN{self.name}:STATE?")
    
    def TRANSIENT_trigmode(self, trigmode=None):
        "get/set TRANSIENT sub-mode (COUT|PULS|TRIG)"
        
        if trigmode is not None:
            trigmode = trigmode.upper()
            if trigmode == "CONT":
                trigmode = "COUT"
            if trigmode in ["COUT", "PULS", "TRIG"]:
                self.write(f"TRAN{self.name}:MODE {trigmode}")
            else:
                raise ValueError(f"Invalid TRANSIENT trigger mode '{trigmode}'")
        else:
            return self.query(f"TRAN{self.name}:MODE?")

    def TRANSIENT_current(self, current=None):
        """get/set TRANSIENT currents (CC mode)
        
        current:    list of two current values: [I_A, I_B]
        """

        if (current is not None): 
            if isinstance(current, (list, tuple)) and (len(current)==2):
                self.write(f"CURR{self.name}:TA {current[0]}")
                self.write(f"CURR{self.name}:TB {current[1]}")
            else:
                raise ValueError(f"Transient current must be a tuple/list of length 2")

        else:
            return (
                    _tofloat(self.query(f"CURR{self.name}:TA?")), 
                    _tofloat(self.query(f"CURR{self.name}:TB?")), 
                    )
    

    def TRANSIENT_voltage(self, voltage=None):
        """get/set TRANSIENT voltages (CV mode)
        
        current:    list of two voltage values: [V_A, V_B]
        """

        if voltage is not None:
            if isinstance(voltage, (list, tuple)) and len(voltage)==2:
                self.write(f"VOLT{self.name}:TA {voltage[0]}")
                self.write(f"VOLT{self.name}:TB {voltage[1]}")
            else:
                raise ValueError(f"Transient voltage must be a tuple/list of length 2")

        else:
            return (
                    _tofloat(self.query(f"VOLT{self.name}:TA?")), 
                    _tofloat(self.query(f"VOLT{self.name}:TB?")), 
                    )

    def TRANSIENT_width(self, width=None):
        """get/set TRANSIENT widh [ms]

        time:    list/tuple of two time values: [W_A, W_B]
        """

        if width is not None:
            if isinstance(width, (list, tuple)) and len(width)==2:
                self.write(f"TIME{self.name}:WA {width[0]}")
                self.write(f"TIME{self.name}:WB {width[1]}")
            else:
                raise ValueError(f"Transient widths must be a tuple/list of length 2")
        else:
            return (
                    _tofloat(self.query(f"TIME{self.name}:WA?")), 
                    _tofloat(self.query(f"TIME{self.name}:WB?")), 
                    )

    ############################################################
    # list mode

    def LIST_mode(self):
        "Put instrument into LIST mode"
        self.write(f"Ch{self.name}:MODE LIST")

    # XXX: to be implemented

    ############################################################
    # Qualifiction test mode

    # XXX: to be implemented

    ############################################################
    # Trigger support

    def trigger_mode(self, trigmode=None):
        """Set the trigger mode (MAN|EXT|TRG)

        MAN:    manual trigger (TRIG button)
        EXT:    external trigger (connector on back)
        TRG:    remote trigger (trigger() method)
        """
        
        if trigmode is not None:
            if trigmode.upper() in ("MAN", "EXT", "TRG"):
                self.write(f"LOAD{self.name}:TRIG {trigmode}")
            else:
                raise ValueError(f"invalid trigger mode '{trigmode}'.")
        else:
            return self.query(f"LOAD{self.name}:TRIG?")

    def trigger(self):
        "trigger event"
        self.write(f"*TRG")

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

def _toint(value):
    "strip leading 'R' and convert to int"

    if value.startswith("R"):
        value = value[1:]
    return int(value)

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

def value_extend (x, n):
    "turn x into list of length n by replicating the last element"

    if isinstance(x, list):
        pass
    elif isinstance(x, tuple):
        x = list(x)
    elif isinstance(x, (int, float, str)):
        x = [x]
    else:
        raise ValueError(f"x must be in, float, list or tupple not '{type(x)}'")
    
    if 0 < len(x) < n+1 :
        x.extend([x[-1]] * (n-len(x)) )
    else:
        raise ValueError(f"Wrong number of arguments. Expected up to {n}, got {len(x)}.")
    return x

