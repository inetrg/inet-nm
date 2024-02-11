# Example usage of `inet-nm` location features

The following will add some fake boards in order to show the features of the `inet-nm` location commands. With the fake boards will need to commission some and then we can start setting the locations. We can see how info is stored and also a nice graph.

## Steps

1. We would like to display the following command but need some setup.
```bash
$ inet-nm-set-location --help
usage: inet-nm-set-location [-h] [-c CONFIG] [-u UID] [-l]

Commission USB boards

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to the config dir, defaults to NM_CONFIG_DIR or ~/.config/inet_nm if NM_CONFIG_DIR is not set
  -u UID, --uid UID     UID of the board to locate
  -l, --locate          Use usb hub location
```

```bash
$ inet-nm-show-location --help
usage: inet-nm-show-location [-h] [-c CONFIG] [-f FEAT_FILTER [FEAT_FILTER ...]] [-e FEAT_EVAL] [-b BOARDS [BOARDS ...]] [-d UIDS [UIDS ...]] [-l] [-g] [-u]

Commission USB boards

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to the config dir, defaults to NM_CONFIG_DIR or ~/.config/inet_nm if NM_CONFIG_DIR is not set
  -f FEAT_FILTER [FEAT_FILTER ...], --feat-filter FEAT_FILTER [FEAT_FILTER ...]
                        Filter all boards that don't provide these features
  -e FEAT_EVAL, --feat-eval FEAT_EVAL
                        Evaluate features with this function
  -b BOARDS [BOARDS ...], --boards BOARDS [BOARDS ...]
                        Use only the list of boards that match these names
  -d UIDS [UIDS ...], --uids UIDS [UIDS ...]
                        Use only the list of boards that match these UIDs
  -l, --location-only   Show only the location names
  -g, --graph           If location names follow proper convention, then show a graph
  -u, --unassigned      Include nodes that have no matching location
```

2. First let's fake plug in a board.
```bash
$ inet-nm-fake-usb --id board_1
Please set the INET_NM_FAKE_USB_PATH env var... somewhere.
```

3. OK... all set, let's see this now!
```bash
$ inet-nm-fake-usb --id board_1
Added fake device with ID board_1.
Saved fake devices to /tmp/pytest-of-weiss/pytest-23/test_cli_example_locate0/fakes.json.
```

4. Let commission it.
```bash
$ inet-nm-commission
Found 0 saved nodes in /tmp/pytest-of-weiss/pytest-23/test_cli_example_locate0
Select board name for QinHeng Electronics USB Serial
> board_1
Board board_1 not in board list, continue? [y/N] y
Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example_locate0/nodes.json
```

5. And another...
```bash
$ inet-nm-fake-usb --id board_2
Added fake device with ID board_2.
Saved fake devices to /tmp/pytest-of-weiss/pytest-23/test_cli_example_locate0/fakes.json.
```

```bash
$ inet-nm-commission
Found 1 saved nodes in /tmp/pytest-of-weiss/pytest-23/test_cli_example_locate0
Select board name for QinHeng Electronics USB Serial
> board_2
Board board_2 not in board list, continue? [y/N] y
Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example_locate0/nodes.json
```

6. And one more for good luck, we don't need id for fake boards really.
```bash
$ inet-nm-fake-usb
Added fake device with ID 2.
Saved fake devices to /tmp/pytest-of-weiss/pytest-23/test_cli_example_locate0/fakes.json.
```

```bash
$ inet-nm-commission
Found 2 saved nodes in /tmp/pytest-of-weiss/pytest-23/test_cli_example_locate0
Select board name for QinHeng Electronics USB Serial
> board_3
Board board_3 not in board list, continue? [y/N] y
Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example_locate0/nodes.json
```

7. Now we are ready! Let's set a location.
```bash
$ inet-nm-set-location
Select the node
1. 39324cabfa3ffa9a8f7de0fa1b295c57 board_1
2. cf56a4dba757a6860edbbf73d699fbc8 board_2
3. b271fae3c662ae5c06b99dd8b7979663 board_3
> 1
Enter a name for the location [1.1.1]:
1.1.1 mapped to pci-0000:00:00.0-usb-0:0
Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example_locate0/location.json
```

8. Hmmm, it seems there is a recommendation here... A little hint, it is part of the inet-mbh project which is a is a modular system that holds up to 4 boards. Thus, a recommended naming scheme is `<vertical_position*4>.<horazontal_position>.<vertical_position>` (e.g. 1.1.1). If you follow this convention, then cool things happen as well as some recommendations.
```bash
$ inet-nm-set-location
Select the node
1. cf56a4dba757a6860edbbf73d699fbc8 board_2
2. b271fae3c662ae5c06b99dd8b7979663 board_3
> 1
Enter a name for the location [1.1.2]: 2.3.4
2.3.4 mapped to pci-0000:00:00.0-usb-0:1
Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example_locate0/location.json
```

9. Of course we don't need to follow anything.
```bash
$ inet-nm-set-location
Enter a name for the location [2.4.1]: in the garbage
in the garbage mapped to pci-0000:00:00.0-usb-0:2
Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example_locate0/location.json
```

10. Let's see what we have.
```bash
$ inet-nm-show-location
[
  {
    "board": "board_1",
    "location": "1.1.1",
    "uid": "39324cabfa3ffa9a8f7de0fa1b295c57"
  },
  {
    "board": "board_2",
    "location": "2.3.4",
    "uid": "cf56a4dba757a6860edbbf73d699fbc8"
  },
  {
    "board": "board_3",
    "location": "in the garbage",
    "uid": "b271fae3c662ae5c06b99dd8b7979663"
  }
]
```

11. Hard to read, eh? So let's get visual. Notice the postions
```bash
$ inet-nm-show-location --graph
┌─┬─┬─┐
│ │ │x│
│ │ │ │
│ │ │ │
│ │ │ │
┼─┼─┼─┼
│ │ │ │
│ │ │ │
│ │ │ │
│x│ │ │
└─┴─┴─┘
in the garbage
```

The suggested workflow is to use just one board and map all the locations, removing and moving each slot. Then add all the boards in after. I hope you enjoyed and learned a little something.
