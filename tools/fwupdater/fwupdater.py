#!/usr/bin/env python3
"Firmware updater for ET5xx series electronic loads"

import time, serial, sys, os.path, argparse

parser = argparse.ArgumentParser(
    description="Perform firmware update on an ET54xx electronic load.",
    epilog="""Instructions: 1. Turn off the load and connect usb lead. 
    2. Start this programm. 3. Turn on the load and wait for program to finish.
    4. When display shows 'Please reset!', power cycle load.""",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("-s", "--serialdev", default="/dev/ttyUSB1", help="Serial device")
parser.add_argument( "-q", "--quiet", action="store_true", help="Run quietly without any output")
parser.add_argument("hexfile", help="path to hexfile, e.g. image.hex")
args = parser.parse_args()


# connect to serial device
try:
    dev = serial.Serial(
        args.serialdev,
        baudrate=14400,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=0.1,
        xonxoff=0,
        rtscts=0,
    )
except serial.serialutil.SerialException:
    sys.exit(f"Error: Cannot open serial device {args.serialdev}")

# send magic nubmer until we get into bootloader menu
magic = bytes.fromhex("1b42543936057a")
while True:
    dev.write(magic)
    dev.flush()
    time.sleep(0.2)
    dev.in_waiting
    if dev.in_waiting > 0:
        break

# Upload hexfile when device is ready
while True:
    line = dev.readline().decode("gb2312").rstrip()
    if not args.quiet:
        print(line) 
    if "帮助" in line:  # "Help"
        dev.write("1".encode("gb2312")) # select option 1: file upload
    if "准备接收文件" in line:  # "Prepare to receive file"
        filesize = os.path.getsize(args.hexfile)
        if not args.quiet:
            print(f"Uploading '{args.hexfile}': {filesize} bytes")

        with open(args.hexfile, "rb") as hexfile:
            sent = 0
            while chunk := hexfile.read(1024):
                dev.write(chunk)
                dev.flush()
                sent += len(chunk)
                percent = (sent / filesize) * 100
                if not args.quiet:
                    print(f"\rProgress: {percent:0.0f}%", end="", flush=True)
        dev.readline()  # skip the progress dots

    if "下载成功!" in line:     # "Download successful!"
        if not args.quiet:
            print("Upload successful.")
            print("Wait for load to display 'Please Reset!' before cycling power.")

        break
