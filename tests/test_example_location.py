import json
import os

import pytest
from cli_tester import CliTester
from flaky import flaky

try:
    import inquirer
except ImportError:
    inquirer = None


@flaky(max_runs=1)
@pytest.mark.skipif(inquirer is not None, reason="inquirer should not be installed")
@pytest.mark.slow
def test_cli_example_locate(tmpdir, cli_readme_mock):
    ct = CliTester()
    ct.title = "Example usage of `inet-nm` location features"
    ct.description = "The following will add some fake boards in order to show"
    ct.description += " the features of the `inet-nm` location commands."
    ct.description += " With the fake boards will need to commission some and "
    ct.description += "then we can start setting the locations."
    ct.description += " We can see how info is stored and also a nice graph."
    ct.footer = "The suggested workflow is to use just one board and map all "
    ct.footer += "the locations, removing and moving each slot. "
    ct.footer += "Then add all the boards in after. "
    ct.footer += "I hope you enjoyed and learned a little something."

    ct.run_step(
        description="We would like to display the following command but "
        "need some setup.",
        cmd="inet-nm-set-location",
        args=[
            "--help",
        ],
    )

    ct.run_step(
        cmd="inet-nm-show-location",
        args=[
            "--help",
        ],
    )

    os.environ["NM_CONFIG_DIR"] = str(tmpdir)

    ct.run_step(
        description="First let's fake plug in a board.",
        cmd="inet-nm-fake-usb",
        args=[
            "--id",
            "board_1",
        ],
    )

    os.environ["INET_NM_FAKE_USB_PATH"] = str(tmpdir) + "/fakes.json"

    ct.run_step(
        description="OK... all set, let's see this now!",
        cmd="inet-nm-fake-usb",
        args=[
            "--id",
            "board_1",
        ],
    )

    ct.run_step(
        description="Let commission it.",
        cmd="inet-nm-commission",
        sendlines=[
            "board_1",
            "y",
        ],
    )

    ct.run_step(
        description="And another...",
        cmd="inet-nm-fake-usb",
        args=[
            "--id",
            "board_2",
        ],
    )

    ct.run_step(
        cmd="inet-nm-commission",
        sendlines=[
            "board_2",
            "y",
        ],
    )

    ct.run_step(
        description="And one more for good luck, we don't need id for fake"
        " boards really.",
        cmd="inet-nm-fake-usb",
    )

    ct.run_step(
        cmd="inet-nm-commission",
        sendlines=[
            "board_3",
            "y",
        ],
    )

    ret = ct.run_step(
        description="Now we are ready! Let's set a location.",
        cmd="inet-nm-set-location",
        sendlines=[
            "1",
            "",
        ],
    )
    assert "1.1.1 mapped to" in ret

    ret = ct.run_step(
        description="Hmmm, it seems there is a recommendation here... A little"
        " hint, it is part of the inet-mbh project which is a"
        " is a modular system that holds up to 4 boards. Thus, a"
        " recommended naming scheme is "
        "`<vertical_position*4>.<horazontal_position>."
        "<vertical_position>`"
        " (e.g. 1.1.1). If you follow this convention, then cool"
        " things happen as well as some recommendations.",
        cmd="inet-nm-set-location",
        sendlines=[
            "1",
            "2.3.4",
        ],
    )
    assert "2.3.4 mapped to" in ret

    ret = ct.run_step(
        description="Of course we don't need to follow anything.",
        cmd="inet-nm-set-location",
        sendlines=[
            "in the garbage",
        ],
    )
    assert "in the garbage mapped to" in ret

    ret = ct.run_step(
        description="Let's see what we have.",
        cmd="inet-nm-show-location",
    )
    try:
        ret = json.loads(ret)
        assert ret[0]["location"] == "1.1.1"
        assert ret[1]["location"] == "2.3.4"
        assert ret[2]["location"] == "in the garbage"
    except json.JSONDecodeError:
        assert False, "Could not decode json\n" + ret

    ret = ct.run_step(
        description="Hard to read, eh? So let's get visual. Notice the postions",
        cmd="inet-nm-show-location",
        args=[
            "--graph",
        ],
    )
    assert (
        """┌─┬─┬─┐
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
in the garbage\n"""
        == ret
    )

    del os.environ["INET_NM_FAKE_USB_PATH"]

    if cli_readme_mock:
        with open(os.path.join(cli_readme_mock, "example_locate.md"), "w") as f:
            f.write(ct.format_md())
    else:
        print(ct.format_md())
