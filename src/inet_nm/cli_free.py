import argparse

import inet_nm.locking as lk
from inet_nm._helpers import nm_print


def main():
    """Release all locks by deleting all lock files and print the process."""
    parser = argparse.ArgumentParser(description="Forces release of all locks.")
    parser.parse_args()

    nm_print("Releasing all locks")

    for lock_file in lk.locks_dir().glob("*"):
        nm_print(f"Removing lock file {lock_file}")
        lock_file.unlink()
    nm_print("All locks released")


if __name__ == "__main__":
    main()
