"""
Controlling East Tester ET54 series electronic loads
"""

import time, pyvisa

class ET54:
    "ET54 series electronic load"

    def __init__(self, RID, model=False):
        rm = pyvisa.ResourceManager()
        self.connection = rm.open_resource(RID)
        self.connection.read_termination = "\r\n"
        self.connection.write_termination = "\n"
        #self.connection.baud_rate=9600

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
        return f"{self.idn['model']} electronic load\nSN:{self.idn['SN']}\nFirmware: {self.idn['firmware']}\n Hardware: {self.idn['hardware']}"


class channel:
    "Electronic load channel"

    def __init__(self, name, connection):
        self.connection = connection
        self.name = name
        self.delay = 0.1   # delay after slow commands

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

    def write(self, command):
        "Write command to connection and check status"

        ret = self.connection.query(command)
        if ret != "Rexecu success":
            print(ret)
        return ret
    

    def get_state(self):
        "Return input stat (on|off)"
        return self.connection.query(f"Ch{self.name}:SW?")

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
        return self.connection.query(f"Ch{self.name}:MODE?")

    def set_Vrange(self, Vrange):
        "set voltage range to {high|low}"

        if Vrange.lower() in ("high", "low"):
            self.write(f"LOAD{self.name}:VRANge {Vrange}")
            time.sleep(self.delay)
        else:
            raise ValueError(f"Voltage range must be 'high' or 'low'")
    
    def get_Vrange(self):
        "get voltage range (high|low)"
        return self.connection.query(f"LOAD{self.name}:VRANGE?")

    def set_Crange(self, Crange):
        "set current range to (high|low)"

        if Crange.lower() in ("high", "low"):
            self.write(f"LOAD{self.name}:CRANge {Crange}")
            time.sleep(self.delay)
        else:
            raise ValueError(f"current range must be 'high' or 'low'")
    
    def get_Crange(self):
        "get current range (high|low)"
        return self.connection.query(f"LOAD{self.name}:CRANGE?")


    ##########################################################################
    # current settings

    def get_OCP(self):
        "set current OCP value"
        return self.connection.query(f"CURR{self.name}:IMAX?")

    def set_OCP(self, value):
        "set current OCP value"
        self.write(f"CURR{self.name}:IMAX {value}")
    
    def set_current_CC(self, value):
        "set the current value for CC mode"
        self.write(f"CURR{self.name}:CC {value}")

    def set_current_CCCV(self, value):
        "set the current value for CCCV mode"
        self.write(f"CURR{self.name}:CCCV {value}")
    
    def set_current_LED(self, value):
        "set the current value for LED mode"
        self.write(f"CURR{self.name}:CCCV {value}")
    

    ##########################################################################
    # measuring

    def get_mode(self):
        "Return channel mode"
        return self.connection.query(f"Ch{self.name}:MODE?")

    def read_voltage(self):
        "read (measure) input voltage [V]"
        return float(self.connection.query(f"MEAS{self.name}:VOLT?"))

    def read_current(self):
        "read (measure) input current [A]"
        return float(self.query(f"MEAS{self.name}:CURR?"))

    def read_power(self):
        "read (measure) input power [W]"
        return float(self.query(f"MEAS{self.name}:POW?"))

    def read_resistance(self):
        "read (measure) resistance [W]"
        return float(self.query(f"MEAS{self.name}:RESI?"))

    def read_all(self):
        "read (measure) output values: Volts [V], current [A], Power[W] Resistance[Ω]"
        return [float(x) for x in self.query(f"MEAS{self.name}:ALL?").split(",")]


