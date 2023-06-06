from inet_nm.data_types import NmNode, NodeEnv


def test_nm_node():
    """Test the calculate_uid for the NmNode class."""
    uid1 = NmNode.calculate_uid("123", "456", "789")
    uid2 = NmNode.calculate_uid("321", "654", "987")
    assert uid1 == "856f4f9c3c084d978ec7ea0ad7d4cadf"
    assert uid2 == "410ddb1b4c8f37759162c9849b85c9de"
    assert uid1 != uid2

    # Test NmNode.to_dict and NmNode.from_dict
    data = {
        "serial": "serial",
        "vendor_id": "vendor_id",
        "product_id": "product_id",
        "vendor": "vendor",
        "model": "model",
        "driver": "driver",
    }
    node = NmNode.from_dict(data)

    # Test a subset of items to allow for additional attributes in the future
    for key in data:
        assert node.to_dict()[key] == data[key]


def test_node_env():
    """Test the NodeEnv data type."""
    env = NodeEnv(
        NM_IDX=1, NM_UID="uid", NM_SERIAL="serial", NM_BOARD="board", NM_PORT="port"
    )
    assert env.to_dict() == {
        "NM_IDX": "1",
        "NM_UID": "uid",
        "NM_SERIAL": "serial",
        "NM_BOARD": "board",
        "NM_PORT": "port",
    }
