# Creative Pebble V3 aux fixer

**I’m not responsible for fried speakers, use this script at your own risk**

This repo contains a small script to modify the firmware of the Creative Pebble V3 speakers. The flashing part has to be done on a Windows machine. A VM didn’t work for me, but you might have more luck.
### The problem
This model of speaker suffers from a weird design flaw that makes the little sensor inside the 3.5mm port die. When it stops working, it is impossible to use the aux input in any way. Let me tell you, using USB-C input on macOS for years was not fun. These speakers are quite buggy with a digital connection.
### The solution
Either tackling the problem with a [hardware repair](https://www.youtube.com/watch?v=_k4gT8VE1oU),
or this script. It bypasses the sensor completely, aux stays in mode rotation even if nothing’s detected. Surprisingly, audio works without any problem, and aux stays selected even after a power cycle.

### How to use it
#### 1. Getting the original firmware
It can be found in the [official updater](https://support.creative.com/Products/ProductDetails.aspx?prodID=23507&prodName=Creative+Pebble+V3). This patcher targets specifically **v3.8.0.0** (the latest at the time of writing) and will refuse to work if it detects a mismatch. You can edit the script to bypass this, but another version will probably mess stuff up.
#### 2. Extracting the firmware from the updater
Use [innoextract](https://github.com/dscharrer/innoextract).

```
$ innoextract PebbleV3FWInstaller_3.8.0.0.exe
```

The firmware will be in `{innoextract folder}\tmp\Tool\Pebble.fw`.

#### 3. Patching
Make sure you have Python 3 installed. Download and throw the script in the `Tool` folder, open a terminal there, and patch:
```
$ python3 patch_pebble_fw.py Pebble.fw
```
It will produce a `Pebble_patched.fw` file.

#### 4. Putting the speakers in flashing mode
Turn them off, flip the gain switch on the bottom of the right speaker to ‘A’, and hold the Bluetooth/Mode button while turning the speaker on. If the led is **cyan**, you’re good to go.

#### 5. Flashing
This part needs to be done on a Windows PC. Still in the Tools folder, execute from a cmd prompt
```
ATSSDK.exe Pebble_patched.fw
```
Wait for the process to finish (ATSSDK will close and the speakers will reboot), and reboot the speakers again.

#### 6. Using the speakers
If everything worked correctly, the Bluetooth/mode button will also cycle to aux mode (cyan led).