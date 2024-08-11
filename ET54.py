"""
Controlling East Tester ET54 series electronic loads
"""

import time, re, pyvisa

class ET54:
    "ET54 series electronic load"

    def __init__(self, RID, model=False):
        rm = pyvisa.ResourceManager()
        self.connection = rm.open_resource(RID)
        self.connection.read_termination = "\r\n"
        self.connection.write_termination = "\n"
        #self.connection.baud_rate=9600
        self.delay = 0.1   # delay after slow commands

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
            print(f"Command failed ({ret})", file=sys.stderr)
            return 1
        else:
            print(f"Command returned unknown response ({ret})", file=sys.stderr)
            return 2
    
    def query(self, command):
        "Write command to connection and return answer value"

        value = self.connection.query(command)
        if value == "Rcmd err":
            print(f"Command failed ({value})", file=sys.stderr)
            return None
        else:
            return value


class channel:
    "Electronic load channel"

    def __init__(self, name, write, query):
        self.name = name
        self.write = write
        self.query = query

    def __str__(self):
        mode = self.mode()

        ret = f"""Channel:            {self.name}
state:              {self.get_}
mode:               {mode}
Input state:        {self.get_state()}
Voltage range:      {self.get_Vrange()}
Current range:      {self.get_Crange()}
OCP:                {self.get_OCP()}
OPP:                {self.get_OPP()}

"""

        match self.mode():
            case "CC":
                ret += f"{self.get_currentCC}"
            case "CV":
                ret += f"{self.get_currentCC}"
            case "CP":
                pass
            case "CR":
                pass
            case "CCCV":
                pass
            case "CRCV":
                pass
            case "TRAN":
                pass
            case "LIST":
                pass
            case "SHOR":
                pass
            case "BATT":
                pass
            case "LED":
                pass
        return ret
    

    def get_state(self):
        "Return input stat (on|off)"
        return self.query(f"Ch{self.name}:SW?")

    def on(self):
        "turn input on"
        self.write(f"Ch{self.name}:SW ON")

    def off(self):
        "turn input off"
        self.write(f"Ch{self.name}:SW OFF")

    ############################################################ 
    # mode and range

    def set_mode(self, mode):
        "set channel to mode {CC|CV|CP|CR|CCCV|CRCV|TRAN|LIST|SHOR|BATT|LED}"
        
        mode = mode.upper()
        if mode in ("CC", "CV", "CP", "CR", "CCCV", "CRCV", "TRAN", "LIST", "SHOR", "BATT", "LED"):
            self.write(f"Ch{self.name}:MODE {mode}")
        else:
            raise ValueError(f"Mode must be in ['CC', 'CV', 'CP', 'CR', 'CCCV', 'CRCV', 'TRAN', 'LIST', 'SHOR', 'BATT', 'LED']")

    def get_mode(self):
        "Return mode"
        return self.query(f"Ch{self.name}:MODE?")

    def set_Vrange(self, Vrange):
        "set voltage range to {high|low}"

        if Vrange.lower() in ("high", "low"):
            self.write(f"LOAD{self.name}:VRANge {Vrange}")
        else:
            raise ValueError(f"Voltage range must be 'high' or 'low'")
    
    def get_Vrange(self):
        "get voltage range (high|low)"
        return self.query(f"LOAD{self.name}:VRANGE?")

    def set_Crange(self, Crange):
        "set current range to (high|low)"

        if Crange.lower() in ("high", "low"):
            self.write(f"LOAD{self.name}:CRANge {Crange}")
        else:
            raise ValueError(f"current range must be 'high' or 'low'")
    
    def get_Crange(self):
        "get current range (high|low)"
        return self.query(f"LOAD{self.name}:CRANGE?")


    ############################################################ 
    # current settings

    def get_OCP(self):
        "get  OCP current"
        return  _tofloat(self.query(f"CURR{self.name}:IMAX?"))

    def set_OCP(self, value):
        "set OCP current"
        self.write(f"CURR{self.name}:IMAX {value}")

    def get_current_CC(self):
        "return the current value for CC mode"
        return _tofloat(self.query(f"CURR{self.name}:CC?"))

    def set_current_CC(self, value):
        "set the current value for CC mode"
        self.write(f"CURR{self.name}:CC {value}")

    def get_current_CCCV(self):
        "return the current value for CC+CV mode"
        return _tofloat(self.query(f"CURR{self.name}:CCCV?"))

    def set_current_CCCV(self, value):
        "set the current value for CC+CV mode"
        self.write(f"CURR{self.name}:CCCV {value}")
    
    def get_current_LED(self):
        "return the current value for LED mode"
        return _tofloat(self.query(f"CURR{self.name}:LED?"))

    def set_current_LED(self, value):
        "set the current value for LED mode"
        self.write(f"CURR{self.name}:LED {value}")
    

    ############################################################ 
    # power settings
    
    def get_OPP(self):
        "get OPP power"
        return  _tofloat(self.query(f"POWE{self.name}:PMAX?"))

    def set_OPP(self, value):
        "set OPP power"
        self.write(f"POWE{self.name}:PMAX {value}")
    

    ############################################################ 
    # measuring

    def get_mode(self):
        "Return channel mode"
        return self.query(f"Ch{self.name}:MODE?")

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


    ############################################################ 
    # setup CC mode

    def CC_mode():
        "Put instrument into CC mode"
        self.write(f"Ch{self.name}:MODE CC")

    def CC_current(self):
        "return the current value for CC mode"
        return _tofloat(self.query(f"CURR{self.name}:CC?"))

    def CC_current(self, value):
        "set the current value for CC mode"
        self.write(f"CURR{self.name}:CC {value}")

    def CC_setup(current, Vrange="high", Crange="high"):
        "Configure CC mode parameters"
        self.CC_mode()
        self.CC_current(current)
        self.set_Vrange(Vrange)
        self.set_Crange(Crange)

    ############################################################
    # setup CV

    def CV_mode():
        "Put instrument into CV mode"
        self.write(f"Ch{self.name}:MODE CV")



# support functions

def _tofloat(value):
    "strip leading 'R' and convert to float"
    return float(re.sub("^R", "", value))

def _tofloats(values):
    "strip leading 'R' split on whitespace and convert all items to float"
    return [float(x) for x in re.sub("^R", "", values).split()]


