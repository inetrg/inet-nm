import logging
import subprocess
from time import sleep
from typing import List

import inet_nm.locking as lck
import inet_nm.usb_ctrl as ucl
from inet_nm.data_types import NmNode

DEFAULT_MAX_ALLOWED_NODES = 14


class PowerControl:
    DEFAULT_POWER_ON_WAIT = 10
    DEFAULT_POWER_OFF_WAIT = 1
    MAX_ALLOWED_NODES = 256

    def __init__(self, locations, nodes: List[NmNode], max_powered_devices=None):
        self.logging = logging.getLogger(__name__)
        self.id_path_to_node_uid = {}
        self.powered_locations = {}
        self.powered_id_paths = set()
        self.node_uids = {node.uid for node in nodes if not node.ignore}
        for id, loc in locations.items():
            if loc["power_control"]:
                self.powered_locations[id] = loc
                self.powered_id_paths.add(id)
        self.max_powered_devices = max_powered_devices
        self._running = False
        self._power_on_procs = []
        self._power_off_procs = []
        self._powered_on = set()

    def _available(self, powered_devs) -> int:
        if self.max_powered_devices is not None:
            return self.max_powered_devices - len(powered_devs)
        return self.MAX_ALLOWED_NODES

    def power_on_uid(self, uid: str):
        if uid not in self.id_path_to_node_uid.values():
            raise ValueError(
                f"Node with uid {uid} not found, "
                "must have been collected during power iterations."
            )
        for id_path, node_uid in self.id_path_to_node_uid.items():
            if node_uid == uid:
                if id_path in self.powered_locations:
                    self._power_on(id_path)

    def power_off_uid(self, uid: str):
        if uid not in self.id_path_to_node_uid.values():
            raise ValueError(
                f"Node with uid {uid} not found, "
                "must have been collected during power iterations."
            )
        for id_path, node_uid in self.id_path_to_node_uid.items():
            if node_uid == uid:
                if id_path in self.powered_locations:
                    self._power_off(id_path)

    def _power_off(self, id_path):
        self.logging.debug("Powering off %s", id_path)
        usb_info = self.powered_locations[id_path]
        self._power_off_procs.append(
            subprocess.Popen(
                [
                    "sudo",
                    "uhubctl",
                    "-l",
                    usb_info["hub"],
                    "-p",
                    usb_info["port"],
                    "-a",
                    "off",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

    def _power_on(self, id_path):
        self.logging.debug("Powering on %s", id_path)
        usb_info = self.powered_locations[id_path]
        self._power_on_procs.append(
            subprocess.Popen(
                [
                    "sudo",
                    "uhubctl",
                    "-l",
                    usb_info["hub"],
                    "-p",
                    usb_info["port"],
                    "-a",
                    "on",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

    def power_on_chunk(self):
        self._running = True
        powered_devs = ucl.get_connected_id_paths()
        available = self._available(powered_devs)

        if available < 0:
            raise ValueError(
                f"More than {self.max_powered_devices} nodes are "
                f"already powered on, {-available} over."
            )
        self.logging.debug(
            "%s nodes powered, %s of %s available",
            len(powered_devs),
            available,
            self.max_powered_devices or self.MAX_ALLOWED_NODES,
        )
        for id_path in self.powered_locations:
            if id_path in powered_devs:
                self._powered_on.add(id_path)
                continue
            if id_path in self._powered_on:
                continue
            self._power_on(id_path)
            # it takes a while to actually show up as a tty device
            # so we just manually add it
            self._powered_on.add(id_path)
            powered_devs.add(id_path)
            if self._available(powered_devs) == 0:
                break
        self.wait_for_power_on()

    @property
    def power_on_complete(self) -> bool:
        if not self._running:
            return False
        # check if all powered_id_paths are powered on
        if self._powered_on == self.powered_id_paths:
            self._running = False
            return True
        return False

    def _map_id_path_to_node_uid(self):
        powered_id_paths = ucl.get_connected_id_paths()
        for id_path in powered_id_paths:
            if id_path in self.id_path_to_node_uid:
                continue
            uid = ucl.get_uid_from_id_path(id_path)
            self.id_path_to_node_uid[id_path] = uid

    def power_off_unused(self) -> None:
        self.logging.debug("Powering off")
        # check locked devices from lockfiles
        locked_uids = lck.get_locked_uids()
        unused_uids = self.node_uids - set(locked_uids)

        for id_path, usb_info in self.powered_locations.items():
            uid = ucl.get_uid_from_id_path(id_path)
            if uid is None:
                continue
            if uid in unused_uids:
                self._power_off(id_path)
        self.wait_for_power_off()

    def wait_for_power_off(self):
        for proc in self._power_off_procs:
            proc.wait()
        if self._power_off_procs:
            sleep(self.DEFAULT_POWER_OFF_WAIT)
        self._power_off_procs = []
        self.logging.debug("Finished powering off")

    def wait_for_power_on(self, wait_time=None):
        for proc in self._power_on_procs:
            proc.wait()
        if self._power_on_procs:
            sleep(wait_time or self.DEFAULT_POWER_ON_WAIT)
        self._power_on_procs = []
        self._map_id_path_to_node_uid()
        self.logging.debug("Finished powering on")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback) -> None:
        """Release the lock when exiting the context."""
        self.wait_for_power_on(wait_time=0)
        self.power_off_unused()
        self.wait_for_power_off()
