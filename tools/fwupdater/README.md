# ET54xx firmware updater

East Tester will provide firmware updates upon request, if begged persistently.
The procedure recommend by them is pretty awkward and involves running a
Windows-only terminal emulator software of unknown origin. So I wrote this
little script to conduct firmware updates on any OS and without untrusted
software.


## Instructions

1. Find the firmware file in the archive provided by the manufacturer. It has
   the extension `.hex`. E.g. `ET54A+.150.025(ET5410 ET5420 ET5408).hex`,
   `ET54A+.150.X26(强制界面).hex` or something like that.
2. Connect a USB cable to the load and your computer
3. Start this tool. E.g.:
```sh
./fwupdater.py -s /dev/ttyUSB0 ET54A+.150.X26.hex   # LINUX
./fwupdater.py -s COM3 ET54A+.150.X26.hex           # Windows
```
4. Wait until the program finishes.
5. Wait until the load shows "Please Reset" on the display
6. Turn load off and on again.
7. Done.

# Example session

    ❯ ./fwupdater.py -s /dev/ttyUSB1 ET54A+.150.X26.hex

    杭州中创
    Bootloader Ver:3.00

    ----------------------
    [1]下载程序

    [2]运行程序

    [?]帮助
    ----------------------

    删除Flash...
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    删除完成!

    准备接收文件...
    Uploading 'ET54A+.150.X26.hex': 903151 bytes
    Progress: 100%下载成功!
    Upload successful.
    Wait for load to display 'Please Reset!' before cycling power.



## Usage 

    usage: fwupdater.py [-h] [-s SERIALDEV] [-q] hexfile

    Perform firmware update on an ET54xx electronic load.

    positional arguments:
      hexfile               path to hexfile, e.g. image.hex

    options:
      -h, --help            show this help message and exit
      -s, --serialdev SERIALDEV
                            Serial device (default: /dev/ttyUSB1)
      -q, --quiet           Run quietly without any output (default: False)

# Images

I am providing two firmware images:

    ET54A+.150.025.hex
    ET54A+.150.X26.hex

The latter one is what I got from East Tester, the other one was found on the
EEVBlog Forum a bit earlier. Ask the manufacturer if there is a later version.

