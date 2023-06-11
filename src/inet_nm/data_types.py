"""This module contains the data types used by the inet-nm module."""
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class DictSerializable:
    """Mixin class to provide to_dict and from_dict methods."""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the instance to a dictionary.

        Returns:
            Dictionary representation of the instance.
        """
        return self.__dict__

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DictSerializable":
        """
        Create an instance from a dictionary.

        Args:
            data: Dictionary with data to populate the instance.

        Returns:
            An instance of the class that inherits this mixin.
        """
        return cls(**data)


@dataclass
class NmNode(DictSerializable):
    """
    A representation of an embedded dev board connected via USB.

    Attributes:
        serial: Serial number of the device.
        vendor_id: Vendor ID of the device.
        product_id: Product ID of the device.
        vendor: Name of the vendor.
        driver: Name of the driver.
        model: Model name of the device.
        uid: Unique ID of the device
        board: Name of the board.
        features_provided: List of features provided by the device.
        mock: Whether the node is a mock node.
        ignore: Whether the node should be ignored.
    """

    serial: str
    vendor_id: str
    product_id: str
    vendor: str
    driver: str
    model: Optional[str] = None
    uid: Optional[str] = None
    board: Optional[str] = None
    features_provided: Optional[List[str]] = None
    mock: bool = False
    ignore: bool = False

    def __post_init__(self):
        """Initialize additional attributes after instantiation."""
        self.features_provided = self.features_provided or []
        self.uid = self.uid or NmNode.calculate_uid(
            self.product_id, self.vendor_id, self.serial
        )

    @staticmethod
    def calculate_uid(product_id: str, vendor_id: str, serial: str) -> str:
        """
        Calculate a unique ID for a device.

        Args:
            product_id: Product ID of the device.
            vendor_id: Vendor ID of the device.
            serial: Serial number of the device.

        Returns:
            Calculated unique ID.
        """
        unique_key = f"{product_id}-{vendor_id}-{serial}"
        return hashlib.md5(unique_key.encode()).hexdigest()


@dataclass
class NodeEnv(DictSerializable):
    """
    Environment variables for a node.

    Attributes:
        NM_IDX: Index of the node.
        NM_UID: Unique ID of the node.
        NM_SERIAL: Serial number of the node.
        NM_BOARD: Board of the node.
        NM_PORT: Port of the node.
    """

    NM_IDX: int
    NM_UID: str
    NM_SERIAL: str
    NM_BOARD: str
    NM_PORT: str

    def to_dict(self) -> Dict[str, str]:
        """
        Convert the instance to a dictionary.

        Returns:
            Dict: Dictionary representation of the instance.

        """
        return {k: str(v) for k, v in self.__dict__.items()}
