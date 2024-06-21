# Example of how to use this tool with RIOT OS.

This will use fake boards to go through the workflow that RIOTers will use.

## Steps

1. I guess we need to clone RIOT first and can operate from there.
```bash
$ git clone --branch 2024.01 --depth 1 -q https://github.com/RIOT-OS/RIOT.git ~/RIOT
```

2. See... We did a secret cd to the RIOT dir.
```bash
$ pwd 
~/RIOT
```

3. Now let's get out board list.
```bash
$ inet-nm-update-from-os examples/hello-world
Getting features_provided for acd52832
Getting features_provided for adafruit-clue
Getting features_provided for adafruit-grand-central-m4-express
Getting features_provided for adafruit-itsybitsy-m4
Getting features_provided for adafruit-itsybitsy-nrf52
Getting features_provided for adafruit-pybadge
Getting features_provided for airfy-beacon
Getting features_provided for alientek-pandora
Getting features_provided for arduino-due
Getting features_provided for arduino-duemilanove
Getting features_provided for arduino-leonardo
Getting features_provided for arduino-mega2560
Getting features_provided for arduino-mkr1000
Getting features_provided for arduino-mkrfox1200
Getting features_provided for arduino-mkrwan1300
Getting features_provided for arduino-mkrzero
Getting features_provided for arduino-nano
Getting features_provided for arduino-nano-33-ble
Getting features_provided for arduino-nano-33-iot
Getting features_provided for arduino-uno
Getting features_provided for arduino-zero
Getting features_provided for atmega1284p
Getting features_provided for atmega256rfr2-xpro
Getting features_provided for atmega328p
Getting features_provided for atmega328p-xplained-mini
Getting features_provided for atmega8
Getting features_provided for atxmega-a1-xplained
Getting features_provided for atxmega-a1u-xpro
Getting features_provided for atxmega-a3bu-xplained
Getting features_provided for avr-rss2
Getting features_provided for avsextrem
Getting features_provided for b-l072z-lrwan1
Getting features_provided for b-l475e-iot01a
Getting features_provided for b-u585i-iot02a
Getting features_provided for bastwan
Getting features_provided for blackpill-stm32f103c8
Getting features_provided for blackpill-stm32f103cb
Getting features_provided for bluepill-stm32f030c8
Getting features_provided for bluepill-stm32f103c8
Getting features_provided for bluepill-stm32f103cb
Getting features_provided for calliope-mini
Getting features_provided for cc1312-launchpad
Getting features_provided for cc1350-launchpad
Getting features_provided for cc1352-launchpad
Getting features_provided for cc1352p-launchpad
Getting features_provided for cc2538dk
Getting features_provided for cc2650-launchpad
Getting features_provided for cc2650stk
Getting features_provided for derfmega128
Getting features_provided for derfmega256
Getting features_provided for dwm1001
Getting features_provided for e104-bt5010a-tb
Getting features_provided for e104-bt5011a-tb
Getting features_provided for e180-zg120b-tb
Getting features_provided for ek-lm4f120xl
Getting features_provided for esp32-ethernet-kit-v1_0
Getting features_provided for esp32-ethernet-kit-v1_1
Getting features_provided for esp32-ethernet-kit-v1_2
Getting features_provided for esp32-heltec-lora32-v2
Getting features_provided for esp32-mh-et-live-minikit
Getting features_provided for esp32-olimex-evb
Getting features_provided for esp32-ttgo-t-beam
Getting features_provided for esp32-wemos-lolin-d32-pro
Getting features_provided for esp32-wroom-32
Getting features_provided for esp32-wrover-kit
Getting features_provided for esp32c3-devkit
Getting features_provided for esp32c3-wemos-mini
Getting features_provided for esp32s2-devkit
Getting features_provided for esp32s2-lilygo-ttgo-t8
Getting features_provided for esp32s2-wemos-mini
Getting features_provided for esp32s3-box
Getting features_provided for esp32s3-devkit
Getting features_provided for esp32s3-pros3
Getting features_provided for esp32s3-usb-otg
Getting features_provided for esp32s3-wt32-sc01-plus
Getting features_provided for esp8266-esp-12x
Getting features_provided for esp8266-olimex-mod
Getting features_provided for esp8266-sparkfun-thing
Getting features_provided for f4vi1
Getting features_provided for feather-m0
Getting features_provided for feather-m0-lora
Getting features_provided for feather-m0-wifi
Getting features_provided for feather-nrf52840
Getting features_provided for feather-nrf52840-sense
Getting features_provided for firefly
Getting features_provided for frdm-k22f
Getting features_provided for frdm-k64f
Getting features_provided for frdm-kl43z
Getting features_provided for frdm-kw41z
Getting features_provided for gd32vf103c-start
Getting features_provided for generic-cc2538-cc2592-dk
Getting features_provided for hamilton
Getting features_provided for hifive1
Getting features_provided for hifive1b
Getting features_provided for hip-badge
Getting features_provided for i-nucleo-lrwan1
Getting features_provided for ikea-tradfri
Getting features_provided for im880b
Getting features_provided for iotlab-a8-m3
Getting features_provided for iotlab-m3
Getting features_provided for limifrog-v1
Getting features_provided for lobaro-lorabox
Getting features_provided for lora-e5-dev
Getting features_provided for lsn50
Getting features_provided for maple-mini
Getting features_provided for mbed_lpc1768
Getting features_provided for mcb2388
Getting features_provided for mega-xplained
Getting features_provided for microbit
Getting features_provided for microbit-v2
Getting features_provided for microduino-corerf
Getting features_provided for msb-430
Getting features_provided for msb-430h
Getting features_provided for msba2
Getting features_provided for msbiot
Getting features_provided for mulle
Getting features_provided for native
Getting features_provided for nrf51dk
Getting features_provided for nrf51dongle
Getting features_provided for nrf52832-mdk
Getting features_provided for nrf52840-mdk
Getting features_provided for nrf52840-mdk-dongle
Getting features_provided for nrf52840dk
Getting features_provided for nrf52840dongle
Getting features_provided for nrf52dk
Getting features_provided for nrf5340dk-app
Getting features_provided for nrf6310
Getting features_provided for nrf9160dk
Getting features_provided for nucleo-f030r8
Getting features_provided for nucleo-f031k6
Getting features_provided for nucleo-f042k6
Getting features_provided for nucleo-f070rb
Getting features_provided for nucleo-f072rb
Getting features_provided for nucleo-f091rc
Getting features_provided for nucleo-f103rb
Getting features_provided for nucleo-f207zg
Getting features_provided for nucleo-f302r8
Getting features_provided for nucleo-f303k8
Getting features_provided for nucleo-f303re
Getting features_provided for nucleo-f303ze
Getting features_provided for nucleo-f334r8
Getting features_provided for nucleo-f401re
Getting features_provided for nucleo-f410rb
Getting features_provided for nucleo-f411re
Getting features_provided for nucleo-f412zg
Getting features_provided for nucleo-f413zh
Getting features_provided for nucleo-f429zi
Getting features_provided for nucleo-f439zi
Getting features_provided for nucleo-f446re
Getting features_provided for nucleo-f446ze
Getting features_provided for nucleo-f722ze
Getting features_provided for nucleo-f746zg
Getting features_provided for nucleo-f767zi
Getting features_provided for nucleo-g070rb
Getting features_provided for nucleo-g071rb
Getting features_provided for nucleo-g431rb
Getting features_provided for nucleo-g474re
Getting features_provided for nucleo-l011k4
Getting features_provided for nucleo-l031k6
Getting features_provided for nucleo-l053r8
Getting features_provided for nucleo-l073rz
Getting features_provided for nucleo-l152re
Getting features_provided for nucleo-l412kb
Getting features_provided for nucleo-l432kc
Getting features_provided for nucleo-l433rc
Getting features_provided for nucleo-l452re
Getting features_provided for nucleo-l476rg
Getting features_provided for nucleo-l496zg
Getting features_provided for nucleo-l4r5zi
Getting features_provided for nucleo-l552ze-q
Getting features_provided for nucleo-wl55jc
Getting features_provided for nz32-sc151
Getting features_provided for olimex-msp430-h1611
Getting features_provided for olimex-msp430-h2618
Getting features_provided for olimexino-stm32
Getting features_provided for omote
Getting features_provided for opencm904
Getting features_provided for openlabs-kw41z-mini
Getting features_provided for openlabs-kw41z-mini-256kib
Getting features_provided for openmote-b
Getting features_provided for openmote-cc2538
Getting features_provided for p-l496g-cell02
Getting features_provided for p-nucleo-wb55
Getting features_provided for particle-argon
Getting features_provided for particle-boron
Getting features_provided for particle-xenon
Getting features_provided for pba-d-01-kw2x
Getting features_provided for phynode-kw41z
Getting features_provided for pinetime
Getting features_provided for pyboard
Getting features_provided for qn9080dk
Getting features_provided for reel
Getting features_provided for remote-pa
Getting features_provided for remote-reva
Getting features_provided for remote-revb
Getting features_provided for rpi-pico
Getting features_provided for rpi-pico-w
Getting features_provided for ruuvitag
Getting features_provided for samd10-xmini
Getting features_provided for samd20-xpro
Getting features_provided for samd21-xpro
Getting features_provided for same54-xpro
Getting features_provided for saml10-xpro
Getting features_provided for saml11-xpro
Getting features_provided for saml21-xpro
Getting features_provided for samr21-xpro
Getting features_provided for samr30-xpro
Getting features_provided for samr34-xpro
Getting features_provided for seeedstudio-gd32
Getting features_provided for seeeduino_arch-pro
Getting features_provided for seeeduino_xiao
Getting features_provided for sensebox_samd21
Getting features_provided for serpente
Getting features_provided for sipeed-longan-nano
Getting features_provided for sipeed-longan-nano-tft
Getting features_provided for slstk3400a
Getting features_provided for slstk3401a
Getting features_provided for slstk3402a
Getting features_provided for slstk3701a
Getting features_provided for sltb001a
Getting features_provided for sltb009a
Getting features_provided for slwstk6000b-slwrb4150a
Getting features_provided for slwstk6000b-slwrb4162a
Getting features_provided for slwstk6220a
Getting features_provided for sodaq-autonomo
Getting features_provided for sodaq-explorer
Getting features_provided for sodaq-one
Getting features_provided for sodaq-sara-aff
Getting features_provided for sodaq-sara-sff
Getting features_provided for spark-core
Getting features_provided for stk3200
Getting features_provided for stk3600
Getting features_provided for stk3700
Getting features_provided for stm32f030f4-demo
Getting features_provided for stm32f0discovery
Getting features_provided for stm32f3discovery
Getting features_provided for stm32f429i-disc1
Getting features_provided for stm32f429i-disco
Getting features_provided for stm32f469i-disco
Getting features_provided for stm32f4discovery
Getting features_provided for stm32f723e-disco
Getting features_provided for stm32f746g-disco
Getting features_provided for stm32f7508-dk
Getting features_provided for stm32f769i-disco
Getting features_provided for stm32g0316-disco
Getting features_provided for stm32l0538-disco
Getting features_provided for stm32l476g-disco
Getting features_provided for stm32l496g-disco
Getting features_provided for stm32mp157c-dk2
Getting features_provided for teensy31
Getting features_provided for telosb
Getting features_provided for thingy52
Getting features_provided for ublox-c030-u201
Getting features_provided for udoo
Getting features_provided for usb-kw41z
Getting features_provided for waspmote-pro
Getting features_provided for waveshare-nrf52840-eval-kit
Getting features_provided for weact-f401cc
Getting features_provided for weact-f401ce
Getting features_provided for weact-f411ce
Getting features_provided for wemos-zero
Getting features_provided for xg23-pk6068a
Getting features_provided for yarm
Getting features_provided for yunjia-nrf51822
Getting features_provided for z1
Getting features_provided for zigduino

Updated ~/board_info.json
```

4. We can also setup out env so we don't need to worry about using the namespaced env vars.
Keep in mind we have a `scripts/riot-os-env-setup`.
```bash
$ inet-nm-export --apply-to-shared BOARD ${NM_BOARD}
Added BOARD=${NM_BOARD} to shared env vars
Written to ~/env.json
```

```bash
$ inet-nm-export --apply-to-shared BUILD_IN_DOCKER 1
Added BUILD_IN_DOCKER=1 to shared env vars
Written to ~/env.json
```

```bash
$ inet-nm-export --apply-to-shared DEBUG_ADAPTER_ID ${NM_SERIAL}
Added DEBUG_ADAPTER_ID=${NM_SERIAL} to shared env vars
Written to ~/env.json
```

```bash
$ inet-nm-export --apply-to-shared PORT ${NM_PORT}
Added PORT=${NM_PORT} to shared env vars
Written to ~/env.json
```

5. Now let's pretend to plug in 2 boards.
```bash
$ inet-nm-fake-usb --id board_1
Added fake device with ID board_1.
Saved fake devices to ~/fakes.json.
```

```bash
$ inet-nm-fake-usb --id board_2
Added fake device with ID board_2.
Saved fake devices to ~/fakes.json.
```

6. Let's commission, since there are multiple boards we need to select one.
```bash
$ inet-nm-commission 
Found 0 saved nodes in ~
Select the node
1. /dev/ttyUSB100 QinHeng Electronics USB Serial 3ed115bd
2. /dev/ttyUSB101 QinHeng Electronics USB Serial 76918b64
> 1
Select board name for QinHeng Electronics USB Serial
> samr21-xpro
Updated ~/nodes.json
```

```bash
$ inet-nm-commission 
Found 1 saved nodes in ~
Select board name for QinHeng Electronics USB Serial
> nucleo-f103rb
Updated ~/nodes.json
```

7. OK, we should maybe to something like `make flash-only test` but we can't since the boards are... fake. So let's do something board specific that doesn't really need a board.
```bash
$ inet-nm-exec "make info-cpu -C examples/hello-world"
NODE:0:BOARD:samr21-xpro: make: Entering directory '~/RIOT/examples/hello-world'
NODE:1:BOARD:nucleo-f103rb: make: Entering directory '~/RIOT/examples/hello-world'
NODE:0:BOARD:samr21-xpro: samd21
NODE:0:BOARD:samr21-xpro: make: Leaving directory '~/RIOT/examples/hello-world'
NODE:1:BOARD:nucleo-f103rb: stm32
NODE:1:BOARD:nucleo-f103rb: make: Leaving directory '~/RIOT/examples/hello-world'
RESULT:NODE:0:BOARD:samr21-xpro: 0
RESULT:NODE:1:BOARD:nucleo-f103rb: 0
```

Hope you enjoyed and happy RIOTing.
