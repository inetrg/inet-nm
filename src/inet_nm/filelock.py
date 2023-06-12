"""
This module provides a simple implementation of a file-based locking mechanism.

The main class `FileLock` uses OS-level file system operations for locking
and unlocking.
This kind of lock can be used to prevent the simultaneous execution of a piece
of code by different processes.
"""
import os
import time


class FileLockTimeout(Exception):
    """
    Exception raised when a file lock operation fails.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Timeout occurred."):
        """Initialize the exception."""
        self.message = message
        super().__init__(self.message)


class FileLock:
    """
    Provides a context manager-based file lock mechanism.

    Attributes:
        file_name: The name of the file to be used as the lock.
        timeout (int): The maximum time to wait for the lock to be released.
    """

    def __init__(self, file_name: str, timeout: int = 10) -> None:
        """
        Construct a new FileLock object.

        Args:
            file_name: The name of the file to be used as the lock.
            timeout: The maximum time to wait for the lock to be released.
        """
        self.file_name = file_name
        self.timeout = timeout
        self.fd = None
        self._lock_held = False

    def acquire(self, timeout: int = None, poll_interval: float = 0.05) -> None:
        """
        Acquire the file lock.

        If the lock is currently in use, wait until it is released,
        or until the specified timeout has passed.

        Args:
            timeout: The maximum time to wait for the lock to be released.
                Default is None, which means use self.timeout.
            poll_interval: Time interval to check the lock file's existence.

        Raises:
            FileLockTimeout: If the timeout has passed and the lock
                has not been released.
        """
        timeout = timeout or self.timeout
        start_time = time.time()
        while True:
            try:
                os.umask(0)
                self.fd = os.open(
                    self.file_name, flags=os.O_CREAT | os.O_EXCL | os.O_RDWR, mode=0o777
                )
                self._lock_held = True
                break
            except FileExistsError:
                if time.time() - start_time >= timeout:
                    msg = f"Timeout trying to lock {self.file_name}"
                    raise FileLockTimeout(msg)
                else:
                    time.sleep(poll_interval)

    def release(self, force: bool = False) -> None:
        """
        Release the file lock.

        Args:
            force: If True, force release the lock even if the lock is
                held by others.
        """
        if self._lock_held:
            os.close(self.fd)
            os.unlink(self.file_name)
        elif force:
            try:
                os.unlink(self.file_name)
            except OSError:
                pass
        self._lock_held = False

    @property
    def is_locked(self) -> bool:
        """
        Check if the file lock is locked.

        Returns:
            bool: True if the lock file exists, False otherwise.
        """
        return os.path.exists(self.file_name)

    def __enter__(self) -> "FileLock":
        """Acquire the lock when entering the context."""
        self.acquire()
        return self

    def __exit__(self, type, value, traceback) -> None:
        """Release the lock when exiting the context."""
        self.release()
