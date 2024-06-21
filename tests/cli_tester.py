import os
import sys
import time

if sys.platform == "win32":
    from pexpect.popen_spawn import PopenSpawn
else:
    import pexpect


class CliTester:
    CLI_PREFIX = "inet_nm_"
    CLI_PREFIX_REPLACE = "inet_nm.cli_"
    DEFAULT_START_WAIT_TIME = 0.2
    DEFAULT_PROCESS_TIMEOUT = 2

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # TODO: Maybe we should force all procs to terminate but I don't
        # now if this will be working on windows... so let's leave it for now.
        if self.teardown:
            self.teardown()
        if self.md_output_file:
            with open(self.md_output_file, "w") as f:
                f.write(self.format_md())


    def __init__(self):
        self.title = None
        self.description = None
        self.footer = None
        self.replace_strings = None
        self.md_output_file = None
        self.teardown = None
        self.cwd = os.getcwd()
        self.cov_rc = f"{self.cwd}/.coveragerc"
        self.cov_data_file = f"{self.cwd}/.coverage"
        os.environ["COVERAGE_PROCESS_START"] = ".coveragerc"
        self._step_results = []
        self._async_procs = []

    @property
    def output_to_stdout(self):
        return self.md_output_file is None

    def _cmd_to_coverage(self, cmd):
        # We do not care about coverage for commands that do not fit
        if self.CLI_PREFIX.replace("-", "_") not in cmd:
            return cmd
        cmd = cmd.replace("-", "_")
        cmd = cmd.replace(self.CLI_PREFIX, self.CLI_PREFIX_REPLACE)
        full_cmd = "coverage run "
        full_cmd += f"--data-file={self.cov_data_file} "
        full_cmd += f"--rcfile={self.cov_rc} -m {cmd}"
        return full_cmd

    def _fmt_cmd_to_str(self, cmd, args):
        cmd_str = f"{cmd} {' '.join(args or [])}"
        if self.replace_strings:
            for k, v in self.replace_strings.items():
                cmd_str = cmd_str.replace(k, v)
        return cmd_str

    def _fmt_output(self, output: bytes):
        output = output.decode(errors="ignore").replace("\r\n", "\n")
        if self.replace_strings:
            for k, v in self.replace_strings.items():
                output = output.replace(k, v)
        return output

    def run_step(
        self,
        cmd,
        args=None,
        sendlines=None,
        description=None,
        timeout=None,
        skip_read=False,
        cwd=None,
        hidden=False
    ):
        cov_cmd = self._cmd_to_coverage(cmd)
        cov_cmd = f"{cov_cmd} {' '.join(args or [])}"
        if sys.platform == "win32":
            child = PopenSpawn(
                cmd=cov_cmd,
                timeout=timeout or self.DEFAULT_PROCESS_TIMEOUT,
                cwd=cwd or self.cwd,
            )
        else:
            child = pexpect.spawn(
                command=cov_cmd,
                timeout=timeout or self.DEFAULT_PROCESS_TIMEOUT,
                cwd=cwd or self.cwd,
            )
        time.sleep(self.DEFAULT_START_WAIT_TIME)
        for line in sendlines or []:
            child.sendline(line)

        cmd_str = self._fmt_cmd_to_str(cmd, args)
        if self.output_to_stdout:
            print(cmd_str)

        if skip_read:
            self._async_procs.append(child)
            output = ""
        else:
            output = self._fmt_output(child.read())
        if self.output_to_stdout:
            print(output)
        if not hidden:
            self._step_results.append(
                (description, cmd_str, output)
            )
        return output

    def format_md(self):
        out = ""
        if self.title:
            out += f"# {self.title}\n\n"
        if self.description:
            out += f"{self.description}\n\n"
        out += "## Steps\n\n"
        skips = 0
        for idx, (desc, cmd, output) in enumerate(self._step_results):
            if desc is None:
                skips += 1
            else:
                out += f"{idx - skips + 1}. {desc}\n"
            out += f"```bash\n$ {cmd}\n"
            out += f"{output}```\n\n"
        if self.footer:
            out += f"{self.footer}\n"
        return out
