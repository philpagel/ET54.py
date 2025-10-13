#!/bin/env python3
import argparse
import time, datetime
from ET54 import ET54


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="/dev/ttyUSB0", help="USB device path")
    parser.add_argument(
        "--rate_A", nargs="+", type=float, default=[1.0], help="Discharge rate in Amps"
    )
    parser.add_argument("--cutoff", type=float, default=10.5, help="Cutoff Voltage")

    args = parser.parse_args()

    el = ET54(f"ASRL{args.device}::INSTR")

    print("Battery discharge")
    print(f"Constant-Current: " + ", ".join(f"{_:.2f}" for _ in args.rate_A))
    print(f"Cutoff Voltage: {args.cutoff:.2f}")
    # set ranges
    el.ch1.off()
    el.ch1.Vrange = "high" if args.cutoff > 15 else "low"

    try:
        start = datetime.datetime.now()
        last = start
        logfile = f"discharge.{last.isoformat()}.csv"
        print("timestamp, V, I, P, R, Ah, Wh")
        with open(logfile, "w") as _fh:
            _fh.write("# timestamp, V, I, P, R, Ah, Wh\n")
        total_Wh = 0
        total_Ah = 0
        for set_A in args.rate_A:
            el.ch1.off()
            el.ch1.Crange = "high" if set_A > 3 else "low"
            el.ch1.BATT_mode("CC", set_A, "V", args.cutoff)
            el.ch1.on()
            last = datetime.datetime.now()

            # monitor voltage, current, power etc.
            while True:
                volt = el.ch1.read_voltage()
                current = el.ch1.read_current()
                power = el.ch1.read_power()
                resistance = el.ch1.read_resistance()
                now = datetime.datetime.now()
                delta = (now - last).total_seconds()
                elapsed = (now - start).total_seconds()
                last = now
                total_Wh += volt * current * delta / 3600
                total_Ah += current * delta / 3600
                line = (
                    f'{time.strftime("%H:%M:%S", time.gmtime(elapsed))}, {volt:.2f}, {current:.2f}, '
                    f"{power:.2f}, {resistance:.2f}, {total_Ah:.4f}, {total_Wh:.4f}"
                )
                print(line)
                with open(logfile, "a") as _fh:
                    _fh.write(line + "\n")
                if current < 0.01:
                    el.ch1.off()
                    break
                time.sleep(1)
    except Exception as _e:
        el.ch1.off()
        raise
    except KeyboardInterrupt:
        el.ch1.off()


if __name__ == "__main__":
    main()
