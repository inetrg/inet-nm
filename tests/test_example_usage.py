import json
import os
import sys
import time

import pexpect
import pytest
from flaky import flaky


class CliTester:
    DEFAULT_START_WAIT_TIME = 0.2
    DEFAULT_PROCESS_TIMEOUT = 2
    title = None
    footer = None
    description = None

    def __init__(self, cfg_dir):
        os.environ["NM_CONFIG_DIR"] = str(cfg_dir)
        os.environ["COVERAGE_PROCESS_START"] = ".coveragerc"
        self._step_results = []
        self._async_procs = []

    @staticmethod
    def _cmd_to_coverage(cmd):
        cmd = cmd.replace("inet-nm-", "inet_nm.cli_")
        cmd = cmd.replace("-", "_")
        return f"coverage run -m {cmd}"

    def run_step(
        self,
        cmd,
        args=None,
        sendlines=None,
        description=None,
        timeout=None,
        skip_read=False,
    ):
        cov_cmd = CliTester._cmd_to_coverage(cmd)
        cov_cmd = f"{cov_cmd} {' '.join(args or [])}"
        child = pexpect.spawn(
            command=cov_cmd, timeout=timeout or self.DEFAULT_PROCESS_TIMEOUT
        )
        time.sleep(self.DEFAULT_START_WAIT_TIME)
        for line in sendlines or []:
            child.sendline(line)
        if skip_read:
            self._async_procs.append(child)
            self._step_results.append(
                (description, f"{cmd} {' '.join(args or [])}", "")
            )
            return ""
        output = child.read().decode().replace("\r\n", "\n")
        self._step_results.append(
            (description, f"{cmd} {' '.join(args or [])}", output)
        )
        return output

    def format_md(self):
        out = ""
        if self.title:
            out += f"# {self.title}\n\n"
        if self.description:
            out += f"{self.description}\n\n"
        out += "## Steps\n\n"
        for idx, (desc, cmd, output) in enumerate(self._step_results):
            out += f"{idx}. {desc}\n"
            out += f"```bash\n$ {cmd}\n"
            out += f"{output}```\n\n"
        if self.footer:
            out += f"{self.footer}\n"
        return out


try:
    import inquirer
except ImportError:
    inquirer = None


@flaky(max_runs=1)
@pytest.mark.skipif(inquirer is not None, reason="inquirer should not be installed")
@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
@pytest.mark.slow
def test_cli_example(tmpdir, cli_readme_mock):
    ct = CliTester(tmpdir)
    ct.title = "Example usage of `inet-nm` CLI features using mocked devices"
    ct.description = "The following will show how to use the `inet-nm` CLI to "
    ct.description += "commission, check, and execute commands on devices. "
    ct.description += "This will use mocked devices so no hardware is required. "
    ct.description += "This will also show how to use the `inet-nm` CLI to "
    ct.description += "update the board info cache from the OS.\n\n"
    ct.description += "Note that the output is generated from an automated test "
    ct.description += "and thus should be up-to-date. If you want to run the "
    ct.description += "example yourself, you can run `tox -e examples`."
    ct.footer = "That was the example to show off and test most of the features."

    ct.run_step(
        description="Let's just create a `board_info` list with some features...\n"
        "We can override the default args to just echo directly.",
        cmd="inet-nm-update-from-os",
        args=[
            ".",
            "--board-info",
            '"echo board_1 board_2"',
            "--board-features",
            '"echo feature_common feature_${BOARD}"',
        ],
    )

    ct.run_step(
        description="Now we can add a board using the wizard. We can just add a "
        "mock device for now and for this example.",
        cmd="inet-nm-commission",
        args=["--mock-dev"],
        sendlines=[
            "",
            "board_1",
        ],
    )
    ct.run_step(
        description="Let's do it again so we have 2 `board_1` boards.",
        cmd="inet-nm-commission",
        args=["--mock-dev"],
        sendlines=[
            "",
            "board_1",
        ],
    )
    ct.run_step(
        description="We can also add the board with directly with the cli args.",
        cmd="inet-nm-commission",
        args=["--mock-dev", "--board", "board_2"],
        sendlines=[""],
    )
    ct.run_step(
        description="If we add a board that is not in our `board_info` list, "
        "we will need to confirm it is correct.",
        cmd="inet-nm-commission",
        args=["--mock-dev"],
        sendlines=[
            "",
            "board_3",
            "Y",
        ],
    )

    ct.run_step(
        description="If we have a device showing up on the list that should not "
        "be commissioned, we can ignore it.  This will prevent "
        "accidentally commissioning it in the future and will not "
        "be selectable by this tool.",
        cmd="inet-nm-commission",
        args=["--mock-dev", "--ignore"],
        sendlines=[
            "",
        ],
    )

    ret = ct.run_step(
        description="Let's see what we have, since these are mocked devices we "
        "the will never be connected, so we should always check "
        "missing boards.",
        cmd="inet-nm-check",
        args=["--missing"],
    )
    assert "board_1" in ret
    assert "board_2" in ret
    assert "board_3" in ret

    ret = ct.run_step(
        description="Maybe I only want boards with a specific feature, "
        "let's see what features we have.",
        cmd="inet-nm-check",
        args=["--all-nodes", "--show-features"],
    )
    assert "feature_board_1" in ret
    assert "feature_board_2" in ret
    assert "feature_common" in ret

    ret = ct.run_step(
        description="Since since `board_3` was not in the board list it "
        "shouldn't have any features. If we only want boards with "
        "`feature_common` we can use the feature flags.",
        cmd="inet-nm-check",
        args=["--missing", "--feat-filter", "feature_common"],
    )
    assert "board_1" in ret
    assert "board_2" in ret
    assert "board_3" not in ret

    ret = ct.run_step(
        description="We can also use multiple feature flags, the board must have all.",
        cmd="inet-nm-check",
        args=["--missing", "--feat-filter", "feature_common", "feature_board_1"],
    )
    assert "board_1" in ret
    assert "board_2" not in ret
    assert "board_3" not in ret

    ret = ct.run_step(
        description="We can also use multiple feature flags, the board must have all.",
        cmd="inet-nm-check",
        args=["--missing", "--feat-filter", "feature_common", "feature_board_1"],
    )

    ret = ct.run_step(
        description="If we need more control over boards with features we can "
        "even select with evaluation of feature flags. "
        "This uses python syntax.",
        cmd="inet-nm-check",
        args=["--missing", "--feat-eval", '"feature_board_1 or feature_board_2"'],
    )
    assert "board_1" in ret
    assert "board_2" in ret
    assert "board_3" not in ret

    ret = ct.run_step(
        description="The checking args function the same for selecting boards "
        "to execute commands on.",
        cmd="inet-nm-exec",
        args=["--missing", '"echo $NM_IDX"'],
    )
    assert "board_3: 3" in ret

    ret = ct.run_step(
        description="That is nice but we want only one of each board... "
        "The answer is the skip duplicates flag.",
        cmd="inet-nm-exec",
        args=["--missing", "--skip-dups", '"echo $NM_IDX"'],
    )
    assert "board_3: 2" in ret

    ret = ct.run_step(
        description="There are many env vars exposed when running these scripts "
        "all starting with `NM_`. Let's check them on only one board.",
        cmd="inet-nm-exec",
        args=['"printenv | grep NM_"', "--missing", "--boards", "board_2"],
    )
    assert "NM_BOARD=board_2" in ret

    start_time = time.time()
    ret = ct.run_step(
        description="Maybe we want to run a command on all boards sequentially.\n"
        "We will sleep for an inverse amount of time to show the that they are "
        "being run sequentially.",
        cmd="inet-nm-exec",
        args=[
            '"sleep 1"',
            "--missing",
            "--skip-dups",
            "--seq",
            "--boards",
            "board_1",
            "board_2",
            "board_3",
        ],
        timeout=5,
    )
    end_time = time.time()
    assert end_time - start_time >= 3

    ret = ct.run_step(
        description="There is also some blocking of boards if they are being used, "
        "let's try it out by blocking `board_1` for some time.",
        cmd="inet-nm-exec",
        args=['"sleep 1"', "--missing", "--skip-dups", "--boards", "board_1"],
        timeout=2,
        skip_read=True,
    )

    ret = ct.run_step(
        description="We can ignore other people and simply force the selected "
        "boards to execute something... You would not be a good citizen but "
        "it may be useful just to replicate an environment.",
        cmd="inet-nm-exec",
        args=['"echo foo"', "--missing", "--force", "--only-used"],
    )
    assert "foo" in ret
    # Wait until async process finishes
    time.sleep(1)

    ret = ct.run_step(
        description="Let's block the board_1 again...",
        cmd="inet-nm-exec",
        args=['"sleep 1"', "--missing", "--skip-dups", "--boards", "board_1"],
        timeout=2,
        skip_read=True,
    )
    ret = ct.run_step(
        description="Before the command finishes, in a different terminal, we "
        "can check to see what is available to us, notice we will "
        "be missing one of the `board_1` boards.",
        cmd="inet-nm-check",
        args=["--missing"],
    )
    assert '"board_1": 1' in ret

    ret = ct.run_step(
        description="We can see what boards are being used with the only used flag.",
        cmd="inet-nm-check",
        args=["--missing", "--only-used"],
    )
    assert "board_1" in ret
    assert "board_2" not in ret
    assert "board_3" not in ret

    ret = ct.run_step(
        description="We can also check all used and unused boards with the "
        "include used boards flag.",
        cmd="inet-nm-check",
        args=["--missing", "--used "],
    )
    assert '"board_1": 2' in ret
    assert "board_2" in ret
    assert "board_3" in ret

    # Wait until async process finishes
    time.sleep(1)

    ret = ct.run_step(
        description="Once the process finished the used board should be freed.",
        cmd="inet-nm-check",
        args=["--missing", "--only-used"],
    )
    assert "board_1" not in ret

    ret = ct.run_step(
        description="If something terrible and somebody locks all the board.",
        cmd="inet-nm-exec",
        args=['"sleep 2"', "--missing"],
        timeout=2,
        skip_read=True,
    )

    ret = ct.run_step(
        description="In a different terminal, we can see all our boards are used.",
        cmd="inet-nm-check",
        args=["--missing", "--only-used"],
    )
    assert "board_1" in ret
    assert "board_2" in ret
    assert "board_3" in ret

    ret = ct.run_step(
        description="We can force them to be freed with the free command, "
        "this will not cancel ongoing processes so be careful as "
        "flashing or board output might conflict.",
        cmd="inet-nm-free",
    )

    assert "Removing lock file" in ret

    ret = ct.run_step(
        description="Now we can see they are free again.",
        cmd="inet-nm-check",
        args=["--missing"],
    )
    assert "board_1" in ret
    assert "board_2" in ret
    assert "board_3" in ret

    ct.run_step(
        description="What happens if we now add `board_3` to the board info cache?",
        cmd="inet-nm-update-from-os",
        args=[
            ".",
            "--board-info",
            '"echo board_1 board_2 board_3"',
            "--board-features",
            '"echo feature_common feature_${BOARD}"',
        ],
    )

    ct.run_step(
        description="Well we can updated the nodes cache in a separate step, "
        "no need to re-commission.",
        cmd="inet-nm-update-commissioned",
    )

    ret = ct.run_step(
        description="Now we can see the new feature and board is available.",
        cmd="inet-nm-check",
        args=["--missing", "--feat-filter", "feature_board_3"],
    )

    assert "board_3" in ret

    ct.run_step(
        description="The default environment is namespaced with `NM_` but how "
        "about being able to setup a custom environment... "
        "Well, we can do that too! Let's start with just adding an "
        "env variable to all node environments. "
        "This will apply to all commissioned nodes and any future "
        "commissioned nodes. "
        "Take special note of the escape characters and brackets. "
        "Just something like `\\$VAR` will not work, `\\${VAR}` is needed.",
        cmd="inet-nm-export",
        args=["MY_CUSTOM_BOARD_ENV_VAR", "\\${NM_BOARD}", "--apply-to-shared"],
    )

    ct.run_step(
        description="Apply a pattern to select only some boards or features.",
        cmd="inet-nm-export",
        args=[
            "MY_CUSTOM_SETTING",
            "1",
            "--apply-pattern",
            "--missing",
            "--feat-filter",
            "feature_board_3",
        ],
    )

    ct.run_step(
        description="The pattern has higher priority than the shared env vars. "
        "Let's overwrite the shared variable for board 2",
        cmd="inet-nm-export",
        args=[
            "MY_CUSTOM_BOARD_ENV_VAR",
            "board_2",
            "--apply-pattern",
            "--missing",
            "--boards",
            "board_2",
        ],
    )

    ct.run_step(
        description="Finally we can apply env vars to specific nodes. "
        "This is based on the UID, therefor commissioning new nodes will not "
        "contain these env vars. This has the highest priority.",
        cmd="inet-nm-export",
        args=[
            "MY_CUSTOM_NODE_HAS_SPECIAL_HARDWARE_FLAG",
            "1",
            "--missing",
            "--boards",
            "board_1",
            "--skip-dups",
        ],
    )

    ret = ct.run_step(
        description="Now we can check each environment.",
        cmd="inet-nm-exec",
        args=['"printenv | grep MY_CUSTOM"', "--missing"],
    )

    assert ret.count("board_1: MY_CUSTOM_NODE_HAS_SPECIAL_HARDWARE_FLAG") == 1
    assert ret.count("board_3: MY_CUSTOM_SETTING") == 1
    assert ret.count("MY_CUSTOM_BOARD_ENV_VAR") == 4
    assert ret.count("MY_CUSTOM_BOARD_ENV_VAR=board_2") == 1

    ct.run_step(
        description="Let's say I want to check the state of my boards. "
        "I can see a nice table of what is available, used, and missing.",
        cmd="inet-nm-inventory",
    )

    ret = ct.run_step(
        description="We can also get that in a machine readable way.",
        cmd="inet-nm-inventory",
        args=["--json"],
    )

    res = json.loads(ret)

    assert res[0]["board"] == "board_1"
    assert res[0]["available"] == 0
    assert res[0]["used"] == 0
    assert res[0]["missing"] == 2
    assert res[0]["total"] == 2

    assert res[1]["board"] == "board_2"
    assert res[2]["board"] == "board_3"

    # write a example json string to a tmp dir
    tmp_json = tmpdir / "example.json"
    with open(tmpdir / "example.json", "w") as f:
        f.write(
            """
log info
{
    "a": 1,
    "b": 2
} more generic text
            """
        )  # noqa

    ret = ct.run_step(
        description="Boy, we are adding features and boards all the time, "
        "let's see some exec json filtering now.",
        cmd="inet-nm-exec",
        args=["--missing", "--json-filter", f'"cat {tmp_json}"'],
    )

    res = json.loads(ret)

    assert res[0]["data"][0]["a"] == 1
    assert res[0]["data"][0]["b"] == 2
    uid = res[0]["uid"]
    board = res[0]["board"]

    ret = ct.run_step(
        description="We can also select nodes based on UID",
        cmd="inet-nm-check",
        args=["--missing", "--uids", f"{uid}"],
    )

    assert board in ret

    ubi = tmpdir / "user_board_info.json"
    with open(ubi, "w") as f:
        f.write(f'{{"{board}": ["user_feature"]}}')

    ct.run_step(
        description="We can also add `user_board_info.json`. "
        "that will not get overridden when updating... I added it behind the scenes.",
        cmd="inet-nm-exec",
        args=[f'"cat {ubi}"', "--missing", "--boards", "board_3"],
    )

    ct.run_step(
        description="Since this is a board parameter, we must update the "
        "already commissioned boards.",
        cmd="inet-nm-update-commissioned",
    )

    ret = ct.run_step(
        description="Now we can see the new feature.",
        cmd="inet-nm-check",
        args=["--feat-filter", "user_feature", "--missing"],
    )

    assert board in ret

    uni = tmpdir / "user_node_info.json"
    with open(uni, "w") as f:
        f.write(f'{{"{uid}": ["user_node_feature"]}}')

    ct.run_step(
        description="We can also add features to specific nodes with "
        "`user_node_info.json`.",
        cmd="inet-nm-exec",
        args=[f'"cat {uni}"', "--missing", "--boards", "board_3"],
    )

    ret = ct.run_step(
        description="This can be directly checked.",
        cmd="inet-nm-check",
        args=["--feat-filter", "user_node_feature", "--missing"],
    )

    assert board in ret

    # End with this
    ct.run_step(
        description="Let's decommission boards, say the have all broken.",
        cmd="inet-nm-decommission",
        args=["--all", "--missing"],
    )

    ret = ct.run_step(
        description="Now we can see nothing is there",
        cmd="inet-nm-check",
        args=["--missing"],
    )

    assert "{}" in ret

    if cli_readme_mock:
        with open(cli_readme_mock, "w") as f:
            f.write(ct.format_md())
    else:
        print(ct.format_md())
