[![CI Tests](https://github.com/inetrg/inet-nm/actions/workflows/ci.yml/badge.svg)](https://github.com/inetrg/inet-nm/actions/workflows/ci.yml)
[![ReadTheDocs](https://readthedocs.org/projects/inet-nm/badge/?version=latest)](https://inet-nm.readthedocs.io/en/stable/)
[![PyPI-Server](https://img.shields.io/pypi/v/inet-nm.svg)](https://pypi.org/project/inet-nm/)
[![Monthly Downloads](https://pepy.tech/badge/inet-nm/month)](https://pepy.tech/project/inet-nm)

# inet_nm - INET Node Manager

INET Node Manager (inet_nm) is a comprehensive suite of command-line
tools designed to streamline the management of multiple USB-based
embedded development kits (also known as nodes or boards). This tool
addresses a common challenge faced by many teams - keeping track of
multiple hardware variants and efficiently running tests across these
platforms.

In the context of managing a large variety of boards such as Nucleo
boards, SAM XPro, ESPs and more, inet_nm comes into play by providing
functionalities like:

* Tracking currently plugged-in boards and previously connected boards
* Running scripts on individual boards with lockfiles to prevent
  conflicts
* Maintaining board information and managing new boards with minimal
  overhead
* Offering a tmux session for interactive control and automatically
  releasing the node on session close
* Identifying boards by their features

All these features are designed to make managing numerous development
boards more manageable and efficient, particularly for teams maintaining
large open-source projects like RIOT OS.

## Installation

### As a developer or single user

You can install inet_nm via pip or pipx (recommended to use a venv):

```bash
pip install inet-nm
```

### On a shared computer for CI

If you have one computer where many different users may want to access the
boards it may be better to setup for all users.

First change the config dir to a shared path (by default we select `/etc/environment`):
```
sudo sed -i '/NM_CONFIG_DIR/d' /etc/environment && echo 'NM_CONFIG_DIR=/etc/inet-nm' | sudo tee -a /etc/environment
```

Then install with pip system-wide
```
sudo pip install inet-nm
```

Now all users should be able to access the cli functions. Note that `sudo` will
be needed to make any changes such as commissioning boards or updating board
names.

## Usage

Below is the usage for each of the command-line applications included in inet_nm:

### inet-nm-update-from-os

This command is used to cache a list of boards and features. The
default commands are compatible with [RIOT OS](https://www.riot-os.org/) but
can be overridden for other systems.

```
$ inet-nm-update-from-os -h
usage: inet-nm-update-from-os [-h] [-c CONFIG] [-i BOARD_INFO] [-f BOARD_FEATURES] [-n BOARD_ENV_VAR] basedir

Cache a list of boards

positional arguments:
  basedir               Path to the board path directory

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to the config dir
  -i BOARD_INFO, --board-info BOARD_INFO
                        Command to get board info, defaults to 'make info-boards'
  -f BOARD_FEATURES, --board-features BOARD_FEATURES
                        Command to get board features, defaults to 'make info-features-provided'
  -n BOARD_ENV_VAR, --board-env-var BOARD_ENV_VAR
                        The env var to indicate the board name for features provided, defaults to 'BOARD'
```

### inet-nm-update-commissioned

This command is used to update commissioned features, usually after
`inet-nm-update-from-os` is called.

```
$ inet-nm-update-commissioned -h
usage: inet-nm-update-commissioned [-h] [-c CONFIG]
```

### inet-nm-commission

This is an interactive prompt to new commission USB boards.

```
$ inet-nm-commission -h
usage: inet-nm-commission [-h] [-c CONFIG] [-b BOARD] [-n]
```

### inet-nm-check

This command is used to check the list of boards given some conditions.

```
$ inet-nm-check -h
usage: inet-nm-check [-h] [-c CONFIG] [-f FEAT_FILTER [FEAT_FILTER ...]] [-a] [-m] [-e FEAT_EVAL] [-u] [-s] [--show-features]
```

### Environment Variables

When executing a script or running interactively,
[env vars are available](src/inet_nm/data_types.py):

```
NM_IDX: Index of the node.
NM_UID: Unique ID of the node.
NM_SERIAL: Serial number of the node.
NM_BOARD: Board of the node.
NM_PORT: Port of the node.
```

There is also an environment variable to specify the default configuration
directory.
```
NM_CONFIG_DIR
```

### inet-nm-exec

This command is used to send execute a command or script. It will block the nodes
until it is finished.

```
$ inet-nm-exec -h
usage: inet-nm-exec [-h] [-t TIMEOUT] [-c CONFIG] [-f FEAT_FILTER [FEAT_FILTER ...]] [-a] [-m] [-e FEAT_EVAL] [-u] [-s] cmd
```

### inet-nm-tmux

This command is used to manage nodes in a tmux session. It will block the nodes
until the session is over.

```
inet-nm-tmux -h
usage: inet-nm-tmux [-h] [-w] [-t TIMEOUT] [-x CMD] [-c CONFIG] [-f FEAT_FILTER [FEAT_FILTER ...]] [-a] [-m] [-e FEAT_EVAL] [-u] [-s]
```


### inet-nm-from-uid

This command finds the tty of a node given the UID. This is useful if a node
gets reconnected during an interactive session.

```
$ inet-nm-tty-from-uid -h
usage: inet-nm-tty-from-uid [-h] [-c CONFIG] uid
```

## Example Workflow

Up-to-date examples are available at [`docs/cli-example.md`](docs/cli-example.md).

1. First update the boards list in the cache to allow for autocomplete and
features.
```
$ inet-nm-update-from-os RIOT/examples/hello-world/
Getting features_provided for acd52832
Getting features_provided for adafruit-clue
...
Getting features_provided for z1
Getting features_provided for zigduino

Updated /home/weiss/.config/inet_nm/board_info.json
```

2. Then plug in a new board, or many new boards and commission them.
Note that you can use autocomplete to help select the board name.
```
$ inet-nm-commission
Found 3 saved nodes in ~/.config/inet_nm
[?] Select the node: /dev/ttyACM1 Atmel Corp. Xplained Pro board debugger and programmer ATML2769041800000967
 > /dev/ttyACM1 Atmel Corp. Xplained Pro board debugger and programmer ATML2769041800000967
   /dev/ttyACM0 STMicroelectronics ST-LINK/V2.1 066DFF545150898367074730

Select board name for Atmel Corp. Xplained Pro board debugger and programmer
> saml1
saml10-xpro        saml11-xpro
> saml11-xpro
Updated /home/user/.config/inet_nm/nodes.json
```

3. Check to see what unused, connected board are available.

```
$ inet-nm-check
{
  "b-l072z-lrwan1": 2,
  "esp32-wroom-32": 1,
  "frdm-kw41z": 1,
  "nucleo-l452re": 1,
  "remote-revb": 1,
  "saml11-xpro": 1
}

```

4. Prepare a board selection to use only one board of each type that have a given feature.
```
$ inet-nm-check -f bootloader_stm32 -s
{
  "b-l072z-lrwan1": 1,
  "nucleo-l452re": 1
}
```

5. Interactively open a terminal to those boards.
Note, tmux can enable synced panes with `:setw synchronize-panes`.


```
$ inet-nm-tmux -f bootloader_stm32 -s
```
```
$ printenv | grep NM_
NM_BOARD=nucleo-l452re
NM_SERIAL=066AFF515055657867195125
NM_UID=328c4b667b4689b077436c385fc55a66
NM_PORT=/dev/ttyACM0
NM_IDX=0
───────────────────────────────────────
$ printenv | grep NM_
NM_BOARD=b-l072z-lrwan1
NM_SERIAL=066CFF495351677867143305
NM_UID=d1b3355a0e68fbf042a033ff3f222334
NM_PORT=/dev/ttyACM3
NM_IDX=1

```

6. While the terminal is still open, run another script.
This will not use the boards that have been used for interactive session.
```
$ inet-nm-exec "echo NM_BOARD=\$NM_BOARD"
NODE:0:BOARD:frdm-kw41z: NM_BOARD=frdm-kw41z
NODE:1:BOARD:saml11-xpro: NM_BOARD=saml11-xpro
NODE:2:BOARD:remote-revb: NM_BOARD=remote-revb
NODE:3:BOARD:esp32-wroom-32: NM_BOARD=esp32-wroom-32
NODE:4:BOARD:b-l072z-lrwan1: NM_BOARD=b-l072z-lrwan1
```

## License

This project is licensed under the terms of the MIT license. See the LICENSE file.

---
For any questions or contributions, please refer to the issues tab or the contributing guide.
