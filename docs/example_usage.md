# Example usage of `inet-nm` CLI features using mocked devices

The following will show how to use the `inet-nm` CLI to commission, check, and execute commands on devices. This will use mocked devices so no hardware is required. This will also show how to use the `inet-nm` CLI to update the board info cache from the OS.

Note that the output is generated from an automated test and thus should be up-to-date. If you want to run the example yourself, you can run `tox -e examples`.

## Steps

1. Let's just create a `board_info` list with some features...
We can override the default args to just echo directly.
```bash
$ inet-nm-update-from-os . --board-info "echo board_1 board_2" --board-features "echo feature_common feature_${BOARD}"
Getting features_provided for board_1
Getting features_provided for board_2

Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example0/board_info.json
```

2. Now we can add a board using the wizard. We can just add a mock device for now and for this example.
```bash
$ inet-nm-commission --mock-dev
Found 0 saved nodes in /tmp/pytest-of-weiss/pytest-23/test_cli_example0
Enter serial number [64153224548693331107]:
Select board name for generic_vendor
> board_1
Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example0/nodes.json
```

3. Let's do it again so we have 2 `board_1` boards.
```bash
$ inet-nm-commission --mock-dev
Found 1 saved nodes in /tmp/pytest-of-weiss/pytest-23/test_cli_example0
Enter serial number [06637995722385894031]:
Select board name for generic_vendor
> board_1
Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example0/nodes.json
```

4. We can also add the board with directly with the cli args.
```bash
$ inet-nm-commission --mock-dev --board board_2
Found 2 saved nodes in /tmp/pytest-of-weiss/pytest-23/test_cli_example0
Enter serial number [48012458763977615595]:
Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example0/nodes.json
```

5. If we add a board that is not in our `board_info` list, we will need to confirm it is correct.
```bash
$ inet-nm-commission --mock-dev
Found 3 saved nodes in /tmp/pytest-of-weiss/pytest-23/test_cli_example0
Enter serial number [73942106759562312165]:
Select board name for generic_vendor
> board_3
Board board_3 not in board list, continue? [y/N] Y
Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example0/nodes.json
```

6. If we have a device showing up on the list that should not be commissioned, we can ignore it.  This will prevent accidentally commissioning it in the future and will not be selectable by this tool.
```bash
$ inet-nm-commission --mock-dev --ignore
Found 4 saved nodes in /tmp/pytest-of-weiss/pytest-23/test_cli_example0
Enter serial number [21502814251526666348]:
Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example0/nodes.json
```

7. Let's see what we have, since these are mocked devices we the will never be connected, so we should always check missing boards.
```bash
$ inet-nm-check --missing
{
  "board_1": 2,
  "board_2": 1,
  "board_3": 1
}
```

8. Maybe I only want boards with a specific feature, let's see what features we have.
```bash
$ inet-nm-check --all-nodes --show-features
[
  "feature_board_1",
  "feature_board_2",
  "feature_common"
]
```

9. Since since `board_3` was not in the board list it shouldn't have any features. If we only want boards with `feature_common` we can use the feature flags.
```bash
$ inet-nm-check --missing --feat-filter feature_common
{
  "board_1": 2,
  "board_2": 1
}
```

10. We can also use multiple feature flags, the board must have all.
```bash
$ inet-nm-check --missing --feat-filter feature_common feature_board_1
{
  "board_1": 2
}
```

11. We can also use multiple feature flags, the board must have all.
```bash
$ inet-nm-check --missing --feat-filter feature_common feature_board_1
{
  "board_1": 2
}
```

12. If we need more control over boards with features we can even select with evaluation of feature flags. This uses python syntax.
```bash
$ inet-nm-check --missing --feat-eval "feature_board_1 or feature_board_2"
{
  "board_1": 2,
  "board_2": 1
}
```

13. The checking args function the same for selecting boards to execute commands on.
```bash
$ inet-nm-exec --missing "echo $NM_IDX"
NODE:0:BOARD:board_1: 0
NODE:1:BOARD:board_1: 1
NODE:2:BOARD:board_2: 2
NODE:3:BOARD:board_3: 3
RESULT:NODE:0:BOARD:board_1: 0
RESULT:NODE:1:BOARD:board_1: 0
RESULT:NODE:2:BOARD:board_2: 0
RESULT:NODE:3:BOARD:board_3: 0
```

14. That is nice but we want only one of each board... The answer is the skip duplicates flag.
```bash
$ inet-nm-exec --missing --skip-dups "echo $NM_IDX"
NODE:0:BOARD:board_1: 0
NODE:1:BOARD:board_2: 1
NODE:2:BOARD:board_3: 2
RESULT:NODE:0:BOARD:board_1: 0
RESULT:NODE:1:BOARD:board_2: 0
RESULT:NODE:2:BOARD:board_3: 0
```

15. There are many env vars exposed when running these scripts all starting with `NM_`. Let's check them on only one board.
```bash
$ inet-nm-exec "printenv | grep NM_" --missing --boards board_2
NODE:0:BOARD:board_2: NM_BOARD=board_2
NODE:0:BOARD:board_2: NM_CONFIG_DIR=/tmp/pytest-of-weiss/pytest-23/test_cli_example0
NODE:0:BOARD:board_2: NM_SERIAL=48012458763977615595
NODE:0:BOARD:board_2: NM_UID=c9dca8b38d9b5bac5602c77f0e5f9efe
NODE:0:BOARD:board_2: NM_PORT=Unknown
NODE:0:BOARD:board_2: NM_IDX=0
RESULT:NODE:0:BOARD:board_2: 0
```

16. Maybe we want to run a command on all boards sequentially.
We will sleep for an inverse amount of time to show the that they are being run sequentially.
```bash
$ inet-nm-exec "sleep 1" --missing --skip-dups --seq --boards board_1 board_2 board_3
RESULT:NODE:0:BOARD:board_1: 0
RESULT:NODE:1:BOARD:board_2: 0
RESULT:NODE:2:BOARD:board_3: 0
```

17. There is also some blocking of boards if they are being used, let's try it out by blocking `board_1` for some time.
```bash
$ inet-nm-exec "sleep 1" --missing --skip-dups --boards board_1
```

18. We can ignore other people and simply force the selected boards to execute something... You would not be a good citizen but it may be useful just to replicate an environment.
```bash
$ inet-nm-exec "echo foo" --missing --force --only-used
NODE:0:BOARD:board_1: foo
RESULT:NODE:0:BOARD:board_1: 0
```

19. Let's block the board_1 again...
```bash
$ inet-nm-exec "sleep 1" --missing --skip-dups --boards board_1
```

20. Before the command finishes, in a different terminal, we can check to see what is available to us, notice we will be missing one of the `board_1` boards.
```bash
$ inet-nm-check --missing
{
  "board_1": 1,
  "board_2": 1,
  "board_3": 1
}
```

21. We can see what boards are being used with the only used flag.
```bash
$ inet-nm-check --missing --only-used
{
  "board_1": 1
}
```

22. We can also check all used and unused boards with the include used boards flag.
```bash
$ inet-nm-check --missing --used
{
  "board_1": 2,
  "board_2": 1,
  "board_3": 1
}
```

23. Once the process finished the used board should be freed.
```bash
$ inet-nm-check --missing --only-used
{}
```

24. If something terrible and somebody locks all the board.
```bash
$ inet-nm-exec "sleep 2" --missing
```

25. In a different terminal, we can see all our boards are used.
```bash
$ inet-nm-check --missing --only-used
{
  "board_1": 2,
  "board_2": 1,
  "board_3": 1
}
```

26. We can force them to be freed with the free command, this will not cancel ongoing processes so be careful as flashing or board output might conflict.
```bash
$ inet-nm-free
Releasing all locks
Removing lock file /tmp/inet_nm/locks/c9dca8b38d9b5bac5602c77f0e5f9efe.lock
Removing lock file /tmp/inet_nm/locks/505d0bcd65827e012171eef1f16aa522.lock
Removing lock file /tmp/inet_nm/locks/28f96a436cfd9a54fc534e53bda807aa.lock
Removing lock file /tmp/inet_nm/locks/8b211c1995e9c8ab164ea85d0f0c9209.lock
All locks released
```

27. Now we can see they are free again.
```bash
$ inet-nm-check --missing
{
  "board_1": 2,
  "board_2": 1,
  "board_3": 1
}
```

28. What happens if we now add `board_3` to the board info cache?
```bash
$ inet-nm-update-from-os . --board-info "echo board_1 board_2 board_3" --board-features "echo feature_common feature_${BOARD}"
Getting features_provided for board_1
Getting features_provided for board_2
Getting features_provided for board_3

Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example0/board_info.json
```

29. Now we can see the new feature and board is available.
```bash
$ inet-nm-check --missing --feat-filter feature_board_3
{
  "board_3": 1
}
```

30. The default environment is namespaced with `NM_` but how about being able to setup a custom environment... Well, we can do that too! Let's start with just adding an env variable to all node environments. This will apply to all commissioned nodes and any future commissioned nodes. Take special note of the escape characters and brackets. Just something like `\$VAR` will not work, `\${VAR}` is needed.
```bash
$ inet-nm-export MY_CUSTOM_BOARD_ENV_VAR \${NM_BOARD} --apply-to-shared
Added MY_CUSTOM_BOARD_ENV_VAR=${NM_BOARD} to shared env vars
Written to /tmp/pytest-of-weiss/pytest-23/test_cli_example0/env.json
```

31. Apply a pattern to select only some boards or features.
```bash
$ inet-nm-export MY_CUSTOM_SETTING 1 --apply-pattern --missing --feat-filter feature_board_3
Added patterns: {'key': 'MY_CUSTOM_SETTING', 'val': '1', 'boards': None, 'feat_filter': ['feature_board_3'], 'feat_eval': None}
Written to /tmp/pytest-of-weiss/pytest-23/test_cli_example0/env.json
```

32. The pattern has higher priority than the shared env vars. Let's overwrite the shared variable for board 2
```bash
$ inet-nm-export MY_CUSTOM_BOARD_ENV_VAR board_2 --apply-pattern --missing --boards board_2
Added patterns: {'key': 'MY_CUSTOM_BOARD_ENV_VAR', 'val': 'board_2', 'boards': ['board_2'], 'feat_filter': None, 'feat_eval': None}
Written to /tmp/pytest-of-weiss/pytest-23/test_cli_example0/env.json
```

33. Finally we can apply env vars to specific nodes. This is based on the UID, therefor commissioning new nodes will not contain these env vars. This has the highest priority.
```bash
$ inet-nm-export MY_CUSTOM_NODE_HAS_SPECIAL_HARDWARE_FLAG 1 --missing --boards board_1 --skip-dups
Added MY_CUSTOM_NODE_HAS_SPECIAL_HARDWARE_FLAG=1 to env vars for nodes {'505d0bcd65827e012171eef1f16aa522'}
Written to /tmp/pytest-of-weiss/pytest-23/test_cli_example0/env.json
```

34. Now we can check each environment.
```bash
$ inet-nm-exec "printenv | grep MY_CUSTOM" --missing
NODE:0:BOARD:board_1: MY_CUSTOM_BOARD_ENV_VAR=${NM_BOARD}
NODE:0:BOARD:board_1: MY_CUSTOM_NODE_HAS_SPECIAL_HARDWARE_FLAG=1
NODE:1:BOARD:board_1: MY_CUSTOM_BOARD_ENV_VAR=${NM_BOARD}
NODE:2:BOARD:board_2: MY_CUSTOM_BOARD_ENV_VAR=board_2
NODE:3:BOARD:board_3: MY_CUSTOM_SETTING=1
NODE:3:BOARD:board_3: MY_CUSTOM_BOARD_ENV_VAR=${NM_BOARD}
RESULT:NODE:0:BOARD:board_1: 0
RESULT:NODE:1:BOARD:board_1: 0
RESULT:NODE:2:BOARD:board_2: 0
RESULT:NODE:3:BOARD:board_3: 0
```

35. Let's say I want to check the state of my boards. I can see a nice table of what is available, used, and missing.
```bash
$ inet-nm-inventory
Updated uid_states written to /tmp/inet-nm-uid-states-ba467f0e4334ba8732fc85592d2b7a02.json
Updated changes written to /tmp/inet-nm-changes-ba467f0e4334ba8732fc85592d2b7a02.json
-----------------------------------------------------------
| Board   | Available | Used      | Missing   | Total     |
-----------------------------------------------------------
| board_1 |         0 |         0 |+        2 |         2 |
| board_2 |         0 |         0 |+        1 |         1 |
| board_3 |         0 |         0 |+        1 |         1 |
-----------------------------------------------------------
|         |         0 |         0 |         4 |         4 |
-----------------------------------------------------------
```

36. We can also get that in a machine readable way.
```bash
$ inet-nm-inventory --json
[
  {
    "available": 0,
    "available_changes": 0,
    "board": "board_1",
    "missing": 2,
    "missing_changes": 2,
    "total": 2,
    "used": 0,
    "used_changes": 0
  },
  {
    "available": 0,
    "available_changes": 0,
    "board": "board_2",
    "missing": 1,
    "missing_changes": 1,
    "total": 1,
    "used": 0,
    "used_changes": 0
  },
  {
    "available": 0,
    "available_changes": 0,
    "board": "board_3",
    "missing": 1,
    "missing_changes": 1,
    "total": 1,
    "used": 0,
    "used_changes": 0
  }
]
```

37. Boy, we are adding features and boards all the time, let's see some exec json filtering now.
```bash
$ inet-nm-exec --missing --json-filter "cat /tmp/pytest-of-weiss/pytest-23/test_cli_example0/example.json"
[
  {
    "board": "board_1",
    "data": [
      {
        "a": 1,
        "b": 2
      }
    ],
    "idx": 0,
    "result": 0,
    "stdout": "\nlog info\n{\n    \"a\": 1,\n    \"b\": 2\n} more generic text\n            ",
    "uid": "505d0bcd65827e012171eef1f16aa522"
  },
  {
    "board": "board_1",
    "data": [
      {
        "a": 1,
        "b": 2
      }
    ],
    "idx": 1,
    "result": 0,
    "stdout": "\nlog info\n{\n    \"a\": 1,\n    \"b\": 2\n} more generic text\n            ",
    "uid": "28f96a436cfd9a54fc534e53bda807aa"
  },
  {
    "board": "board_2",
    "data": [
      {
        "a": 1,
        "b": 2
      }
    ],
    "idx": 2,
    "result": 0,
    "stdout": "\nlog info\n{\n    \"a\": 1,\n    \"b\": 2\n} more generic text\n            ",
    "uid": "c9dca8b38d9b5bac5602c77f0e5f9efe"
  },
  {
    "board": "board_3",
    "data": [
      {
        "a": 1,
        "b": 2
      }
    ],
    "idx": 3,
    "result": 0,
    "stdout": "\nlog info\n{\n    \"a\": 1,\n    \"b\": 2\n} more generic text\n            ",
    "uid": "8b211c1995e9c8ab164ea85d0f0c9209"
  }
]
```

38. We can also select nodes based on UID
```bash
$ inet-nm-check --missing --uids 505d0bcd65827e012171eef1f16aa522
{
  "board_1": 1
}
```

39. We can also add `user_board_info.json`. that will not get overridden when updating... I added it behind the scenes.
```bash
$ inet-nm-exec "cat /tmp/pytest-of-weiss/pytest-23/test_cli_example0/user_board_info.json" --missing --boards board_3
NODE:0:BOARD:board_3: {"board_1": ["user_feature"]}
RESULT:NODE:0:BOARD:board_3: 0
```

40. Now we can see the new feature.
```bash
$ inet-nm-check --feat-filter user_feature --missing
{
  "board_1": 2
}
```

41. We can also add features to specific nodes with `user_node_info.json`.
```bash
$ inet-nm-exec "cat /tmp/pytest-of-weiss/pytest-23/test_cli_example0/user_node_info.json" --missing --boards board_3
NODE:0:BOARD:board_3: {"505d0bcd65827e012171eef1f16aa522": ["user_node_feature"]}
RESULT:NODE:0:BOARD:board_3: 0
```

42. This can be directly checked.
```bash
$ inet-nm-check --feat-filter user_node_feature --missing
{
  "board_1": 1
}
```

43. Let's decommission boards, say the have all broken.
```bash
$ inet-nm-decommission --all --missing
Updated /tmp/pytest-of-weiss/pytest-23/test_cli_example0/nodes.json
```

44. Now we can see nothing is there
```bash
$ inet-nm-check --missing
{}
```

That was the example to show off and test most of the features.
