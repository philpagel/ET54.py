"Electronic load base instrument"

import sys, time, pyvisa
from .channel import channel

class ET54:
    """ET54 series electronic load

    depending on the the specific model, a ET54 instance will
    have one or two channels that are accessible via individual
    instance variabels `ch1` / `ch2` or from the instance variable `channels` 
    which is a list of channel objects"""

    def __init__(
        self,
        RID,
        baudrate=9600,
        eol_r="\r\n",
        eol_w="\n",
        delay=0.2,
        timeout=2000,
        model=None,
    ):
        """
        RID         pyvisa ressource ID
        baudrate    must match baudrate set in device (default: 9600)
        eol_r       line terminator for reading from device
        eol_W       line terminator for writing to device
        delay       delay after read/write operation [s]
        timeout     read timeout [ms]
        model       model ID [ET5410|ET5420|ET5410A+|...]
                    only required if `*IDN?` does not return a valid ID
                    e.g. for Mustool branded ET5410A+
        """
        rm = pyvisa.ResourceManager()
        self.connection = rm.open_resource(RID)
        self.connection.baud_rate = baudrate
        self.connection.query_delay = delay
        self.connection.timeout = timeout
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
            self.Channels = [self.ch1]
        elif self.idn["model"] == "ET5420A+":
            self.ch1 = channel("1", self.write, self.query)
            self.ch2 = channel("2", self.write, self.query)
            self.Channels = [self.ch1, self.ch2]
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
        time.sleep(self.connection.query_delay)
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

    def query(self, command, nrows=1, timeout=None):
        """Write command to connection and return answer value
        By default, reads 1 line of response.
        If you expect more, you need to set `nrows` to the respective value
        If you expect the respinse to be slow, you can set a ne timout just for
        this request
        """

        if timeout is not None:
            _timeout = self.connection.timeout
            self.connection.timeout = timeout

        self.connection.write(command)
        time.sleep(self.connection.query_delay)
        ret = []
        for i in range(nrows):
            value = self.connection.read()
            time.sleep(self.connection.query_delay)
            ret.append(value)
            if value == "Rcmd err":
                print(f"Command '{command}' failed ({value})", file=sys.stderr)
                return None
        if timeout is not None:
            self.connection.timeout = _timeout
        return ret if len(ret) > 1 else ret[0]

    def close(self):
        "close connection to instument"
        self.connection.close()

    def beep(self):
        "Beep"
        self.write("SYST:BEEP")
    
    def reset(self):
        "Reset device to default"
        self.connection.write("RST")

    def trigger(self):
        "send trigger event"
        self.connection.write("TRG")

    def unlock(self):
        """unlock the local interface

        After unlocking, buttons on the device work again.
        Sending a SCPI command will lock the device again.
        """
        self.write("SYST:LOCA")

    def fan(self):
        "return fan state"
        return self.query("SELF:FAN?")


