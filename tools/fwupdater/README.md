# ET54xx firmware updater

East Tester will provide firmware images if begged persistently. 
The procedure recommend by them is pretty awkward and involves running a
Windows-only terminal emulator software of unknown origin. So I wrote this
little programm to conduct firmware updates with less trouble (and also on LINUX).

You can also use this tool to flash original East-Tester Firmware to *Mustool*
branded devices.


## Status

[![works on my machine badge](https://cdn.jsdelivr.net/gh/nikku/works-on-my-machine@v0.4.0/badge.svg)](https://github.com/nikku/works-on-my-machine)

I.e. I have successfully flashed an image to my ET5410A+ load using 
this tool. 

This is a re-write of my original Python tool to make it easier to use without
having to install Python and dependencies, first.

I'd be *very* grateful for feedback by anyone who was brave enough to give my
tool a try, especially, if you are running Windows.


#### Risk assessment

* If something goes wrong, you may soft-brick your device
* I consider the risk of hard-bricking to be almost zero because
  sending a hexfile will preserve the bootloader and you should be able to
  bring your device back to live using this tool or the manufacturer's tool (if
  you can get that to work).


## Firmware Upgrade Instructions

1. Turn *off* the load
2. Connect the load to your computer with a USB cable.  
3. Find the firmware file in the archive provided by the manufacturer. It has
   the extension `.hex`. E.g. `ET54A+.150.025(ET5410 ET5420 ET5408).hex`,
   `ET54A+.150.X26(强制界面).hex` or something like that.
4. Start this tool.  
   You may have to make it executable, first (`chmod a+x et44fwupdater`)
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
   Ch1 State   :  R5   
````
7. Wait until the load shows "Please Reset!" on the display.
8. Turn load off and on again.

The entire process will take about 12 minutes.

The bootloader is very temperamental: It may take several attempts until it
is successfully triggered.


# Example session

```
❯ ./target/release/et54fwupdater -s /dev/ttyUSB1 images/ET54A+.150.X26.hex
Sending magic number. Please turn on the device now.
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
❯ ./target/release/et54fwupdater --help
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



# Images

I have a few firmware images that I found online and/or got from the manufacturer:

* [`ET54A+.150.025.hex`](./images/ET54A+.150.025.hex): V2.01.2352.025
* [`ET54A+.150.A15.hex`](./images/ET54A+.150.A15.hex): V2.01.2408.A15
* [`ET54A+.150.X26.hex`](./images/ET54A+.150.X26.hex): V2.01.2480.X26 (latest version as of writing)

# Installation

Download a binary from the [latest release](https://github.com/philpagel/ET54.py/releases/latest). No installation required. On
Linux, make sure to make the binary executable

    chmod a+x et54fwupdater


# Trouble shooting

What to do if things don't work/go wrong and/or you have soft-bricked your
device and/or the update ends in an error message and/or the bootloader will not
launch? Here are some things to check or do:

1. Don't panic! Even if the device appears dead, the bootloader is still there
   and the device will almost certainly be recoverable. (Guess how I know...)
2. Make sure your OS supports the CH340 usb-serial converter. Install drivers
   if necessary.
3. Double check that you are using the *correct* serial device (`COMx` port or
   `/dev/ttyUSBx`).
5. Try again, several times if necessary.
    - Turn off the load
    - Kill the updater program
    - Start over
6. When turning the device on, do so swiftly. Sometimes when pressing the power
   button too slowly, triggering the bootloader fails.
7. Reset everything:
    - Unplug the USB cable from the computer. 
    - Maybe even reboot the computer.
    - Turn off the load and unplug the power lead.
    - Wait for 20 minutes or even over night until the last cap inside has
      fully discharged.
    - Say a few incantations.
    - Start over.

If all of that fails, you are officially entitled to panic (Just kidding.)


