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

        self.idn = dict()
        if model:
            self.idn["model"] = model
            self.idn["SN"] = None
            self.idn["firmware"] = None
            self.idn["hardware"] = None
        else:
            (self.idn['model'], 
             self.idn['SN'], 
             self.idn['firmware'],
             self.idn['hardware'],
             ) = self.connection.query("*IDN?").split(" ")

        match self.idn["model"].upper():
            case "ET5410":
                self.ch1 = channel("1", self.write, self.query)
            case "ET5410A+":
                self.ch1 = channel("1", self.write, self.query)
            case "ET5411":
                self.ch1 = channel("1", self.write, self.query)
            case "ET5411A+":
                self.ch1 = channel("1", self.write, self.query)
            case "ET5420A+":
                self.ch1 = channel("1", self.write, self.query)
                self.ch2 = channel("2", self.write, self.query)
            case _:
                raise RuntimeError(f"Instrument ID '{self.idn['model']}' not supported." )

    def __del__(self):
        self.connection.close()

    def __str__(self):
        return f"{self.idn['model']} electronic load\nSN:{self.idn['SN']}\nFirmware: {self.idn['firmware']}\n Hardware: {self.idn['hardware']}"

    def write(self, command):
        "Write command to connection and check status"

        ret = self.connection.query(command)
        if ret != "Rexecu success":
            print(ret)
        time.sleep(self.delay)
        return ret
    
    def query(self, command):
        "Write command to connection and return answer value"

        value = self.connection.query(command)
        if value == "Rcmd err":
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

        ret = f"""Channel:    {self.name}
state:              {self.get_}
mode:               {mode}
Voltage range:     {self.get_Vrange()}
Current range:     {self.get_Crange()}

"""

        match self.mode():
            case "CC":
                pass
            case "CV":
                pass
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

    

    def get_state(self):
        "Return input stat (on|off)"
        return self.query(f"Ch{self.name}:SW?")

    def on(self):
        "turn input on"
        self.write(f"Ch{self.name}:SW ON")

    def off(self):
        "turn input off"
        self.write(f"Ch{self.name}:SW OFF")

    ##########################################################################
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


    ##########################################################################
    # current settings

    def get_OCP(self):
        "set current OCP value"
        return  tofloat(self.query(f"CURR{self.name}:IMAX?"))

    def set_OCP(self, value):
        "set current OCP value"
        self.write(f"CURR{self.name}:IMAX {value}")
    
    def get_current_CC(self):
        "return the current value for CC mode"
        return tofloat(self.query(f"CURR{self.name}:CC?"))

    def set_current_CC(self, value):
        "set the current value for CC mode"
        self.write(f"CURR{self.name}:CC {value}")

    def get_current_CCCV(self):
        "return the current value for CC+CV mode"
        return tofloat(self.query(f"CURR{self.name}:CCCV?"))

    def set_current_CCCV(self, value):
        "set the current value for CC+CV mode"
        self.write(f"CURR{self.name}:CCCV {value}")
    
    def get_current_LED(self):
        "return the current value for LED mode"
        return tofloat(self.query(f"CURR{self.name}:LED?"))

    def set_current_LED(self, value):
        "set the current value for LED mode"
        self.write(f"CURR{self.name}:LED {value}")
    

    ##########################################################################
    # measuring

    def get_mode(self):
        "Return channel mode"
        return self.query(f"Ch{self.name}:MODE?")

    def read_voltage(self):
        "read (measure) input voltage [V]"
        return tofloat(self.query(f"MEAS{self.name}:VOLTAGE?"))

    def read_current(self):
        "read (measure) input current [A]"
        return tofloat(self.query(f"MEAS{self.name}:CURRENT?"))

    def read_power(self):
        "read (measure) input power [W]"
        return tofloat(self.query(f"MEAS{self.name}:POWER?"))

    def read_resistance(self):
        "read (measure) resistance [W]"
        return tofloat(self.query(f"MEAS{self.name}:RESISTANCE?"))

    def read_all(self):
        "read (measure) output values: Volts [V], current [A], Power[W] Resistance[Ω]"
        return tofloats(self.query(f"MEAS{self.name}:ALL?"))


def tofloat(value):
    "strip leading 'R' and convert to float"
    return float(re.sub("^R", "", value))

def tofloats(values):
    "strip leading 'R' split on whitespace and convert all items to float"
    return [float(x) for x in re.sub("^R", "", values).split()]


