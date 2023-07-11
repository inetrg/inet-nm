"""
Runs applications on nodes.

This module provides the NmNodesRunner class which handles running
operations on multiple nodes.
An operation is defined by a method `func` which is to be implemented
in the subclass.
"""
from threading import Thread
from typing import Dict, List

import inet_nm.locking as lk
from inet_nm._helpers import nm_print
from inet_nm.commissioner import TtyNotPresent, get_tty_from_nm_node
from inet_nm.data_types import NmNode, NodeEnv
from inet_nm.filelock import FileLock


class NmNodesRunner:
    """
    Class to handle running operations on nodes.

    The class manages locking/unlocking nodes, running operations on each node
    concurrently in separate threads, and handles cleanup after operations
    have completed.

    The operations to be run are defined by a method `func` which is to
    be implemented in the subclass.
    """

    def __init__(self, nodes: List[NmNode], default_timeout: int = None, seq=False):
        """
        Initialize a new instance of NmNodesRunner.

        Args:
            nodes: A list of NmNode instances to be managed.
            default_timeout: Default timeout value for file lock acquisition.
            seq: If True, operations are run sequentially instead of concurrently.

        """
        self.nodes = nodes
        self.default_timeout = default_timeout
        self.seq = seq
        self.lockable_nodes = [
            (node, FileLock(lk.get_lock_path(node), timeout=default_timeout))
            for node in nodes
        ]
        self.locks = [lock for _, lock in self.lockable_nodes]
        self._acquired = False

    def pre(self):
        """Override in the subclass if pre-operation steps are needed."""
        pass

    def post(self):
        """Override in the subclass if post-operation steps are needed."""
        pass

    def func(self, node: NmNode, idx: int, env: Dict[str, str]):
        """
        Function to execute.

        It must be implemented in the subclass.

        Args:
            node: The node to run the function on.
            idx: The index of the node in the list of nodes.
            env: A dictionary of environment variables.
        """
        raise NotImplementedError("You must implement a func() method")

    def acquire(self, timeout: float = None):
        """
        Acquire file locks for all nodes.

        This method must be called before running operations on nodes.

        Args:
            timeout (float): Timeout value for file lock acquisition.
                If None, default_timeout is used.
        """
        for lock in self.locks:
            lock.acquire(timeout=timeout or self.default_timeout)
        self._acquired = True

    def release(self):
        """Release all acquired file locks."""
        for lock in self.locks:
            try:
                lock.release()
            except FileNotFoundError:
                nm_print(f"File {lock.file_name} already unlocked.")
        self._acquired = False

    def run(self):
        """
        Run operations on all nodes.

        This method spawns a new thread for each node and runs the
        operation concurrently on all nodes.
        The operation to run is defined by the `func` method.
        """
        if not self._acquired:
            raise Exception("You must call acquire() before calling run()")

        self.pre()

        self.threads = []
        for idx, node in enumerate(self.nodes):
            try:
                nm_port = get_tty_from_nm_node(node)
            except TtyNotPresent:
                nm_port = "Unknown"
            node_env = NodeEnv(
                NM_IDX=idx,
                NM_UID=node.uid,
                NM_SERIAL=node.serial,
                NM_BOARD=node.board,
                NM_PORT=nm_port,
            ).to_dict()

            thread = Thread(target=self.func, args=(node, idx, node_env))
            thread.start()
            if self.seq:
                thread.join()
            else:
                self.threads.append(thread)

        for thread in self.threads:
            thread.join()

        self.post()
        self.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, type, value, traceback):
        if self._acquired:
            self.release()
            self._acquired = False
