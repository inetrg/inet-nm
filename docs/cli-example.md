# Example usage of `inet-nm` CLI features using mocked devices

The following will show how to use the `inet-nm` CLI to commission, check, and execute commands on devices. This will use mocked devices so no hardware is required. This will also show how to use the `inet-nm` CLI to update the board info cache from the OS.

Note that the output is generated from an automated test and thus should be up-to-date. If you want to run the example yourself, you can run `tox -e examples`.

## Steps

0. Let's just create a `board_info` list with some features...
We can override the default args to just echo directly.
```bash
$ inet-nm-update-from-os . --board-info "echo board_1 board_2" --board-features "echo feature_common feature_${BOARD}"
Getting features_provided for board_1
Getting features_provided for board_2

Updated /tmp/pytest-of-weiss/pytest-128/test_cli_example0/board_info.json
```

1. Now we can add a board using the wizard. We can just add a mock device for now and for this example.
```bash
$ inet-nm-commission --mock-dev
Found 0 saved nodes in /tmp/pytest-of-weiss/pytest-128/test_cli_example0
Enter serial number [33046574371651769908]:
Select board name for generic_vendor
> board_1
Updated /tmp/pytest-of-weiss/pytest-128/test_cli_example0/nodes.json
```

2. Let's do it again so we have 2 `board_1` boards.
```bash
$ inet-nm-commission --mock-dev
Found 1 saved nodes in /tmp/pytest-of-weiss/pytest-128/test_cli_example0
Enter serial number [48850751729363102347]:
Select board name for generic_vendor
> board_1
Updated /tmp/pytest-of-weiss/pytest-128/test_cli_example0/nodes.json
```

3. We can also add the board with directly with the cli args.
```bash
$ inet-nm-commission --mock-dev --board board_2

Found 2 saved nodes in /tmp/pytest-of-weiss/pytest-128/test_cli_example0
Enter serial number [39660114694392531263]:
Updated /tmp/pytest-of-weiss/pytest-128/test_cli_example0/nodes.json
```

4. If we add a board that is not in our `board_info` list, we will need to confirm it is correct.
```bash
$ inet-nm-commission --mock-dev
Found 3 saved nodes in /tmp/pytest-of-weiss/pytest-128/test_cli_example0
Enter serial number [28977745412211566911]:
Select board name for generic_vendor
> board_3
Board board_3 not in board list, continue? [y/N] Y
Updated /tmp/pytest-of-weiss/pytest-128/test_cli_example0/nodes.json
```

5. If we have a device showing up on the list that should not be commissioned, we can ignore it.  This will prevent accidentally commissioning it in the future and will not be selectable by this tool.
```bash
$ inet-nm-commission --mock-dev --ignore
Found 4 saved nodes in /tmp/pytest-of-weiss/pytest-128/test_cli_example0
Enter serial number [59469734794235533397]:
Updated /tmp/pytest-of-weiss/pytest-128/test_cli_example0/nodes.json
```

6. Let's see what we have, since these are mocked devices we the will never be connected, so we should always check missing boards.
```bash
$ inet-nm-check --missing
{
  "board_1": 2,
  "board_2": 1,
  "board_3": 1
}
```

7. Maybe I only want boards with a specific feature, let's see what features we have.
```bash
$ inet-nm-check --all-nodes --show-features
[
  "feature_board_1",
  "feature_board_2",
  "feature_common"
]
```

8. Since since `board_3` was not in the board list it shouldn't have any features. If we only want boards with `feature_common` we can use the feature flags.
```bash
$ inet-nm-check --missing --feat-filter feature_common
{
  "board_1": 2,
  "board_2": 1
}
```

9. We can also use multiple feature flags, the board must have all.
```bash
$ inet-nm-check --missing --feat-filter feature_common feature_board_1
{
  "board_1": 2
}
```

10. We can also use multiple feature flags, the board must have all.
```bash
$ inet-nm-check --missing --feat-filter feature_common feature_board_1
{
  "board_1": 2
}
```

11. If we need more control over boards with features we can even select with evaluation of feature flags. This uses python syntax.
```bash
$ inet-nm-check --missing --feat-eval "feature_board_1 or feature_board_2"
{
  "board_1": 2,
  "board_2": 1
}
```

12. The checking args function the same for selecting boards to execute commands on.
```bash
$ inet-nm-exec --missing "echo $NM_IDX"
NODE:0:BOARD:board_1: 0
NODE:1:BOARD:board_1: 1
NODE:2:BOARD:board_2: 2
NODE:3:BOARD:board_3: 3
```

13. That is nice but we want only one of each board... The answer is the skip duplicates flag.
```bash
$ inet-nm-exec --missing --skip-dups "echo $NM_IDX"
NODE:0:BOARD:board_1: 0
NODE:1:BOARD:board_2: 1
NODE:2:BOARD:board_3: 2
```

14. There are many env vars exposed when running these scripts all starting with `NM_`. Let's check them on only one board.
```bash
$ inet-nm-exec "printenv | grep NM_" --missing --boards board_2
NODE:0:BOARD:board_2: NM_BOARD=board_2
NODE:0:BOARD:board_2: NM_CONFIG_DIR=/tmp/pytest-of-weiss/pytest-128/test_cli_example0
NODE:0:BOARD:board_2: NM_SERIAL=39660114694392531263
NODE:0:BOARD:board_2: NM_UID=5e1b2f6b9a3d5e956e4388a6a32de9aa
NODE:0:BOARD:board_2: NM_PORT=Unknown
NODE:0:BOARD:board_2: NM_IDX=0
```

15. Maybe we want to run a command on all boards sequentially.
We will sleep for an inverse amount of time to show the that they are being run sequentially.
```bash
$ inet-nm-exec "sleep 1" --missing --skip-dups --seq --boards board_1 board_2 board_3
```

16. There is also some blocking of boards if they are being used, let's try it out by blocking `board_1` for some time.
```bash
$ inet-nm-exec "sleep 0.5" --missing --skip-dups --boards board_1
```

17. Before the command finishes, in a different terminal, we can check to see what is available to us, notice we will be missing one of the `board_1` boards.
```bash
$ inet-nm-check --missing
{
  "board_1": 1,
  "board_2": 1,
  "board_3": 1
}
```

18. We can see what boards are being used with the only used flag.
```bash
$ inet-nm-check --missing --only-used
{
  "board_1": 1
}
```

19. We can also check all used and unused boards with the include used boards flag.
```bash
$ inet-nm-check --missing --used
{
  "board_1": 2,
  "board_2": 1,
  "board_3": 1
}
```

20. Once the process finished the used board should be freed.
```bash
$ inet-nm-check --missing --only-used
{}
```

21. If something terrible and somebody locks all the board.
```bash
$ inet-nm-exec "sleep 2" --missing
```

22. In a different terminal, we can see all our boards are used.
```bash
$ inet-nm-check --missing --only-used
{
  "board_1": 2,
  "board_2": 1,
  "board_3": 1
}
```

23. We can force them to be freed with the free command, this will not cancel ongoing processes so be careful as flashing or board output might conflict.
```bash
$ inet-nm-free
Releasing all locks
Removing lock file /tmp/inet_nm/locks/1b1766d0ba2e659aadade393718d27cc.lock
Removing lock file /tmp/inet_nm/locks/5e1b2f6b9a3d5e956e4388a6a32de9aa.lock
Removing lock file /tmp/inet_nm/locks/1c3a3933105da429ec8cec5513b09176.lock
Removing lock file /tmp/inet_nm/locks/524d1fcaf596d7a04adceabf2d0cdf49.lock
All locks released
```

24. Now we can see they are free again.
```bash
$ inet-nm-check --missing
{
  "board_1": 2,
  "board_2": 1,
  "board_3": 1
}
```

25. What happens if we now add `board_3` to the board info cache?
```bash
$ inet-nm-update-from-os . --board-info "echo board_1 board_2 board_3" --board-features "echo feature_common feature_${BOARD}"
Getting features_provided for board_1
Getting features_provided for board_2
Getting features_provided for board_3

Updated /tmp/pytest-of-weiss/pytest-128/test_cli_example0/board_info.json
```

26. Well we can updated the nodes cache in a separate step, no need to re-commission.
```bash
$ inet-nm-update-commissioned
Updated /tmp/pytest-of-weiss/pytest-128/test_cli_example0/nodes.json
```

27. Now we can see the new feature and board is available.
```bash
$ inet-nm-check --missing --feat-filter feature_board_3
{
  "board_3": 1
}
```

That was the example to show off and test most of the features.
