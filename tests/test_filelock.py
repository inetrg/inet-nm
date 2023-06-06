import random

import pytest

from inet_nm.filelock import FileLock, FileLockTimeout


def test_filelock(tmpdir):
    # Create a lock file path in the platform-independent temporary directory
    lock_file = tmpdir.join(f"testlock-{random.randint(0, 100000)}.lock")

    with FileLock(str(lock_file), timeout=0.1) as lock:
        assert lock.is_locked
        with pytest.raises(FileLockTimeout):
            with FileLock(str(lock_file), timeout=0.1):
                pass

    lock = FileLock(str(lock_file), timeout=1)
    assert not lock.is_locked
