# ET54xx firmware updater

East Tester will provide firmware updates upon request, if begged persistently.
The procedure recommend by them is pretty awkward and involves running a
Windows-only terminal emulator software of unknown origin. So I wrote this
little script to conduct firmware updates on any OS and without untrusted
software.

## Status

Tested and working on ET5410A+. I don't know if the older Version (ET54xx without the "A+") 
use the same bootloader. Feedback is welcome!

## Firmware Upgrade Instructions

1. Find the firmware file in the archive provided by the manufacturer. It has
   the extension `.hex`. E.g. `ET54A+.150.025(ET5410 ET5420 ET5408).hex`,
   `ET54A+.150.X26(强制界面).hex` or something like that.
2. With the load turned off, connect a USB cable to the load and your computer
3. Start this tool. E.g.:
```sh
./fwupdater.py -s /dev/ttyUSB0 ET54A+.150.X26.hex   # LINUX
./fwupdater.py -s COM3 ET54A+.150.X26.hex           # Windows
```
4. Turn on the load
5. Wait until the program finishes.
6. Wait until the load shows "Please Reset" on the display
7. Turn load off and on again.
8. Done.

# Example session

    ❯ ./fwupdater.py -s /dev/ttyUSB0 ET54A+.150.X26.hex
    Sending magic number. Please turn on the device now.
    ............
    > 
    > 杭州中创
    > Bootloader Ver:3.00
    > 
    > ----------------------
    > [1]下载程序
    > 
    > [2]运行程序
    > 
    > [?]帮助
    > ----------------------
    Selecting: [1] File Upload.
    > 
    > 删除Flash...
    > >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    > 删除完成!
    > 
    > 准备接收文件...
    Uploading 'ET54A+.150.X26.hex': 903151 bytes
    Progress: 100%
    > 下载成功!
    Upload successful.
    Wait for load to display 'Please Reset!' before cycling power.

Lines starting with `>` echo the output received from the device.


## Usage 

    usage: fwupdater.py [-h] [-s SERIALDEV] [-q] hexfile

    Perform firmware update on an ET54xx electronic load.

    positional arguments:
      hexfile               path to hexfile, e.g. image.hex

    options:
      -h, --help            show this help message and exit
      -s, --serialdev SERIALDEV
                            Serial device (default: /dev/ttyUSB1)
      -i, --info            Show info only - do not upload anything (default: False)

      -q, --quiet           Run quietly without any output (default: False)

If you find the tool too verbose, use the `-q/--quiet` flag.

When setting `-i/--info`, the program will activate the bootloader but not
trigger the hex file upload. You still need to provide the hexfile argument,
but it is OK if that file doesn't even exist, in this case. This option may be
useful for debugging, later – i.e.  finding the bootloader version.


# Images

I am providing two firmware images:

* `ET54A+.150.025.hex`: Found in the EEVBlog Forum
* `ET54A+.150.X26.hex`: Received from EastTester. Presumably the latest version as of writing

Ask the manufacturer if there is a later version.

