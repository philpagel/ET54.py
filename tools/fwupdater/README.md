# ET54xx firmware updater

East Tester will provide firmware images if begged persistently.  The procedure
recommend by them is pretty awkward and involves running a Windows-only
terminal emulator software of unknown origin. So I wrote this little programm
to conduct firmware updates with less trouble (and not only on Windows).

You can also use this tool to flash original East-Tester Firmware to *Mustool*
branded devices.


## Status

[![works on my machine badge](https://cdn.jsdelivr.net/gh/nikku/works-on-my-machine@v0.4.0/badge.svg)](https://github.com/nikku/works-on-my-machine)

I can reliably flash my ET5410A+ load using this tool and I have received 
reports from others using it sucessfully.

This is a re-write (wiht some AI help) of my original Python tool to make it
easier to use without having to install Python and dependencies, first.


## Installation

Download a binary (Windows/LINUX/MacOS) from the [latest
release](https://github.com/philpagel/ET54.py/releases/latest). No installation
required. On Linux/Mac, make sure to make the binary executable, first:

    chmod a+x et54fwupdater


## Firmware Upgrade Instructions

1. Turn *off* the load
2. Connect the load to your computer with a USB cable.  
3. Find the firmware file in the archive provided by the manufacturer. It has
   the extension `.hex`. E.g. `ET54A+.150.025(ET5410 ET5420 ET5408).hex`,
   `ET54A+.150.X26(强制界面).hex` or something like that. I also provide some
   in the [images](images/) folder.
4. Open a terminal/shell and run this tool:   
```sh
   ./et54fwupdater -s /dev/ttyUSB0 images/ET54A+.150.X26.hex   # LINUX 
   .\et54fwupdater.exe -s COM3 images\ET54A+.150.X26.hex       # Windows 
```
5. Turn *on* the load  
   You should see a menu in Chinese followed by a progress line on your computer.  
   The load's screen will say "Downloading..." 
6. Wait for firmware upload to finish  
   The loads display will then show something like this:
```
   Programming :  xxxxxxxxx
   CH1 State   :  R5   
```
7. Wait until the load shows "Please Reset!" on the display.
8. Turn load off and on again.

The entire process will take about 13 minutes (~11min for the upload and another
~2 minutes for programming).

The bootloader is very temperamental: It may take several attempts until it
is successfully triggered.


## Example session

```
❯ ./et54fwupdater -s /dev/ttyUSB1 images/ET54A+.150.X26.hex
Sanity checking hexfile
Waiting for bootloader. Please turn on the device now.
  .       
> 杭州中创
> Bootloader Ver:3.00
> ----------------------
> [1]下载程序
> [2]运行程序
> [?]帮助
> ----------------------
Selecting: [1].
> 删除Flash...
> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
> 删除完成!
> 准备接收文件...
Uploading 'images/ET54A+.150.X26.hex'
Progress: 20075/20075 rows 100%
> 下载成功!
Upload finished.
 Wait for load to display 'Please Reset!' before cycling power.
```

Lines starting with `>` echo the output received from the device.


## Usage 

```
❯ ./et54fwupdater --help
ET54xx electronic load firmware updater

Usage: et54fwupdater [OPTIONS] <HEXFILE>

Arguments:
  <HEXFILE>  Firmware hex file

Options:
  -s, --serialdev <SERIALDEV>  Serial device / COM port [default: /dev/ttyUSB0]
  -b, --baudrate <BAUDRATE>    baud rate [default: 14400]
  -q, --quiet                  Suppress console output
  -h, --help                   Print help
  -V, --version                Print version
```


## Trouble shooting

What to do if things don't work/go wrong and/or you have soft-bricked your
device and/or the update ends in an error message and/or the bootloader will not
launch? Here are some things to check or do:

### The tool cannot connect ot the load

1. Double check that you are using the *correct* serial device (`COMx` port or
   `/dev/ttyUSBx`).
2. Make sure your OS has drivers for the CH340 serial converter used by the device. 


### The tool hangs or exits with a cryptic error message

If the updater seems stuck after you turn on the load, the bootloader did not 
fire up. That happens a lot.

1. Try again, many times if necessary.
    - Turn off the load
    - Kill the updater program
    - Start over
2. Try pressing the power button faster/slower/with more passion/while praying
   to the god of firmware updates
3. Try starting with the load powered on. Start the updater, then turn the
   load off and back on.
4. Reset everything:
    - Turn off the load and unplug the power lead.
    - Unplug the USB cable from the computer. 
    - Wait for 20 minutes or even over night until the last cap inside has
      fully discharged.
    - Maybe even reboot the computer.
    - Say a few incantations.
    - Start over.


### The load is bricked @#!?!!

1. Don't panic! Even if the device appears dead, the bootloader is still there
   and the device will almost certainly be recoverable. (Guess how I know...)
2. Verifiy that the hex file is ok:
    - double check that the hexfile is intended for your specific device and
      you did not accidentally use the firmware file of some other device.
    - verify the checksum if you got it from here.
    - inspect the file in a text editor. It should look something like this:  
```
:020000040800F2
:10000000781A002039020008590C0008D30B0008A8
:10001000550C0008F3040008F1140008000000006B
:10002000000000000000000000000000E50F0008D4

    [...]

:00000001FF
```
3. Reset everything:
    - Unplug the USB cable from the computer. 
    - Maybe even reboot the computer.
    - Turn off the load and unplug the power lead.
    - Wait for 20 minutes or even over night until the last cap inside has
      fully discharged.
    - Say a few incantations.
    - Start over.

If all of that fails, you are officially entitled to panic (Just kidding.)

