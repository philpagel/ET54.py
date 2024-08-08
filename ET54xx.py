"""
Controlling EastTester ET54 series electronic loads
"""

import pyvisa

class ET54:
    "ET54 series electronic load"

    def __init__(self, RID, model=False):
        rm = pyvisa.ResourceManager()
        self.connection = rm.open_resource(RID)
        self.connection.read_termination = "\r\n"
        self.connection.write_termination = "\n"
        self.delay = 0.5   # read delay after write

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

        match self.idn["model"]:
            case "ET5410":
                self.ch1 = channel("1", self.connection)
            case "ET5410A+":
                self.ch1 = channel("1", self.connection)
            case "ET5411":
                self.ch1 = channel("1", self.connection)
            case "ET5411A+":
                self.ch1 = channel("1", self.connection)
            case "ET5420A+":
                self.ch1 = channel("1", self.connection)
                self.ch2 = channel("2", self.connection)
            case _:
                raise RuntimeError(f"Instrument ID '{self.idn['model']}' not supported." )

    def __del__(self):
        self.connection.close()

    def __str__(self):
        return f"{self.idn['model']} electronic load\nSN:{self.idn['SN']}\nFirmware: {self.idn['firmware']}"


class channel:
    "Electronic load channel"

    def __init__(self, name, connection):
        self.connection = connection
        self.name = name

    def set_Vrange(self, Vrange):
        "set voltage range to {high|low}"

        if Vrange.lower() in ("high", "low"):
            ret = self.connection.query(f"LOAD{self.name}:VRANge {Vrange}")
            if ret != "Rexecu success":
                print(ret)
        else:
            raise ValueError(f"Voltage range must be 'high' or 'low'")
    
    def get_Vrange(self):
        "get voltage range (high|low)"

        return self.connection.query(f"LOAD{self.name}:VRANGE?")

    def set_Crange(self, Crange):
        "set current range to (high|low)"

        if Crange.lower() in ("high", "low"):
            ret = self.connection.query(f"LOAD{self.name}:CRANge {Crange}")
            if ret != "Rexecu success":
                print(ret)
        else:
            raise ValueError(f"current range must be 'high' or 'low'")
    
    def get_Crange(self):
        "get current range (high|low)"

        return self.connection.query(f"LOAD{self.name}:CRANGE?")

    def set_mode(self, mode):
        "set channel to mode {CC|CV|CP|CR|CCCV|CRCV|TRAN|LIST|SHOR|BATT|LED}"
        
        if mode.lower() in ("CC", "CV", "CP", "CR", "CCCV", "CRCV", "TRAN", "LIST", "SHOR", "BATT", "LED"):
            self.connection.query(f"Ch{self.name}:MODE {mode}")
        else:
            raise ValueError(f"Mode must be in ['CC', 'CV', 'CP', 'CR', 'CCCV', 'CRCV', 'TRAN', 'LIST', 'SHOR', 'BATT', 'LED']")

    def get_mode(self):
        "Return channel mode"

        return self.connection.query(f"Ch{self.name}:MODE?")

    def read_voltage(self):
        "read (measure) input voltage [V]"

        return float(self.connection.query(f"MEAS{self.name}:VOLT?"))

    def read_current(self):
        "read (measure) input current [A]"

        return float(self.connection.query(f"MEAS{self.name}:CURR?"))

    def read_power(self):
        "read (measure) input power [W]"

        return float(self.connection.query(f"MEAS{self.name}:POW?"))

    def read_resistance(self):
        "read (measure) resistance [W]"

        return float(self.connection.query(f"MEAS{self.name}:RESI?"))

    def read_all(self):
        "read (measure) output values: Volts [V], current [A], Power[W]"

        return [float(x) for x in self.connection.query(f"MEAS{self.name}:ALL?").split(",")]

    def on(self):
        "turn input on"
        self.connection.query(f"Ch{self.name}:SW ON")

    def off(self):
        "turn input off"
        self.connection.query(f"Ch{self.name}:SW OFF")


