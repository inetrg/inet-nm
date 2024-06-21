import json
import os
import sys
import time

import pytest
from cli_tester import CliTester
from flaky import flaky

try:
    import inquirer
except ImportError:
    inquirer = None


@flaky(max_runs=1)
@pytest.mark.skipif(inquirer is not None, reason="inquirer should not be installed")
@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
@pytest.mark.slow
@pytest.mark.os_specific
def test_cli_example_riot(tmpdir, cli_readme_mock):
    def teardown():
        if "INET_NM_FAKE_USB_PATH" in os.environ:
            del os.environ["INET_NM_FAKE_USB_PATH"]

    with CliTester() as ct:
        ct.title = "Example of how to use this tool with RIOT OS."
        ct.description = "This will use fake boards to go through the workflow "
        ct.description += "that RIOTers will use."
        ct.footer = "Hope you enjoyed and happy RIOTing."
        ct.teardown = teardown
        ct.replace_strings = {str(tmpdir): "~"}
        if cli_readme_mock:
            ct.md_output_file = os.path.join(cli_readme_mock, "example_riot.md")

        os.environ["NM_CONFIG_DIR"] = str(tmpdir)
        os.environ["INET_NM_FAKE_USB_PATH"] = str(tmpdir) + "/fakes.json"

        _riot_dir = os.path.join(tmpdir, "RIOT")
        ct.run_step(
            description="I guess we need to clone RIOT first and can operate from there.",
            cmd="git",
            args=[
                "clone",
                "--branch",
                "2024.01",
                "--depth",
                "1",
                "-q",
                "https://github.com/RIOT-OS/RIOT.git",
                _riot_dir,
            ],
            timeout=120,
        )

        ct.cwd = _riot_dir
        ct.run_step(
            description="See... We did a secret cd to the RIOT dir.",
            cmd="pwd"
        )


        # HACK: This is a hack since there are some toolchain requirements just
        # to get a list of features.
        os.environ["BUILD_IN_DOCKER"] = "1"
        ct.run_step(
            description="Now let's get out board list.",
            cmd="inet-nm-update-from-os",
            args=[
                os.path.join("examples", "hello-world"),
            ],
            timeout=60,
        )
        del os.environ["BUILD_IN_DOCKER"]

        ct.run_step(
            description="We can also setup out env so we don't need to "
                        "worry about using the namespaced env vars.\n"
                        "Keep in mind we have a `scripts/riot-os-env-setup`.",
            cmd="inet-nm-export",
            args=[
                "--apply-to-shared",
                "BOARD",
                "${NM_BOARD}"
            ],
        )
        ct.run_step(
            cmd="inet-nm-export",
            args=[
                "--apply-to-shared",
                "BUILD_IN_DOCKER",
                "1"
            ],
        )
        ct.run_step(
            cmd="inet-nm-export",
            args=[
                "--apply-to-shared",
                "DEBUG_ADAPTER_ID",
                "${NM_SERIAL}"
            ],
        )
        ct.run_step(
            cmd="inet-nm-export",
            args=[
                "--apply-to-shared",
                "PORT",
                "${NM_PORT}"
            ],
        )

        ct.run_step(
            description="Now let's pretend to plug in 2 boards.",
            cmd="inet-nm-fake-usb",
            args=[
                "--id",
                "board_1",
            ],
        )
        ct.run_step(
            cmd="inet-nm-fake-usb",
            args=[
                "--id",
                "board_2",
            ],
        )

        ct.run_step(
            description="Let's commission, since there are multiple "
                        "boards we need to select one.",
            cmd="inet-nm-commission",
            sendlines=[
                "1",
                "samr21-xpro",
            ],
        )

        ct.run_step(
            cmd="inet-nm-commission",
            sendlines=[
                "nucleo-f103rb",
            ],
        )

        ct.run_step(
            description="OK, we should maybe to something like "
                        "`make flash-only test` but we "
                        "can't since the boards are... fake. So let's do "
                        "something board specific that doesn't really need a "
                        "board.",
            cmd="inet-nm-exec",
            args=[
                f"\"make info-cpu -C {os.path.join('examples', 'hello-world')}\"",
            ]
        )

        ct.run_step(
            description="For testing maybe we should remove RIOT since it takes "
                        "space. I guess nobody will see this.",
            cmd="rm",
            args=[
                "-rf",
                f"{tmpdir}/RIOT",
            ],
            hidden=True,
        )
