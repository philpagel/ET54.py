"Electronic load input channel"

from ._support_functions import _toint, _tofloat, _tofloats, _value_extend 

class channel:
    "input channel"

    def __init__(self, name, write, query):
        self.name = name
        self.write = write
        self.query = query

    def __str__(self):
        mode = self.mode

        ret = f"""Channel {self.name}
Input state:    {self.input}
Voltage range:  {self.Vrange}
Current range:  {self.Crange}
OCP:            {self.OCP} A
OVP:            {self.OVP} V
OPP:            {self.OPP} W
Trigger:        {self.trigger_mode}

Qualification:  {self.QUALI_state}
Quali  Vrange:  {self.QUALI_Vrange} V
Quali  Crange:  {self.QUALI_Crange} A
Quali  Prange:  {self.QUALI_Prange} W

Mode:           {mode}
"""

        match self.mode:
            case "CC":
                ret += f"Current:        {self.CC_current} A"
            case "CV":
                ret += f"Voltage:        {self.CV_voltage} V"
            case "CP":
                ret += f"Power:          {self.CP_power} W"
            case "CR":
                ret += f"Resistance:     {self.CP_resistance} Ω"
            case "CCCV":
                ret += f"Current:        {self.CCCV_current} A"
                ret += f"Voltage:        {self.CCCV_voltage} V"
            case "CRCV":
                ret += f"Resistance:     {self.CRCV_resistance} Ω"
                ret += f"Voltage:        {self.CRCV_voltage} V"
            case "LED":
                ret += f"Current:        {self.LED_current} A"
                ret += f"Voltage:        {self.LED_voltage} V"
                ret += f"Coefficient:    {self.LED_coefficient}"
            case "SHOR":
                pass
            case "BATT":
                submode = self.BATT_submode()
                cutoff = self.BATT_cutoff()
                ret += f"submode:        {self.BATT_submode}\n"
                ret += f"cutoff:         {self.BATT_cutoff}\n"
                if submode == "CC":
                    ret += f"current:        {self.BATT_current} A\n"
                elif submode == "CR":
                    ret += f"resistance      {self.BATT_resistance} Ω\n"
                if cutoff == "Voltage":
                    ret += f"cutoff_value:   {self.BATT_cutoff_value} V\n"
                elif cutoff == "Time":
                    ret += f"cutoff_value:   {self.BATT_cutoff_value} s\n"
                elif cutoff == "Energy":
                    ret += f"cutoff_value:   {self.BATT_cutoff_value} Wh\n"
                elif cutoff == "Capacity":
                    ret += f"cutoff_value:   {self.BATT_cutoff_value} Ah\n"
            case "TRAN":
                submode = self.TRANSIENT_submode
                ret += f"submode:        {seld.TRANSIENT_submode}\n"
                ret += f"trigmode:       {self.TRANSIENT_trigmode}\n"
                if submode == "CC":
                    ret += f"current:        {self.TRANSIENT_current} V\n"
                elif submode == "CV":
                    ret += f"voltage:        {self.TRANSIENT_voltage} A\n"
                ret += f"pulse width:    {self.TRANSIENT_width} s\n"
            case "LIST":
                ret += f"Loop:           {self.LIST_loop}\n"
                ret += f"Step mode:      {self.LIST_stepmode}\n"
                ret += f"Steps:          {self.LIST_steps}\n"
                ret += "List params:    "
                ret += "num mode   value delay comp        maxval minval\n"
                for row in self.LIST_rows():
                    ret += f"                {row['num']:3} "
                    ret += f"{row['mode']:<5} "
                    ret += f"{row['value']:>6} "
                    ret += f"{row['delay']:5} "
                    ret += f"{row['comp']:<10}  "
                    ret += f"{row['maxval']:6} "
                    ret += f"{row['minval']:6}\n"
                ret += "List results:   "
                ret += "num mode   value result maxval minval\n"
                for row in self.LIST_result():
                    ret += f"                {row['num']:3} "
                    ret += f"{row['mode']:<5} "
                    ret += f"{row['value']:>6} "
                    ret += f"{row['result']:5}  "
                    ret += f"{row['maxval']:6} "
                    ret += f"{row['minval']:6}\n"
            case "SCAN":
                ret += f"submode:        {self.SCAN_submode}\n"
                ret += f"threshold type: {self.SCAN_threshold}\n"
                ret += f"threshold value:{self.SCAN_threshold_value}\n"
                ret += f"Comparison:     {self.SCAN_compare}\n"
                ret += f"Limits          {self.SCAN_limits}\n"
                ret += f"Start, end:     {self.SCAN_start_end}\n"
                ret += f"Step:           {self.SCAN_step}\n"
                ret += f"Step time:      {self.SCAN_step_time}\n"

        return ret

    ############################################################
    # input state

    @property
    def input(self):
        "input state (ON|OFF)"
        return self.query(f"Ch{self.name}:SW?")
   
    @input.setter
    def input(self, value):
        if value.upper() in ("ON", "OFF"):
            self.write(f"Ch{self.name}:SW {value}")
        else:
            raise RuntimeError(f"invalid input state '{value}'")

    def on(self):
        self.input = "ON"
    
    def off(self):
        self.input = "OFF"


    ############################################################
    # mode and ranges

    @property
    def mode(self):
        "channel mode (CC|CV|CP|CR|CCCV|CRCV|TRAN|LIST|SCAN|SHOR|BATT|LED)"
        return self.query(f"Ch{self.name}:MODE?")
    
    @mode.setter
    def mode(self, mode):
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
            "SCAN",
            "SHOR",
            "BATT",
            "LED",
        ):
            self.write(f"Ch{self.name}:MODE {mode}")
        else:
            raise ValueError(
                f"Mode must be in ['CC', 'CV', 'CP', 'CR', 'CCCV', 'CRCV', 'TRAN', 'LIST', 'SCAN', 'SHOR', 'BATT', 'LED']"
            )
    
    @property
    def Vrange(self):
        "voltage range (high|low)"
        return self.query(f"LOAD{self.name}:VRANGE?")

    @Vrange.setter
    def Vrange(self, Vrange):
        if Vrange.lower() in ("high", "low"):
            self.write(f"LOAD{self.name}:VRANge {Vrange}")
        else:
            raise ValueError(f"Voltage range must be 'high' or 'low'")

    @property
    def Crange(self):
        "current range (high|low)"
        return self.query(f"LOAD{self.name}:CRANGE?")

    @Crange.setter
    def Crange(self, Crange):
        if Crange.lower() in ("high", "low"):
            self.write(f"LOAD{self.name}:CRANge {Crange}")
        else:
            raise ValueError(f"current range must be 'high' or 'low'")
    
    ############################################################
    # protection

    @property
    def OVP(self):
        "OVP voltage [V]"
        return _tofloat(self.query(f"VOLT{self.name}:VMAX?"))

    @OVP.setter
    def OVP(self, value):
        self.write(f"VOLT{self.name}:VMAX {value}")

    @property
    def OCP(self):
        "OCP current [A]"
        return _tofloat(self.query(f"CURR{self.name}:IMAX?"))

    @OCP.setter
    def OCP(self, value):
        self.write(f"CURR{self.name}:IMAX {value}")

    @property
    def OPP(self):
        "OPP power [W]"
        return _tofloat(self.query(f"POWE{self.name}:PMAX?"))

    @OPP.setter
    def OPP(self, value):
        self.write(f"POWE{self.name}:PMAX {value}")

    @property
    def protection(self):
        """protection state

        NONE    No protection has been triggered
        OV      OCP triggered
        OC      OCP triggered
        OP      OPP triggered
        OT      Overtemp protection triggered
        LRV     reverse voltage protection triggered
        FAN     Fan failure
        """
        return self.query(f"LOAD{self.name}:ABNO?")

    ############################################################
    # CC mode

    def CC_mode(self, current):
        """Put instrument into constant current (CC) mode
        and set CC current"""
        self.CC_current = current
        self.mode = "CC"
    
    @property
    def CC_current(self):
        "current value for CC mode [A]"
        return _tofloat(self.query(f"CURR{self.name}:CC?"))
    
    @CC_current.setter
    def CC_current(self, current):
        self.write(f"CURR{self.name}:CC {current}")

    ############################################################
    # CV mode

    def CV_mode(self, voltage):
        """Put instrument into constant voltage (CV) mode
        and set CV voltage
        """
        self.CV_voltage = voltage
        self.mode = "CV"

    @property
    def CV_voltage(self):
        "voltage value for CV mode [V]"
        return _tofloat(self.query(f"VOLT{self.name}:CV?"))

    @CV_voltage.setter
    def CV_voltage(self, voltage):
        self.write(f"VOLT{self.name}:CV {voltage}")

    ############################################################
    # CP mode

    def CP_mode(self, power):
        """Put instrument into constant power (CP) mode
        and set power"""

        if power is not None:
            self.CP_power = power
        self.mode = "CP"

    @property
    def CP_power(self):
        "power value for CP mode [W]"
        return _tofloat(self.query(f"POWE{self.name}:CP?"))

    @CP_power.setter
    def CP_power(self, power):
        self.write(f"POWE{self.name}:CP {power}")

    ############################################################
    # CR mode

    def CR_mode(self, resistance):
        "Put instrument into constant resistance (CR) mode"
        self.CR_resistance =resistance
        self.mode = "CR"

    @property
    def CR_resistance(self):
        "resistance value for CR mode [Ω]"
        return _tofloat(self.query(f"RESI{self.name}:CR?"))

    @CR_resistance.setter
    def CR_resistance(self, resistance):
        self.write(f"RESI{self.name}:CR {resistance}")

    ############################################################
    # CC+CV mode

    def CCCV_mode(self, current, voltage):
        """Put instrument into constant current and constant voltage (CC+CV) mode
        and set current, voltage"""

        self.CCCV_current = current
        self.CCCV_voltage = voltage 
        self.mode = "CCCV"

    @property
    def CCCV_current(self):
        "current value for CC+CV mode"
        return _tofloat(self.query(f"CURR{self.name}:CCCV?"))

    @CCCV_current.setter
    def CCCV_current(self, current):
        self.write(f"CURR{self.name}:CCCV {current}")

    @property
    def CCCV_voltage(self):
        "voltage value for CC+CV mode [V]"
        return _tofloat(self.query(f"VOLT{self.name}:CCCV?"))

    @CCCV_voltage.setter
    def CCCV_voltage(self, voltage):
        self.write(f"VOLT{self.name}:CCCV {voltage}")

    ############################################################
    # CR+CV mode

    def CRCV_mode(self, resistance, voltage):
        """Put instrument into constant resistance and constant voltage (CR+CV) mode
        and set voltage, resistance"""

        self.CRCV_voltage = voltage
        self.CRCV_resistance = resistance
        self.mode = "CRCV"

    @property
    def CRCV_resistance(self):
        "resistance value for CR+CV mode [Ohm]"
        return _tofloat(self.query(f"RESI{self.name}:CRCV?"))

    @CRCV_resistance.setter
    def CRCV_resistance(self, resistance):
        self.write(f"RESI{self.name}:CRCV {resistance}")

    @property
    def CRCV_voltage(self):
        "voltage value for CR+CV mode [V]"
        return _tofloat(self.query(f"VOLT{self.name}:CRCV?"))

    @CRCV_voltage.setter
    def CRCV_voltage(self, voltage):
        self.write(f"VOLT{self.name}:CRCV {voltage}")

    ############################################################
    # short mode
    def SHORT_mode(self):
        "Put instrument into SHORT circuit mode"
        self.mode = "SHORT"

    ############################################################
    # LED mode

    def LED_mode(self, V, I, coef):
        "Configure LED mode"

        self.LED.voltage = V
        self.LED.current = I
        self.LED_coefficient = coef
        self.mode = "LED"

    @property
    def LED_voltage(self):
        "V0 voltage value for LED mode"
        return _tofloat(self.query(f"VOLT{self.name}:LED?"))

    @LED_voltage.setter
    def LED_voltage(self, value):
        self.write(f"VOLT{self.name}:LED {value}")

    @property
    def LED_current(self):
        "I_0 current value for LED mode"
        return _tofloat(self.query(f"CURR{self.name}:LED?"))

    @LED_current.setter
    def LED_current(self, value):
        self.write(f"CURR{self.name}:LED {value}")

    @property
    def LED_coefficient(self):
        """coefficient for LED mode

        Used in determining the behaviour of the led simulation:
        Rd = (Vo / Io) * Coeff
        Vf = Vo * (1 - Coeff)
        """
        return _tofloat(self.query(f"LED{self.name}:COEF?"))

    @LED_coefficient.setter
    def LED_coefficient(self):
        self.write(f"LED{self.name}:COEF {value}")

    ############################################################
    # battery mode

    def BATT_mode(self, mode, value, cutoff, cutoff_value):
        """Put instrument into battery test mode

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

                        Level  Current     Voltage     Description
                        ---------------------------------------------------
                        3      2.0         15.0,       2.0A if V > 15.0V
                        2      1.5         12.0,       1.5A if V > 12.0V
                        1      1.0         10.0,       1.0A if V > 10.0V then off
        """

        self.BATT_submode = mode
        self.BATT_cutoff = cutoff
        match mode.upper():
            case "CC":
                self.BATT_current = value
            case "CR":
                self.BATT_resistance = value
            case _:
                raise ValueError(f"Invalid BATT submode '{mode}'.")
        self.BATT_cutoff_value = cutoff_value
        self.mode = "BATT"

    @property
    def BATT_submode(self):
        "BATTERY submode (CC|CR)"
        return self.query(f"BATT{self.name}:MODE?")

    @BATT_submode.setter
    def BATT_submode(self, mode):
        mode = mode.upper()
        if mode in ("CC", "CR"):
            self.write(f"BATT{self.name}:MODE {mode}")
        else:
            raise RuntimeError("Invalid battery discharge mode '{mode}'.")

    @property
    def BATT_current(self):
        "BATTERY mode CC current"
        if self.BATT_cutoff == "Voltage":
            return (
                _tofloat(self.query(f"CURR{self.name}:BCC1?")),
                _tofloat(self.query(f"CURR{self.name}:BCC2?")),
                _tofloat(self.query(f"CURR{self.name}:BCC3?")),
            )
        else:
            return _tofloat(self.query(f"CURR{self.name}:BCC?"))

    @BATT_current.setter
    def BATT_current(self, current):
        if self.BATT_cutoff== "Voltage":
            current = _value_extend(current, 3)
            self.write(f"CURR{self.name}:BCC1 {current[0]}")
            self.write(f"CURR{self.name}:BCC2 {current[1]}")
            self.write(f"CURR{self.name}:BCC3 {current[2]}")
        else:
            self.write(f"CURR{self.name}:BCC {current}")

    @property
    def BATT_resistance(self):
        "BATTERY mode CR resistance"
        return _tofloat(self.query(f"RESI{self.name}:BCR?"))

    @BATT_resistance.setter
    def BATT_resistance(self, resistance):
        self.write(f"RESI{self.name}:BCR {resistance}")

    @property
    def BATT_cutoff(self):
        """BATTERY mode cutoff type

        Uses single letters for setting but will return
        words:

        set get
        ---------------
        V   Voltage [V]
        T   Time [s]
        E   Energy [Wh]
        C   Capacity [Ah]
        """
        return self.query(f"BATT{self.name}:BCUT?")

    @BATT_cutoff.setter
    def BATT_cutoff(self, cutoff):
        self.write(f"BATT{self.name}:BCUT {cutoff}")

    @property
    def BATT_cutoff_value(self):
        "BATTERY mode cutoff value"
        match self.BATT_cutoff:
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

    @BATT_cutoff_value.setter
    def BATT_cutoff_value(self, value):
        match self.BATT_cutoff:
            case "Voltage":
                value = _value_extend(value, 3)
                self.write(f"VOLT{self.name}:BCC1 {value[0]}")
                self.write(f"VOLT{self.name}:BCC2 {value[1]}")
                self.write(f"VOLT{self.name}:BCC3 {value[2]}")
            case "Time":
                self.write(f"TIME{self.name}:BTT {value}")
            case "Capacity":
                self.write(f"BATT{self.name}:BTC {value}")
            case "Energy":
                self.write(f"BATT{self.name}:BTE {value}")

    @property
    def BATT_capacity(self):
        "battery discharge capacity value [Ah]"
        return _tofloat(self.query(f"BATT{self.name}:CAPA?"))

    @property
    def BATT_energy(self):
        "battery discharge energy value [Wh]"
        return _tofloat(self.query(f"BATT{self.name}:ENER?"))

    @property
    def BATT_cutoff_level(self):
        """Battery cutoff level (1|2|3)

        only works in CC mode with voltage cutoff.
        Will force the 1st/2nd/3rd cutoff level without requiring
        the voltage to drop to the respective cutoff value.
        Level 3 is the default state!
        """
        return _toint(self.query(f"BATT{self.name}:BAEN?"))

    @BATT_cutoff_level.setter
    def BATT_cutoff_level(self, level):
        self.write(f"BATT{self.name}:BAEN {level}")

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

        self.TRANSIENT_submode = mode.upper()
        self.TRANSIENT_trigmode = trigmode
        match mode.upper():
            case "CC":
                self.TRANSIENT_current = value
            case "CV":
                self.TRANSIENT_voltage = value
            case _:
                raise ValueError(f"Invalid TRANSIENT submode {mode}")
        self.TRANSIENT_width = width
        self.mode = "TRAN"

    @property
    def TRANSIENT_submode(self):
        "TRANSIENT sub-mode (CC|CV)"
        return self.query(f"TRAN{self.name}:STATE?")

    @TRANSIENT_submode.setter
    def TRANSIENT_submode(self, mode):
        mode = mode.upper()
        if mode in ["CC", "CV"]:
            self.write(f"TRAN{self.name}:STATE {mode}")
        else:
            raise ValueError(f"Invalid TRANSIENT sub-mode '{mode}'.")

    @property
    def TRANSIENT_trigmode(self):
        "TRANSIENT sub-mode (COUT||CONT|PULS|TRIG)"
        return self.query(f"TRAN{self.name}:MODE?")

    @TRANSIENT_trigmode.setter
    def TRANSIENT_trigmode(self, trigmode):
        trigmode = trigmode.upper()
        if trigmode == "CONT":
            trigmode = "COUT"
        if trigmode in ["COUT", "PULS", "TRIG"]:
            self.write(f"TRAN{self.name}:MODE {trigmode}")
        else:
            raise ValueError(f"Invalid TRANSIENT trigger mode '{trigmode}'")

    @property
    def TRANSIENT_current(self):
        """TRANSIENT currents (CC mode)
        list of two current values: [I_A, I_B]
        """
        return (
            _tofloat(self.query(f"CURR{self.name}:TA?")),
            _tofloat(self.query(f"CURR{self.name}:TB?")),
        )

    @TRANSIENT_current.setter
    def TRANSIENT_current(self, current):
        if isinstance(current, (list, tuple)) and (len(current) == 2):
            self.write(f"CURR{self.name}:TA {current[0]}")
            self.write(f"CURR{self.name}:TB {current[1]}")
        else:
            raise ValueError(f"Transient current must be a tuple/list of length 2")

    @property
    def TRANSIENT_voltage(self):
        """TRANSIENT voltages (CV mode)
        list of two voltage values: [V_A, V_B]
        """
        return (
            _tofloat(self.query(f"VOLT{self.name}:TA?")),
            _tofloat(self.query(f"VOLT{self.name}:TB?")),
        )

    @TRANSIENT_voltage.setter
    def TRANSIENT_voltage(self, voltage):
        if isinstance(voltage, (list, tuple)) and len(voltage) == 2:
            self.write(f"VOLT{self.name}:TA {voltage[0]}")
            self.write(f"VOLT{self.name}:TB {voltage[1]}")
        else:
            raise ValueError(f"Transient voltage must be a tuple/list of length 2")

    @property
    def TRANSIENT_width(self):
        """TRANSIENT width [ms]
        list/tuple of two time values: [W_A, W_B]
        """
        return (
            _tofloat(self.query(f"TIME{self.name}:WA?")),
            _tofloat(self.query(f"TIME{self.name}:WB?")),
        )

    @TRANSIENT_width.setter
    def TRANSIENT_width(self, width):
        if isinstance(width, (list, tuple)) and len(width) == 2:
            self.write(f"TIME{self.name}:WA {width[0]}")
            self.write(f"TIME{self.name}:WB {width[1]}")
        else:
            raise ValueError(f"Transient widths must be a tuple/list of length 2")

    ############################################################
    # list mode

    def LIST_mode(self, stepmode, params):
        """Put instrument into LIST mode and configure it

        stepmode: mode for advancing in list {AUTO|TRIGGER}

        params: list/tuple of lists/tuples/dicts representing a row in the list:

            num     row number (1-10)
            mode    {CC|CV|CP|CR|OPEN|SHORT}
            value   value of current|voltage|poewr|resistance for respecive mode
            delay   time to spend in this row [s]
            comp    {OFF|CURRent|VOLTage|POWer|RESistance}
            maxval  upper limit for value
            minval  lower limit for value
        """

        self.LIST_stepmode = stepmode
        self.LIST_rows = params
        self.mode = "LIST"

    @property
    def LIST_stepmode(self):
        "LIST step mode {AUTO|TRIGGER}"
        return self.query(f"LIST{self.name}:MODE?")

    @LIST_stepmode.setter
    def LIST_stepmode(self, stepmode):
        "LIST step mode {AUTO|TRIGGER}"
        self.write(f"LIST{self.name}:MODE {stepmode.upper()}")

    @property
    def LIST_rows(self):
        """LIST mode parameters

        params is a list of parameter sets, each defining one list entry.
        Every entry must contain all of the following values:

            num     row number (1-10)
            mode    {CC|CV|CP|CR|OPEN|SHORT}
            value   value of current|voltage|poewr|resistance for respecive mode
            delay   time to spend in this row [s]
            comp    {OFF|CURRent|VOLTage|POWer|RESistance}
            maxval  upper limit for value
            minval  lower limit for value

        either as a list/tuple in that order or a dict containing
        all of them as keys with the respective values
        """

        response = self.query(f"LIST{self.name}:PARA? 1,10", 10, timeout=2500)
        ret = []
        for line in response:
            line = line.rstrip()
            line = line[1:] if line.startswith("R") else line
            fields = line.split(",")
            dat = dict(
                zip(
                    ("num", "mode", "value", "delay", "comp", "maxval", "minval"),
                    fields,
                )
            )
            dat["mode"] = ["CC", "CV", "CP", "CR", "OPEN", "SHORT"][
                int(dat["mode"])
            ]
            dat["comp"] = ["OFF", "CURRENT", "VOLTAGE", "POWER", "RESISTANCE"][
                int(dat["comp"])
            ]
            for par in ["num", "delay"]:
                dat[par] = int(dat[par])
            for par in ["value", "maxval", "minval"]:
                try:
                    dat[par] = float(dat[par])
                except ValueError:
                    dat[par] = "---"
            ret.append(dat)
        return ret if len(ret) > 1 else ret[0]

    @LIST_rows.setter
    def LIST_rows(self, params):
        if params is not None:
            for row in params:
                if isinstance(row, (list, tuple)):
                    self._LIST_row(*row)
                elif isinstance(row, dict):
                    self._LIST_row(**row)
                else:
                    raise ValueError(
                        f"LIST 'params' must be a list, tuple or dict. Got {type(params)}"
                    )

    def _LIST_row(self, num, mode, value, delay, comp, maxval, minval):
        "set a single paramter row in the LIST"

        mode = {"CC": 0, "CV": 1, "CP": 2, "CR": 3, "OPEN": 4, "SHORT": 5}[mode.upper()]
        comp = {"OFF": 0, "CURRENT": 1, "VOLTAGE": 2, "POWER": 3, "RESISTANCE": 4}[
            comp.upper()
        ]
        params = ",".join(
            [str(x) for x in [num, mode, value, delay, comp, maxval, minval]]
        )
        self.write(f"LIST{self.name}:PARA {params}")

    @property
    def LIST_loop(self):
        "loop state {ON|OFF}"
        return self.query(f"LIST{self.name}:LOOP?")

    @LIST_loop.setter
    def LIST_loop(self, state):
        self.write(f"LIST{self.name}:LOOP {state.upper()}")

    @property
    def LIST_steps(self):
        "number of steps to execute"
        return _toint(self.query(f"LIST{self.name}:NUM?"))

    @LIST_steps.setter
    def LIST_steps(self, steps):
        self.write(f"LIST{self.name}:NUM {steps}")

    def LIST_result(self):
        "return the final result after the list has finisehd {pass|fail}"

        steps = self.LIST_steps()
        response = self.query(
            f"LIST{self.name}:OUT? 1,{steps}", nrows=steps, timeout=2500
        )
        ret = []
        for line in response:
            line = line.rstrip()
            line = line[1:] if line.startswith("R") else line
            fields = line.split(",")
            dat = dict(
                zip(("num", "mode", "value", "result", "maxval", "minval"), fields)
            )
            dat["mode"] = ["CC", "CV", "CP", "CR", "OPEN", "SHORT"][int(dat["mode"])]
            dat["result"] = ["NA", "PASS", "FAIL"][int(dat["result"])]
            for par in ["num"]:
                dat[par] = int(dat[par])
            for par in ["value", "maxval", "minval"]:
                try:
                    dat[par] = float(dat[par])
                except ValueError:
                    dat[par] = "---"
            ret.append(dat)
        return ret if len(ret) > 1 else ret[0]

    ############################################################
    # Scan mode

    def SCAN_mode(
        self,
        mode,
        threshold,
        threshold_value,
        compare,
        limits,
        start_end,
        step,
        step_time,
    ):
        """configure SCAN mode
        
        Load will in `mode` and increment voltage|current|power depending on
        `compare` in the increments defined by `step` starting from
        `start_end[0]` to `start_end[1]`.  `step_delay` defines how long the
        load will stay at each step.
        
        While stepping through these settings, it will check if the value of
        `compare` (V|A|W) are within the `limits` or not. The result of this tst is 
        shown on the display, 
        """

        self.SCAN_submode = mode
        self.SCAN_threshold = threshold
        self.SCAN_threshold_value = threshold_value
        self.SCAN_compare = compare
        self.SCAN_limits = limits
        self.SCAN_start_end = start_end
        self.SCAN_step = step
        self.SCAN_stepdelay = step_time
        self.mode = "SCAN"

    @property
    def SCAN_submode(self):
        "scan mode {CC|CV|CP}"
        return self.query(f"SCAN{self.name}:TYPE?")

    @SCAN_submode.setter
    def SCAN_submode(self, mode):
        self.write(f"SCAN{self.name}:TYPE {mode}")

    @property
    def SCAN_threshold(self):
        "Scan threshold type {VTH|DROP|VMIN}"
        return self.query(f"SCAN{self.name}:THTYPE?")

    @SCAN_threshold.setter
    def SCAN_threshold(self, threshold):
        self.write(f"SCAN{self.name}:THTYPE {threshold.upper()}")

    @property
    def SCAN_threshold_value(self):
        """scan votage threshold value}
        depending on SCAN threshold this is the voltage or voltage drop"""
        match self.SCAN_threshold:
            case "VTH":
                return _tofloat(self.query(f"VOLT{self.name}:VTH?"))
            case "VMIN":
                return _tofloat(self.query(f"VOLT{self.name}:VMIN?"))
            case "DROP":
                pass

    @SCAN_threshold_value.setter
    def SCAN_threshold_value(self, value):
        match self.SCAN_threshold:
            case "VTH":
                self.write(f"VOLT{self.name}:VTH {value}")
            case "VMIN":
                self.write(f"VOLT{self.name}:VMIN {value}")
            case "DROP":
                pass

    @property
    def SCAN_compare(self):
        "comparison type {INCURR|INVOLT|INPOW|OFF}"
        return self.query(f"SCAN{self.name}:COMPARE?")

    @SCAN_compare.setter
    def SCAN_compare(self, compare):
        self.write(f"SCAN{self.name}:COMPARE {compare.upper()}")

    @property
    def SCAN_limits(self):
        """upper and lower limit for SCAN mode
        list/tupple of 2
        depending on SCAN submode, value is in [A|V|W]"""
        match self.SCAN_submode:
            case "CC":
                return (
                    _tofloat(self.query(f"CURR{self.name}:LOW?")),
                    _tofloat(self.query(f"CURR{self.name}:HIGH?")),
                )
            case "CV":
                return (
                    _tofloat(self.query(f"VOLT{self.name}:LOW?")),
                    _tofloat(self.query(f"VOLT{self.name}:HIGH?")),
                )
            case "CP":
                return (
                    _tofloat(self.query(f"POWE{self.name}:LOW?")),
                    _tofloat(self.query(f"POWE{self.name}:HIGH?")),
                )

    @SCAN_limits.setter
    def SCAN_limits(self, value):
        low, high = value
        match self.SCAN_submode:
            case "CC":
                self.write(f"CURR{self.name}:LOW {low}")
                self.write(f"CURR{self.name}:HIGH {high}")
            case "CV":
                self.write(f"VOLT{self.name}:LOW {low}")
                self.write(f"VOLT{self.name}:HIGH {high}")
            case "CP":
                self.write(f"POWE{self.name}:LOW {low}")
                self.write(f"POWE{self.name}:HIGH {high}")

    @property
    def SCAN_start_end(self):
        """start and end value for SCAN mode
        list/tupple of 2
        depending on SCAN submode, value is in [A|V|W]"""

        match self.SCAN_submode:
            case "CC":
                return (
                    _tofloat(self.query(f"CURR{self.name}:START?")),
                    _tofloat(self.query(f"CURR{self.name}:END?")),
                )
            case "CV":
                return (
                    _tofloat(self.query(f"VOLT{self.name}:START?")),
                    _tofloat(self.query(f"VOLT{self.name}:END?")),
                )
            case "CP":
                return (
                    _tofloat(self.query(f"POWE{self.name}:START?")),
                    _tofloat(self.query(f"POWE{self.name}:END?")),
                )

    @SCAN_start_end.setter
    def SCAN_start_end(self, value):
        start, end = value
        
        match self.SCAN_submode:
            case "CC":
                self.write(f"CURR{self.name}:START {start}")
                self.write(f"CURR{self.name}:END {end}")
            case "CV":
                self.write(f"VOLT{self.name}:START {start}")
                self.write(f"VOLT{self.name}:END {end}")
            case "CP":
                self.write(f"POWE{self.name}:START {start}")
                self.write(f"POWE{self.name}:END {end}")

    @property
    def SCAN_step(self):
        """step value for SCAN mode
        depending on SCAN submode, value is in [A|V|W]
        """

        match self.SCAN_submode:
            case "CC":
                return _tofloat(self.query(f"CURR{self.name}:STEP?"))
            case "CV":
                return _tofloat(self.query(f"VOLT{self.name}:STEP?"))
            case "CP":
                return _tofloat(self.query(f"POWE{self.name}:STEP?"))

    @SCAN_step.setter
    def SCAN_step(self, value):
        match self.SCAN_submode:
            case "CC":
                self.write(f"CURR{self.name}:STEP {value}")
            case "CV":
                self.write(f"VOLT{self.name}:STEP {value}")
            case "CP":
                self.write(f"POWE{self.name}:STEP {value}")

    @property
    def SCAN_stepdelay(self):
        "step delay [s] for SCAN mode"
        return _toint(self.query(f"TIME{self.name}:STEP?"))

    @SCAN_stepdelay.setter
    def SCAN_stepdelay(self, time):
        self.write(f"TIME{self.name}:STEP {time}")

    ############################################################
    # Qualifiction test mode

    def QUALI_mode(self, Vrange, Crange, Prange):
        """Qualification test mode
        
        Vrange  (low, high) [V]
        Crange  (low, high) [C]
        Prange  (low, high) [P]

        This mode can be used in conjunction with the basic modes 
        CC, CV, CR and CP.
        """
        self.QUALI_Vrange = Vrange
        self.QUALI_Crange = Crange
        self.QUALI_Prange = Prange
        self.QUALI_state = "ON"

    @property
    def QUALI_state(self):
        "State of qualification test mode {ON|OFF}"
        return self.query(f"QUAL{self.name}:TEST?")

    @QUALI_state.setter
    def QUALI_state(self, state):
        self.query(f"QUAL{self.name}:TEST {state}")
    
    @property
    def QUALI_result(self):
        "Result qualification test {NONE|PASS|FAIL}"
        return self.query(f"QUAL{self.name}:OUT?")

    @property
    def QUALI_Vrange(self):
        "Voltage range for qualification test (Vlow, Vhigh) [V]"
        return (
                _tofloat(self.query(f"QUAL{self.name}:VLOW?")),
                _tofloat(self.query(f"QUAL{self.name}:VHIGH?")),
                )

    @QUALI_Vrange.setter    
    def QUALI_Vrange(self, value):
            self.write(f"QUAL{self.name}:VLOW {value[0]}")
            self.write(f"QUAL{self.name}:VHIGH {value[1]}")

    @property
    def QUALI_Crange(self):
        "Current range for qualification test (Clow, Chigh) [A]"
        return (
                _tofloat(self.query(f"QUAL{self.name}:CLOW?")),
                _tofloat(self.query(f"QUAL{self.name}:CHIGH?")),
                )

    @QUALI_Crange.setter    
    def QUALI_Crange(self, value):
            self.write(f"QUAL{self.name}:CLOW {value[0]}")
            self.write(f"QUAL{self.name}:CHIGH {value[1]}")

    @property
    def QUALI_Prange(self):
        "Power range for qualification test (Plow, Phigh) [W]"
        return (
                _tofloat(self.query(f"QUAL{self.name}:PLOW?")),
                _tofloat(self.query(f"QUAL{self.name}:PHIGH?")),
                )

    @QUALI_Prange.setter    
    def QUALI_Prange(self, value):
            self.write(f"QUAL{self.name}:PLOW {value[0]}")
            self.write(f"QUAL{self.name}:PHIGH {value[1]}")



    ############################################################
    # Load effect test

    # XXX: to be implemented


    ############################################################
    # Trigger support

    @property
    def trigger_mode(self):
        """trigger mode (MAN|EXT|TRG)

        MAN:    manual trigger (TRIG button)
        EXT:    external trigger (connector on back)
        TRG:    remote trigger (trigger() method)
        """
        return self.query(f"LOAD{self.name}:TRIG?")

    @trigger_mode.setter
    def trigger_mode(self, trigmode):
        if trigmode.upper() in ("MAN", "EXT", "TRG"):
            self.write(f"LOAD{self.name}:TRIG {trigmode}")
        else:
            raise ValueError(f"invalid trigger mode '{trigmode}'.")

    def trigger(self):
        "send trigger event"
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


