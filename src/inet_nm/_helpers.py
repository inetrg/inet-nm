"""Interactive user prompts and general basic helpers."""

import os
import readline
import sys
from typing import Callable, List, Optional

try:
    import inquirer
except ImportError:
    inquirer = None


def nm_prompt_choice(
    msg: str,
    choices: List[str],
    choice_func: Optional[Callable] = None,
    custom: bool = False,
) -> str:
    """
    Interactive user prompt to choose from a list of choices.

    If inquirer is not installed, a simpler choice will be used.
    If choice_func is provided, it will be applied to the choices for display.

    Args:
        msg: Message to display to the user.
        choices: List of choices.
        choice_func: Function to format choices for display.
        custom: Allow user to provide custom input.

    Returns:
        str: The selected or entered choice.

    Raises:
        ValueError: If no choices are available.
    """
    if len(choices) == 0:
        raise ValueError(f"No choices available for: {msg}")
    if len(choices) == 1:
        return choices[0]
    if custom:
        choices.append("custom")
    if choice_func:
        _choices = [choice_func(choice) for choice in choices]
    else:
        _choices = choices

    res = _prompt_choice(msg, _choices)
    if res == "custom":
        return input("Custom value: ")
    return choices[_choices.index(res)] if choice_func else res


def _prompt_choice(
    msg: str,
    choices: List[str],
) -> str:
    if inquirer:
        return _inquirer_prompt_choice(msg, choices)
    return _basic_prompt_choice(msg, choices)


def _inquirer_prompt_choice(
    msg: str,
    choices: List[str],
) -> str:
    res = inquirer.prompt(
        [inquirer.List("res", message=msg, choices=choices)],
        raise_keyboard_interrupt=True,
    )
    return res["res"]


def _basic_prompt_choice(msg: str, choices: List[str]) -> str:
    nm_print(msg)
    for i, choice in enumerate(choices):
        nm_print(f"{i+1}. {choice}")
    while True:
        try:
            choice = int(input("> "))
            if choice < 1 or choice > len(choices):
                raise ValueError
            break
        except ValueError:
            nm_print(
                "Invalid choice. Please enter a number between 1 and " f"{len(choices)}"
            )
    return choices[choice - 1]


class _Completer:
    """Helper class for command line autocompletion."""

    def __init__(self, options: List[str]):
        """
        Initialize _Completer with a list of options.

        Args:
            options: List of autocompletion options.
        """
        self.options = sorted(options)

    def complete(self, text: str, state: int) -> Optional[str]:
        """
        Autocomplete function used by readline.

        Args:
            text: Partial text to complete.
            state: Index of the match being requested.

        Returns:
            Match at index 'state', or None if index is out
                of bounds.
        """
        if state == 0:  # on first trigger, build possible matches
            if not text:
                self.matches = self.options[:]
            else:
                mat = [s for s in self.options if s and s.startswith(text)]
                self.matches = mat

        # return match indexed by state
        try:
            return self.matches[state]
        except IndexError:
            return None

    def display_matches(self, substitution: str, matches: List[str], _):
        """
        Display possible matches to the user.

        Args:
            substitution (str): The substitution made so far.
            matches (List[str]): List of matches found.
        """
        line_buffer = readline.get_line_buffer()
        columns = os.environ.get("COLUMNS", 80)

        nm_print()
        full_matches = [substitution + match for match in matches]

        tpl = "{:<" + str(int(max(map(len, full_matches)) * 1.2)) + "}"

        buffer = ""
        for match in full_matches:
            match = tpl.format(match[len(substitution) :])
            if len(buffer + match) > columns:
                nm_print(buffer)
                buffer = ""
            buffer += match

        if buffer:
            nm_print(buffer)

        nm_print("> ", end="")
        nm_print(line_buffer, end="")
        sys.stdout.flush()


def nm_prompt_input(prompt: str, options: List[str] = None) -> str:
    """
    Interactive user prompt with auto-completion.

    Args:
        prompt: Message to display to the user.
        options: List of auto-completion options.

    Returns:
        User input.
    """
    if options is None:
        options = []
    completer = _Completer(list(set(options)))
    readline.set_completer_delims(" \t\n;")
    readline.set_completer(completer.complete)
    readline.parse_and_bind("tab: complete")
    readline.set_completion_display_matches_hook(completer.display_matches)

    nm_print(prompt)
    return nm_input("> ")


def nm_prompt_default_input(prompt: str, default: str) -> str:
    """
    Interactive user prompt with auto-completion and default value.

    Args:
        prompt: Message to display to the user.
        default: Default value.

        Returns:
            User input."""
    return nm_input(f"{prompt} [{default}]: ") or default


def nm_prompt_confirm(msg: str, default: bool = False) -> bool:
    """
    Interactive user prompt for confirmation.

    Args:
        msg: Message to display to the user.
        default: Default value.

    Returns:
        bool: User confirmation.
    """
    if inquirer:
        res = inquirer.prompt(
            [inquirer.Confirm("res", message=msg, default=default)],
            raise_keyboard_interrupt=True,
        )
        return res["res"]
    else:
        return nm_input(f"{msg} [y/N] ").lower() == "y"


def nm_print(*args, **kwargs):
    """Abstraction of print."""
    print(*args, **kwargs)


def nm_input(*args, **kwargs):
    """Abstraction of input."""
    return input(*args, **kwargs)
