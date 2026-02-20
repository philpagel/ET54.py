#!/usr/bin/env python3
"Firmware updater for ET5xx series electronic loads"

import time, serial, sys, os.path, argparse

def main():
    parser = argparse.ArgumentParser(
        description="Perform firmware update on an ET54xx electronic load.",
        epilog="""Instructions: 1. Turn off the load and connect usb lead. 
        2. Start this programm. 3. Turn on the load and wait for program to finish.
        4. When display shows 'Please reset!', power cycle load.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-s", "--serialdev", default="/dev/ttyUSB1", help="Serial device")
    parser.add_argument("-i", "--info", action="store_true", help="Show info only - do not upload anything")
    parser.add_argument( "-q", "--quiet", action="store_true", help="Run quietly without any output")
    parser.add_argument("hexfile", help="path to hexfile, e.g. image.hex")
    global args
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

    trigger(dev)
    upload(dev, args.hexfile)


def logger(*dat, end="\n", flush=True):
    "print logging output"
    if not args.quiet:
        print(" ".join(dat), end=end, flush=flush)


def trigger(dev):
    "trigger bootloader"

    logger("Sending magic number. Please turn on the device now.") 

    # send magic nubmer until we get into bootloader menu
    magic = bytes.fromhex("1b42543936057a")
    while True:
        logger(".", end="") 
        dev.write(magic)
        dev.flush()
        time.sleep(0.2)
        dev.in_waiting
        if dev.in_waiting > 0:  # load is responding
            break
    logger()


def upload(dev, hexfile):
    "upload the hexfile"
    # Upload hexfile when device is ready
    menucomplete = 0
    while True:
        line = dev.readline().decode("gb2312").rstrip()
        logger(">",line) 
        if "帮助" in line:  # "Help"
            menucomplete = 1
        if "----------------------" in line and menucomplete:
            if args.info:
                break
            else:
                dev.write("1".encode("gb2312")) # select option 1: file upload
                logger("Selecting: [1] File Upload.")
        if "准备接收文件" in line:  # "Prepare to receive file"
            try:
                filesize = os.path.getsize(hexfile)
            except:
                sys.exit(f"Error: cannot open hexfile '{hexfile}'")
            logger(f"Uploading '{hexfile}': {filesize} bytes")
            
            try:
                with open(hexfile, "rb") as infile:
                    sent = 0
                    while chunk := infile.read(1024):
                        dev.write(chunk)
                        dev.flush()
                        sent += len(chunk)
                        percent = (sent / filesize) * 100
                        logger(f"\rProgress: {percent:0.0f}%", end="")
                dev.readline()  # skip the progress dots
                logger()
            except:
                sys.exit(f"Error: cannot open hexfile '{hexfile}'")

        if "下载成功!" in line:     # "Download successful!"
            logger("Upload successful.")
            logger("Wait for load to display 'Please Reset!' before cycling power.")

            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
