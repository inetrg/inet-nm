"""
This module includes classes that are used to run applications on nodes.

Classes:
    NmShellRunner: Runs shell commands on nodes.
    NmTmuxPanedRunner: Runs tmux with paned windows.
    NmTmuxWindowedRunner: Runs tmux with individual windows for each node.
"""

import os
import subprocess
import time
from typing import Dict

from inet_nm._helpers import nm_print
from inet_nm.data_types import NmNode
from inet_nm.runner_base import NmNodesRunner


class NmShellRunner(NmNodesRunner):
    """Runs shell commands on nodes.

    This class inherits from NmNodesRunner and overrides the func method
    to execute shell commands on nodes.

    Attributes:
        cmd: Command to execute on nodes.
    """

    cmd = "echo $NM_IDX"
    SETUP_WAIT = 0.1

    @staticmethod
    def _run_command(cmd, prefix, env):
        def get_output(process):
            output = process.stdout.readline()

            if output:
                nm_print(f"{prefix}{output.decode().strip()}")
            else:
                # Have a small sleep so we are not burning CPU waiting for output.
                time.sleep(0.1)
            return output

        process = subprocess.Popen(
            cmd, env=env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        while True:
            output = get_output(process)
            poll = process.poll()
            if poll is not None:
                output = True
                while output:
                    output = get_output(process)
                break
        rc = process.returncode

        return rc

    def func(self, node: NmNode, idx: int, env: Dict[str, str]):
        """Execute shell commands on nodes.

        Args:
            node: Node to run the command on.
            idx: Index of the node.
            env: Environment variables for the command.
        """
        time.sleep(idx * self.SETUP_WAIT)
        full_env = {**os.environ, **env}  # Merge original and new environment variables
        full_env = {
            k: str(v) for k, v in full_env.items()
        }  # Cast everything in env to a string

        prefix = f"NODE:{idx}"
        if node.board:
            prefix += f":BOARD:{node.board}"
        prefix += ": "

        # Since most use cases are with bash we will use that as the default shell.
        # This may change as soon as we have a use case that requires a different shell.
        # Note that the run command exits after one command is executed.
        # So if we want to loop with a default shell it will exit after the first loop.
        cmd = f"/bin/bash -c '{self.cmd}'"
        NmShellRunner._run_command(cmd, prefix=prefix, env=full_env)


class NmTmuxBaseRunner(NmNodesRunner):
    """Base class for tmux runners.

    This class inherits from NmNodesRunner and sets up a tmux session.
    """

    session_name: str = "default"
    cmd: str = None
    SETUP_WAIT = 0.2

    def post(self):
        """Run after the operations on nodes have completed.

        It attaches to the tmux session and keeps checking if
        the session is still active.
        """
        os.system(f"tmux attach -t {self.session_name}")

        while True:
            result = subprocess.run(
                f"tmux has-session -t {self.session_name}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if result.returncode != 0:
                break


class NmTmuxPanedRunner(NmTmuxBaseRunner):
    """Run tmux with paned windows.

    This class inherits from NmTmuxBaseRunner and sets up a tmux
    session with panes.
    """

    def func(self, node: NmNode, idx: int, env: Dict[str, str]):
        """Set up a tmux session with paned windows.

        Args:
            node: Node to run the command on.
            idx: Index of the node.
            env: Environment variables for the command.
        """
        time.sleep(idx * self.SETUP_WAIT)

        e_args = " -e " + " -e ".join([f"{key}={value}" for key, value in env.items()])
        if idx != 0:
            subprocess.run(
                f"tmux split-window {e_args} -t {self.session_name}", shell=True
            )
        else:
            subprocess.run(f"tmux new-session -d -s {self.session_name}", shell=True)
            subprocess.run(
                f"tmux respawn-window -k {e_args} -t {self.session_name} -t 0.{idx}",
                shell=True,
            )

        # Select pane
        subprocess.run(f"tmux select-pane -t {idx}", shell=True)

        # Execute command
        if self.cmd:
            subprocess.run(
                f"tmux send-keys -t {self.session_name}:0.{idx} '{self.cmd}' Enter",
                shell=True,
            )

        # Evenly distribute panes
        subprocess.run(f"tmux select-layout -t {self.session_name} tiled", shell=True)


class NmTmuxWindowedRunner(NmTmuxBaseRunner):
    """Runs tmux with individual windows for each node.

    This class inherits from NmTmuxBaseRunner and sets up a tmux session with
    individual windows for each node.
    """

    def func(self, node: NmNode, idx: int, env: Dict[str, str]):
        """Sets up a tmux session with individual windows for each node.

        Args:
            node: Node to run the command on.
            idx: Index of the node.
            env: Environment variables for the command.
        """
        env = {k: str(v) for k, v in env.items()}  # Cast everything in env to a string
        uid = env["NM_UID"]
        session_name = self.session_name

        time.sleep(idx * self.SETUP_WAIT)

        e_args = " -e " + " -e ".join([f"{key}={value}" for key, value in env.items()])
        if idx != 0:
            subprocess.run(
                f"tmux new-window -t {session_name}:{idx} {e_args}", shell=True
            )
        else:
            subprocess.run(f"tmux new-session -d -s {session_name}", shell=True)
            subprocess.run(
                f"tmux respawn-window -k {e_args} -t {session_name} -t 0.{idx}",
                shell=True,
            )

        subprocess.run(f"tmux rename-window -t {session_name}:{idx} {uid}", shell=True)

        if self.cmd:
            subprocess.run(
                f"tmux send-keys -t {session_name}:{idx} '{self.cmd}' Enter", shell=True
            )
