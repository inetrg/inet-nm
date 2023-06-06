from unittest.mock import patch

import pytest

from inet_nm._helpers import (
    inquirer,
    nm_prompt_choice,
    nm_prompt_confirm,
    nm_prompt_input,
)


def test_nm_prompt_choice_single_choice():
    """Test nm_prompt_choice function with single choice."""
    assert nm_prompt_choice("Choose", ["choice1"]) == "choice1"


def test_nm_prompt_choice_multiple_choices():
    """Test nm_prompt_choice function with multiple choices."""
    with patch("inet_nm._helpers._prompt_choice", return_value="choice2"):
        assert nm_prompt_choice("Choose", ["choice1", "choice2"]) == "choice2"


@pytest.mark.skipif(not inquirer, reason="inquirer not installed")
def test_nm_prompt_choice_multiple_choices_inquirer():
    """Test nm_prompt_choice function with multiple choices mocking inquirer."""
    with patch("inquirer.prompt", return_value={"res": "choice2"}):
        assert nm_prompt_choice("Choose", ["choice1", "choice2"]) == "choice2"


def test_nm_prompt_choice_with_custom():
    """Test nm_prompt_choice function with custom input."""
    with patch("inet_nm._helpers._prompt_choice", return_value="custom"), patch(
        "builtins.input", return_value="mychoice"
    ):
        assert (
            nm_prompt_choice("Choose", ["choice1", "choice2"], custom=True)
            == "mychoice"
        )


def test_nm_prompt_choice_multiple_choices_func():
    """Test nm_prompt_choice function with multiple choices non-string choices."""

    def _test(val: int):
        msg = f"val=={val+1}"
        return msg

    with patch("inet_nm._helpers._prompt_choice", return_value="val==2"):
        assert nm_prompt_choice("Choose", [1, 10], _test) == 1


def test_nm_prompt_input():
    """Test nm_input function."""
    with patch("builtins.input", return_value="myinput"):
        assert nm_prompt_input("Enter value") == "myinput"


@pytest.mark.skipif(not inquirer, reason="inquirer not installed")
def test_nm_prompt_confirm():
    """Test nm_prompt_confirm function."""
    with patch("inquirer.prompt", return_value={"res": True}):
        assert nm_prompt_confirm("Confirm") is True
    with patch("inquirer.prompt", return_value={"res": False}):
        assert nm_prompt_confirm("Confirm") is False
