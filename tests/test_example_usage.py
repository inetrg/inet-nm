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
            out += f"{self.footer}\n\n"
        return out


try:
    import inquirer
except ImportError:
    inquirer = None


@flaky(max_runs=1)
@pytest.mark.skipif(inquirer is not None, reason="does not run on windows")
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
        args=['"sleep 0.5"', "--missing", "--skip-dups", "--boards", "board_1"],
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

    if cli_readme_mock:
        with open(cli_readme_mock, "w") as f:
            f.write(ct.format_md())
    else:
        print(ct.format_md())
